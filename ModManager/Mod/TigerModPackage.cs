using System.Collections.Generic;
using System.IO;
using System.Linq;
using SottrModManager.Shared.Cdc;
using SottrModManager.Shared.Util;

namespace SottrModManager.Mod
{
    internal class TigerModPackage : ModPackage
    {
        private readonly Dictionary<int, Archive> _archivesBySubId;
        private readonly Dictionary<ArchiveFileKey, ArchiveFileReference> _files = new();
        private readonly Dictionary<ResourceKey, ResourceReference> _resources = new();

        public TigerModPackage(string nfoFilePath, List<string> archiveFilePaths)
        {
            ArchiveMetaData metaData = ArchiveMetaData.Load(nfoFilePath);
            _archivesBySubId = archiveFilePaths.Select(p => Archive.Open(p, metaData))
                                               .ToDictionary(a => a.SubId);
            Name = _archivesBySubId.Values.First().ModName;

            foreach (Archive archive in _archivesBySubId.Values)
            {
                foreach (ArchiveFileReference fileRef in archive.Files)
                {
                    ResourceCollection collection = archive.GetResourceCollection(fileRef);
                    if (collection == null)
                    {
                        _files[fileRef] = fileRef;
                        continue;
                    }

                    foreach (ResourceReference resourceRef in collection.ResourceReferences)
                    {
                        if (resourceRef.ArchiveId == archive.Id)
                            _resources[resourceRef] = resourceRef;
                    }
                }
            }
        }

        public override string Name
        {
            get;
        }

        public override ICollection<ArchiveFileKey> Files => _files.Keys;

        public override Stream OpenFile(ArchiveFileKey fileKey)
        {
            ArchiveFileReference fileRef = _files.GetOrDefault(fileKey);
            return fileRef != null ? _archivesBySubId[fileRef.ArchiveSubId].OpenFile(fileRef) : null;
        }

        public override ICollection<ResourceKey> Resources => _resources.Keys;

        public override Stream OpenResource(ResourceKey resourceKey)
        {
            ResourceReference resourceRef = _resources.GetOrDefault(resourceKey);
            return resourceRef != null ? _archivesBySubId[resourceRef.ArchiveSubId].OpenResource(_resources[resourceKey]) : null;
        }

        public override string ToString()
        {
            return Name;
        }

        public override void Dispose()
        {
            base.Dispose();
            foreach (Archive archive in _archivesBySubId.Values)
            {
                archive.Dispose();
            }
        }
    }
}
