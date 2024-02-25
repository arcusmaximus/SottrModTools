using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using SottrModManager.Shared.Util;

namespace SottrModManager.Shared.Cdc
{
    public class ResourceUsageCache
    {
        private const string FileName = "resourceusage.bin";
        private const int Version = 6;

        private readonly ResourceUsageCache _baseCache;
        private readonly Dictionary<ResourceKey, Dictionary<ArchiveFileKey, int>> _resourceUsages = new();
        private readonly Dictionary<int, HashSet<WwiseSoundBankItemReference>> _soundUsages = new();

        public ResourceUsageCache()
        {
        }

        public ResourceUsageCache(ResourceUsageCache baseCache)
        {
            _baseCache = baseCache;
        }

        public void AddArchiveSet(ArchiveSet archiveSet, ITaskProgress progress, CancellationToken cancellationToken)
        {
            try
            {
                progress?.Begin("Creating resource usage cache...");
                AddFiles(archiveSet.Files, archiveSet, progress, cancellationToken);
            }
            finally
            {
                progress?.End();
            }
        }

        public void AddArchives(IEnumerable<Archive> archives, ArchiveSet archiveSet)
        {
            foreach (Archive archive in archives)
            {
                AddArchive(archive, archiveSet);
            }
        }

        public void AddArchive(Archive archive, ArchiveSet archiveSet)
        {
            AddFiles(archive.Files, archiveSet, null, CancellationToken.None);
        }

        private void AddFiles(IEnumerable<ArchiveFileReference> files, ArchiveSet archiveSet, ITaskProgress progress, CancellationToken cancellationToken)
        {
            List<ArchiveFileReference> collectionRefs = files.Where(f => CdcHash.Lookup(f.NameHash) != null).ToList();
            int collectionIdx = 0;
            foreach (ArchiveFileReference collectionRef in collectionRefs)
            {
                cancellationToken.ThrowIfCancellationRequested();

                ResourceCollection collection = archiveSet.GetResourceCollection(collectionRef);
                if (collection != null)
                    AddResourceCollection(collection, archiveSet);

                collectionIdx++;
                progress?.Report((float)collectionIdx / collectionRefs.Count);
            }
        }

        public void AddResourceCollection(ResourceCollection collection, ArchiveSet archiveSet)
        {
            for (int i = 0; i < collection.ResourceReferences.Count; i++)
            {
                AddResourceReference(collection, i);

                ResourceReference resourceRef = collection.ResourceReferences[i];
                if (resourceRef.Type == ResourceType.SoundBank)
                    AddSoundBank(resourceRef, archiveSet);
            }
        }

        public void AddResourceReference(ResourceCollection collection, int resourceIdx)
        {
            ResourceReference resourceRef = collection.ResourceReferences[resourceIdx];
            Dictionary<ArchiveFileKey, int> usages = _resourceUsages.GetOrAdd(resourceRef, () => new());

            ArchiveFileKey collectionKey = new ArchiveFileKey(collection.NameHash, collection.Locale);
            if (collection.Locale == 0xFFFFFFFFFFFFFFFF && !usages.ContainsKey(collectionKey))
            {
                foreach (ArchiveFileKey localeSpecificCollectionKey in usages.Keys.Where(c => c.NameHash == collection.NameHash).ToList())
                {
                    usages.Remove(localeSpecificCollectionKey);
                }
            }

            usages[collectionKey] = resourceIdx;
        }

        private void AddSoundBank(ResourceReference resourceRef, ArchiveSet archiveSet)
        {
            WwiseSoundBank bank;
            using (Stream stream = archiveSet.OpenResource(resourceRef))
            {
                bank = new WwiseSoundBank(stream);
            }

            var dataIndexSection = bank.GetSection<WwiseSoundBank.DataIndexSection>();
            if (dataIndexSection != null)
            {
                for (int i = 0; i < dataIndexSection.Entries.Count; i++)
                {
                    _soundUsages.GetOrAdd(dataIndexSection.Entries[i].SoundId, () => new())
                                .Add(new WwiseSoundBankItemReference(resourceRef.Id, WwiseSoundBankItemReferenceType.DataIndex, i));
                }
            }

            var eventsSection = bank.GetSection<WwiseSoundBank.HircSection>();
            if (eventsSection != null)
            {
                for (int i = 0; i < eventsSection.Entries.Count; i++)
                {
                    if (eventsSection.Entries[i] is not WwiseSoundBank.HircSoundEntry soundEntry)
                        continue;
                    
                    _soundUsages.GetOrAdd(soundEntry.SoundId, () => new())
                                .Add(new WwiseSoundBankItemReference(resourceRef.Id, WwiseSoundBankItemReferenceType.Event, i));
                }
            }
        }

        public IEnumerable<ResourceCollectionItemReference> GetResourceUsages(ArchiveSet archiveSet, ResourceKey resourceKey)
        {
            IEnumerable<ResourceCollectionItemReference> baseUsages = _baseCache?.GetResourceUsages(archiveSet, resourceKey);
            Dictionary<ArchiveFileKey, int> usages = _resourceUsages.GetOrDefault(resourceKey);

            if (baseUsages != null)
            {
                foreach (ResourceCollectionItemReference baseUsage in baseUsages)
                {
                    if (usages != null)
                    {
                        if (usages.ContainsKey(new ArchiveFileKey(baseUsage.CollectionReference.NameHash, baseUsage.CollectionReference.Locale)))
                            continue;

                        if (baseUsage.CollectionReference.Locale != 0xFFFFFFFFFFFFFFFF &&
                            usages.ContainsKey(new ArchiveFileKey(baseUsage.CollectionReference.NameHash, 0xFFFFFFFFFFFFFFFF)))
                            continue;
                    }

                    yield return baseUsage;
                }
            }

            if (usages != null)
            {
                foreach ((ArchiveFileKey collectionKey, int resourceIdx) in usages)
                {
                    yield return new ResourceCollectionItemReference(archiveSet.GetFileReference(collectionKey.NameHash, collectionKey.Locale), resourceIdx);
                }
            }
        }

        public ResourceReference GetResourceReference(ArchiveSet archiveSet, ResourceKey resourceKey)
        {
            ResourceCollectionItemReference collectionItem = GetResourceUsages(archiveSet, resourceKey).FirstOrDefault();
            if (collectionItem == null)
                return null;

            ResourceCollection collection = archiveSet.GetResourceCollection(collectionItem.CollectionReference);
            return collection?.ResourceReferences[collectionItem.ResourceIndex];
        }

        public IEnumerable<WwiseSoundBankItemReference> GetSoundUsages(int soundId)
        {
            return _soundUsages.GetOrDefault(soundId) ?? Enumerable.Empty<WwiseSoundBankItemReference>();
        }

        public bool Load(string archiveFolderPath)
        {
            string filePath = Path.Combine(archiveFolderPath, FileName);
            if (!File.Exists(filePath))
                return false;

            using Stream stream = File.OpenRead(filePath);
            BinaryReader reader = new BinaryReader(stream);
            int version = reader.ReadInt32();
            if (version != Version)
                return false;

            int archiveDateHash = reader.ReadInt32();
            if (archiveDateHash != GetArchiveDateHash(archiveFolderPath))
                return false;

            ReadResourceUsages(reader);
            ReadSoundUsages(reader);
            return true;
        }

        private void ReadResourceUsages(BinaryReader reader)
        {
            int numResources = reader.ReadInt32();
            for (int i = 0; i < numResources; i++)
            {
                ResourceType type = (ResourceType)reader.ReadByte();
                int id = reader.ReadInt32();
                int numUsages = reader.ReadInt32();
                Dictionary<ArchiveFileKey, int> usages = new(numUsages);
                for (int j = 0; j < numUsages; j++)
                {
                    ulong collectionNameHash = reader.ReadUInt64();
                    ulong collectionLocale = reader.ReadByte() == 0 ? 0xFFFFFFFFFFFFFFFF : reader.ReadUInt64();
                    int resourceIdx = reader.ReadInt32();
                    usages.Add(new ArchiveFileKey(collectionNameHash, collectionLocale), resourceIdx);
                }
                _resourceUsages.Add(new ResourceKey(type, id), usages);
            }
        }

        private void ReadSoundUsages(BinaryReader reader)
        {
            int numSounds = reader.ReadInt32();
            for (int i = 0; i < numSounds; i++)
            {
                int id = reader.ReadInt32();
                int numUsages = reader.ReadInt32();
                HashSet<WwiseSoundBankItemReference> usages = new();
                for (int j = 0; j < numUsages; j++)
                {
                    int soundBankResourceId = reader.ReadInt32();
                    WwiseSoundBankItemReferenceType type = (WwiseSoundBankItemReferenceType)reader.ReadByte();
                    int index = reader.ReadInt32();
                    usages.Add(new WwiseSoundBankItemReference(soundBankResourceId, type, index));
                }
                _soundUsages.Add(id, usages);
            }
        }

        public void Save(string archiveFolderPath)
        {
            using Stream stream = File.Create(Path.Combine(archiveFolderPath, FileName));
            BinaryWriter writer = new BinaryWriter(stream);

            writer.Write(Version);
            writer.Write(GetArchiveDateHash(archiveFolderPath));

            WriteResourceUsages(writer);
            WriteSoundUsages(writer);
        }

        private void WriteResourceUsages(BinaryWriter writer)
        {
            writer.Write(_resourceUsages.Count);
            foreach ((ResourceKey resource, Dictionary<ArchiveFileKey, int> usages) in _resourceUsages)
            {
                writer.Write((byte)resource.Type);
                writer.Write(resource.Id);
                writer.Write(usages.Count);
                foreach ((ArchiveFileKey collectionKey, int resourceIdx) in usages)
                {
                    writer.Write(collectionKey.NameHash);
                    if (collectionKey.Locale == 0xFFFFFFFFFFFFFFFF)
                    {
                        writer.Write((byte)0);
                    }
                    else
                    {
                        writer.Write((byte)1);
                        writer.Write(collectionKey.Locale);
                    }
                    writer.Write(resourceIdx);
                }
            }
        }

        private void WriteSoundUsages(BinaryWriter writer)
        {
            writer.Write(_soundUsages.Count);
            foreach ((int soundId, HashSet<WwiseSoundBankItemReference> usages) in _soundUsages)
            {
                writer.Write(soundId);
                writer.Write(usages.Count);
                foreach (WwiseSoundBankItemReference usage in usages)
                {
                    writer.Write(usage.BankResourceId);
                    writer.Write((byte)usage.Type);
                    writer.Write(usage.Index);
                }
            }
        }

        private static int GetArchiveDateHash(string archiveFolderPath)
        {
            int hash = 0;
            unchecked
            {
                foreach (string archiveFilePath in Directory.EnumerateFiles(archiveFolderPath, "*.tiger"))
                {
                    if (!Path.GetFileName(archiveFilePath).StartsWith(ArchiveSet.ModArchivePrefix))
                        hash = hash * 397 ^ File.GetLastWriteTime(archiveFilePath).GetHashCode();
                }
            }
            return hash;
        }
    }
}
