using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using SottrModManager.Shared.Cdc;
using SottrModManager.Shared.Util;

namespace SottrModManager.Mod
{
    internal class FolderModPackage : ModPackage
    {
        private const string VariationDescriptionFileName = "variation.txt";
        private const string VariationImageFileName = "variation.png";

        private readonly string _folderPath;
        private readonly ArchiveSet _archiveSet;
        private readonly ResourceUsageCache _resourceUsageCache;
        private readonly Dictionary<ArchiveFileKey, string> _files = new();
        private readonly Dictionary<ResourceKey, string> _physicalResources = new();
        private readonly Dictionary<ResourceKey, MemoryStream> _virtualResources = new();

        public FolderModPackage(string folderPath, ArchiveSet archiveSet, ResourceUsageCache resourceUsageCache)
            : this(Path.GetFileName(folderPath), folderPath, archiveSet, resourceUsageCache)
        {
        }

        public FolderModPackage(string name, string folderPath, ArchiveSet archiveSet, ResourceUsageCache resourceUsageCache)
        {
            Name = name;
            _folderPath = folderPath;
            _archiveSet = archiveSet;
            _resourceUsageCache = resourceUsageCache;
            ScanFolder(_folderPath, _folderPath);
            AddVirtualResources(_virtualResources, _physicalResources, _files, _archiveSet, _resourceUsageCache);
        }

        public override string Name
        {
            get;
        }

        public override IEnumerable<ArchiveFileKey> Files => _files.Keys;

        public override Stream OpenFile(ArchiveFileKey fileKey)
        {
            return OpenFile(_files, fileKey, _archiveSet);
        }

        public override IEnumerable<ResourceKey> Resources => _physicalResources.Keys.Concat(_virtualResources.Keys);

        public override Stream OpenResource(ResourceKey resourceKey)
        {
            return OpenResource(_physicalResources, _virtualResources, resourceKey, _archiveSet, _resourceUsageCache);
        }

        private void ScanFolder(string baseFolderPath, string folderPath)
        {
            AddFilesAndResourcesFromFolder(baseFolderPath, folderPath, _files, _physicalResources, false);

            foreach (string subFolderPath in Directory.EnumerateDirectories(folderPath))
            {
                if (File.Exists(Path.Combine(subFolderPath, VariationDescriptionFileName)) ||
                    File.Exists(Path.Combine(subFolderPath, VariationImageFileName)))
                {
                    Variations.Add(new FolderModVariation(subFolderPath, _archiveSet, _resourceUsageCache));
                }
                else
                {
                    ScanFolder(baseFolderPath, subFolderPath);
                }
            }
        }

        private static void AddFilesAndResourcesFromFolder(string baseFolderPath, string folderPath, Dictionary<ArchiveFileKey, string> files, Dictionary<ResourceKey, string> resources, bool recursive)
        {
            if (!baseFolderPath.EndsWith("\\"))
                baseFolderPath += "\\";

            foreach (string filePath in Directory.EnumerateFiles(folderPath, "*", recursive ? SearchOption.AllDirectories : SearchOption.TopDirectoryOnly))
            {
                (ResourceType type, ResourceSubType subType) = ResourceNaming.GetType(filePath);
                if (type != ResourceType.Unknown && int.TryParse(Path.GetFileNameWithoutExtension(filePath), out int id))
                {
                    resources[new ResourceKey(type, subType, id)] = filePath;
                    continue;
                }

                string filePathToHash = filePath.Substring(baseFolderPath.Length);
                ulong locale = 0xFFFFFFFFFFFFFFFF;
                if (Enum.TryParse(Path.GetFileNameWithoutExtension(filePath), true, out LocaleLanguage localeLang) && Enum.IsDefined(typeof(LocaleLanguage), localeLang))
                {
                    filePathToHash = Path.GetDirectoryName(filePathToHash);
                    locale = 0xFFFFFFFFFFFF0400 | (ulong)localeLang;
                }

                string extension = Path.GetExtension(filePath);
                if (extension != ".txt" && extension != ".png")
                    files[new ArchiveFileKey(CdcHash.Calculate(filePathToHash), locale)] = filePath;
            }
        }

        private static void AddVirtualResources(
            Dictionary<ResourceKey, MemoryStream> virtualResources,
            Dictionary<ResourceKey, string> physicalResources,
            Dictionary<ArchiveFileKey, string> files,
            ArchiveSet archiveSet,
            ResourceUsageCache resourceUsageCache)
        {
            Dictionary<ResourceKey, WwiseSoundBank> virtualSoundBanks = new();
            foreach (string wemFilePath in files.Values.Where(p => Path.GetExtension(p) == ".wem"))
            {
                if (!int.TryParse(Path.GetFileNameWithoutExtension(wemFilePath), out int soundId))
                    continue;

                foreach (WwiseSoundBankItemReference soundUsage in resourceUsageCache.GetSoundUsages(soundId))
                {
                    ResourceKey bankResourceKey = new ResourceKey(ResourceType.SoundBank, soundUsage.BankResourceId);
                    if (physicalResources.ContainsKey(bankResourceKey))
                        continue;

                    WwiseSoundBank bank = virtualSoundBanks.GetOrDefault(bankResourceKey);
                    if (bank == null)
                    {
                        ResourceReference bankResourceRef = resourceUsageCache.GetResourceReference(archiveSet, bankResourceKey);
                        if (bankResourceRef == null)
                            continue;

                        using (Stream stream = archiveSet.OpenResource(bankResourceRef))
                        {
                            bank = new WwiseSoundBank(stream);
                        }
                        virtualSoundBanks.Add(bankResourceKey, bank);
                    }

                    var indexSection = bank.GetSection<WwiseSoundBank.DataIndexSection>();
                    if (indexSection == null)
                        continue;

                    var indexEntry = indexSection.Entries[soundUsage.Index];
                    indexEntry.Length = 0;
                    indexSection.Entries[soundUsage.Index] = indexEntry;
                }
            }

            foreach ((ResourceKey bankResourceKey, WwiseSoundBank bank) in virtualSoundBanks)
            {
                MemoryStream stream = new MemoryStream();
                bank.Write(stream);
                stream.Position = 0;
                virtualResources.Add(bankResourceKey, stream);
            }
        }

        private static Stream OpenFile(Dictionary<ArchiveFileKey, string> files, ArchiveFileKey fileKey, ArchiveSet archiveSet)
        {
            string filePath = files.GetOrDefault(fileKey);
            if (filePath == null)
                return null;

            Stream stream = File.OpenRead(filePath);
            if (filePath.EndsWith(".json") && Path.GetFileName(Path.GetDirectoryName(filePath)) == "locals.bin")
            {
                Stream localsStream;
                try
                {
                    localsStream = GetPatchedLocalsBin(stream, fileKey, archiveSet);
                }
                finally
                {
                    stream.Close();
                }
                stream = localsStream;
            }
            return stream;
        }

        private static Stream GetPatchedLocalsBin(Stream jsonStream, ArchiveFileKey fileKey, ArchiveSet archiveSet)
        {
            ArchiveFileReference fileRef = archiveSet.GetFileReference(fileKey);
            if (fileRef == null)
                throw new Exception($"File {fileKey} not found for locals.bin");

            LocalsBin locals;
            using (Stream origStream = archiveSet.OpenFile(fileRef))
            {
                locals = new LocalsBin(origStream);
            }

            JObject json;
            try
            {
                using StreamReader streamReader = new StreamReader(jsonStream);
                using JsonReader jsonReader = new JsonTextReader(streamReader);
                json = JObject.Load(jsonReader);
            }
            catch (Exception ex)
            {
                throw new Exception("Failed to parse JSON file for locals.bin:\r\n" + ex.Message);
            }

            foreach ((string key, JToken value) in json)
            {
                locals.Strings[key] = (string)value;
            }

            MemoryStream patchedStream = new MemoryStream();
            locals.Write(patchedStream);
            patchedStream.Position = 0;
            return patchedStream;
        }

        private static Stream OpenResource(
            Dictionary<ResourceKey, string> physicalResources,
            Dictionary<ResourceKey, MemoryStream> virtualResources,
            ResourceKey resourceKey,
            ArchiveSet archiveSet,
            ResourceUsageCache resourceUsageCache)
        {
            Stream virtualStream = virtualResources.GetOrDefault(resourceKey);
            if (virtualStream != null)
                return virtualStream;

            string filePath = physicalResources.GetOrDefault(resourceKey);
            if (filePath == null)
                return null;

            Stream stream = File.OpenRead(filePath);
            switch (resourceKey.Type)
            {
                case ResourceType.Texture:
                    Stream textureStream = ConvertTexture(stream, resourceKey, archiveSet, resourceUsageCache);
                    stream.Close();
                    return textureStream;

                case ResourceType.SoundBank:
                    Stream dtpStream = ConvertSoundBank(stream);
                    stream.Close();
                    return dtpStream;

                default:
                    return stream;
            }
        }

        private static Stream ConvertTexture(Stream ddsStream, ResourceKey resourceKey, ArchiveSet archiveSet, ResourceUsageCache resourceUsageCache)
        {
            CdcTexture texture = CdcTexture.ReadFromDds(ddsStream);

            uint originalFormat = GetOriginalTextureFormat(resourceKey, archiveSet, resourceUsageCache);
            if (CdcTexture.IsSrgbFormat(originalFormat))
                texture.Header.Format = CdcTexture.MapRegularFormatToSrgb(texture.Header.Format);

            Stream textureStream = new MemoryStream();
            texture.Write(textureStream);
            textureStream.Position = 0;
            return textureStream;
        }

        private static Stream ConvertSoundBank(Stream bnkStream)
        {
            MemoryStream dtpStream = new MemoryStream(8 + (int)bnkStream.Length);
            
            BinaryWriter writer = new BinaryWriter(dtpStream);
            writer.Write(0);
            writer.Write((int)bnkStream.Length);
            bnkStream.CopyTo(dtpStream);

            BinaryReader reader = new BinaryReader(dtpStream);
            dtpStream.Position = 0x14;
            uint soundBankId = reader.ReadUInt32();
            dtpStream.Position = 0;
            writer.Write(soundBankId);

            dtpStream.Position = 0;
            return dtpStream;
        }

        private static uint GetOriginalTextureFormat(ResourceKey resourceKey, ArchiveSet archiveSet, ResourceUsageCache resourceUsageCache)
        {
            ResourceReference resourceRef = resourceUsageCache.GetResourceReference(archiveSet, resourceKey);
            if (resourceRef == null)
                return 0;

            using Stream origTextureStream = archiveSet.OpenResource(resourceRef);
            BinaryReader reader = new BinaryReader(origTextureStream);
            CdcTexture.CdcTextureHeader header = reader.ReadStruct<CdcTexture.CdcTextureHeader>();
            return header.Format;
        }

        private class FolderModVariation : ModVariation
        {
            private readonly ArchiveSet _archiveSet;
            private readonly ResourceUsageCache _resourceUsageCache;
            private readonly Dictionary<ArchiveFileKey, string> _files = new();
            private readonly Dictionary<ResourceKey, string> _physicalResources = new();
            private readonly Dictionary<ResourceKey, MemoryStream> _virtualResources = new();

            public FolderModVariation(string folderPath, ArchiveSet archiveSet, ResourceUsageCache resourceUsageCache)
                : base(Path.GetFileName(folderPath), GetDescription(folderPath), GetImage(folderPath))
            {
                FolderPath = folderPath;
                _archiveSet = archiveSet;
                _resourceUsageCache = resourceUsageCache;
                AddFilesAndResourcesFromFolder(FolderPath, FolderPath, _files, _physicalResources, true);
                AddVirtualResources(_virtualResources, _physicalResources, _files, _archiveSet, _resourceUsageCache);
            }

            public string FolderPath
            {
                get;
            }

            private static string GetDescription(string folderPath)
            {
                string filePath = Path.Combine(folderPath, VariationDescriptionFileName);
                return File.Exists(filePath) ? File.ReadAllText(filePath) : null;
            }

            private static Image GetImage(string folderPath)
            {
                string filePath = Path.Combine(folderPath, VariationImageFileName);
                if (!File.Exists(filePath))
                    return null;

                using Image image = Image.FromFile(filePath);
                return new Bitmap(image);
            }

            public override IEnumerable<ArchiveFileKey> Files => _files.Keys;

            public override Stream OpenFile(ArchiveFileKey fileKey)
            {
                return FolderModPackage.OpenFile(_files, fileKey, _archiveSet);
            }

            public override IEnumerable<ResourceKey> Resources => _physicalResources.Keys.Concat(_virtualResources.Keys);

            public override Stream OpenResource(ResourceKey resourceKey)
            {
                return FolderModPackage.OpenResource(_physicalResources, _virtualResources, resourceKey, _archiveSet, _resourceUsageCache);
            }
        }
    }
}
