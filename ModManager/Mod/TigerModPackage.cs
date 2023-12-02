using System.Collections.Generic;
using System.IO;
using SottrModManager.Shared.Cdc;

namespace SottrModManager.Mod
{
    internal class TigerModPackage : ModPackage
    {
        private readonly Archive _archive;
        private readonly Dictionary<ResourceKey, ResourceReference> _resources = new();

        public TigerModPackage(string filePath)
        {
            _archive = Archive.Open(filePath);
            Name = _archive.ModName;

            foreach (ArchiveFileReference fileRef in _archive.Files)
            {
                ResourceCollection collection = _archive.GetResourceCollection(fileRef);
                if (collection == null)
                    continue;

                foreach (ResourceReference resourceRef in collection.ResourceReferences)
                {
                    if (resourceRef.ArchiveId == _archive.Id)
                        _resources[new ResourceKey(resourceRef.Type, resourceRef.SubType, resourceRef.Id)] = resourceRef;
                }
            }
        }

        public override string Name
        {
            get;
        }

        public override IEnumerable<ResourceKey> Resources => _resources.Keys;

        public override Stream OpenResource(ResourceKey resourceKey)
        {
            return _archive.OpenResource(_resources[resourceKey]);
        }

        public override string ToString()
        {
            return Name;
        }

        public override void Dispose()
        {
            base.Dispose();
            _archive.Dispose();
        }
    }
}
