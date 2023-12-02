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

        public abstract IEnumerable<ResourceKey> Resources
        {
            get;
        }

        public abstract Stream OpenResource(ResourceKey key);

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
