using System.Collections.Generic;
using System.Drawing;
using System.IO;
using SottrModManager.Shared.Cdc;
using SottrModManager.Shared.Util;

namespace SottrModManager.Mod
{
    internal class FolderModPackage : ModPackage
    {
        private const string VariationDescriptionFileName = "variation.txt";
        private const string VariationImageFileName = "variation.png";

        private readonly string _folderPath;
        private readonly Dictionary<ResourceKey, string> _resources = new();

        public FolderModPackage(string folderPath)
            : this(Path.GetFileName(folderPath), folderPath)
        {
        }

        public FolderModPackage(string name, string folderPath)
        {
            Name = name;
            _folderPath = folderPath;
            ScanFolder(_folderPath);
        }

        public override string Name
        {
            get;
        }

        public override IEnumerable<ResourceKey> Resources
        {
            get
            {
                return _resources.Keys;
            }
        }

        public override Stream OpenResource(ResourceKey resourceKey)
        {
            string filePath = _resources.GetOrDefault(resourceKey);
            return filePath != null ? File.OpenRead(filePath) : null;
        }

        private void ScanFolder(string folderPath)
        {
            AddResourcesFromFolder(_resources, folderPath, false);

            foreach (string subFolderPath in Directory.EnumerateDirectories(folderPath))
            {
                if (File.Exists(Path.Combine(subFolderPath, VariationDescriptionFileName)) ||
                    File.Exists(Path.Combine(subFolderPath, VariationImageFileName)))
                {
                    Variations.Add(new FolderModVariation(subFolderPath));
                }
                else
                {
                    ScanFolder(subFolderPath);
                }
            }
        }

        private static void AddResourcesFromFolder(Dictionary<ResourceKey, string> resources, string folderPath, bool recursive)
        {
            foreach (string filePath in Directory.EnumerateFiles(folderPath, "*", recursive ? SearchOption.AllDirectories : SearchOption.TopDirectoryOnly))
            {
                (ResourceType type, ResourceSubType subType) = ResourceNaming.GetType(filePath);
                if (type != ResourceType.Unknown && int.TryParse(Path.GetFileNameWithoutExtension(filePath), out int id))
                    resources[new ResourceKey(type, subType, id)] = filePath;
            }
        }

        private class FolderModVariation : ModVariation
        {
            private readonly Dictionary<ResourceKey, string> _resources;

            public FolderModVariation(string folderPath)
                : base(Path.GetFileName(folderPath), GetDescription(folderPath), GetImage(folderPath))
            {
                FolderPath = folderPath;

                _resources = new();
                AddResourcesFromFolder(_resources, FolderPath, true);
            }

            public string FolderPath
            {
                get;
            }

            public override IEnumerable<ResourceKey> Resources => _resources.Keys;

            private static string GetDescription(string folderPath)
            {
                string filePath = Path.Combine(folderPath, VariationDescriptionFileName);
                return File.Exists(filePath) ? File.ReadAllText(filePath) : null;
            }

            private static Image GetImage(string folderPath)
            {
                string filePath = Path.Combine(folderPath, VariationImageFileName);
                return File.Exists(filePath) ? Image.FromFile(filePath) : null;
            }

            public override Stream OpenResource(ResourceKey resourceKey)
            {
                string filePath = _resources.GetOrDefault(resourceKey);
                return filePath != null ? File.OpenRead(filePath) : null;
            }
        }
    }
}
