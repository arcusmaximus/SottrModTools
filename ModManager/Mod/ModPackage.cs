using System;
using System.Collections.Generic;
using System.IO;
using SottrModManager.Shared.Cdc;

namespace SottrModManager.Mod
{
    internal abstract class ModPackage : IDisposable
    {
        public abstract string Name
        {
            get;
        }

        public abstract ICollection<ArchiveFileKey> Files
        {
            get;
        }

        public abstract Stream OpenFile(ArchiveFileKey fileKey);

        public abstract ICollection<ResourceKey> Resources
        {
            get;
        }

        public abstract Stream OpenResource(ResourceKey resourceKey);

        public List<ModVariation> Variations
        {
            get;
        } = new List<ModVariation>();

        public override string ToString()
        {
            return Name;
        }

        public virtual void Dispose()
        {
        }
    }
}
