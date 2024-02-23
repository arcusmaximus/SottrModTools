using SottrModManager.Shared.Cdc;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;

namespace SottrModManager.Mod
{
    internal abstract class ModVariation : IDisposable
    {
        public ModVariation(string name, string description, Image image)
        {
            Name = name;
            Description = description;
            Image = image;
        }

        public string Name
        {
            get;
        }

        public string Description
        {
            get;
        }

        public Image Image
        {
            get;
        }

        public abstract IEnumerable<ArchiveFileKey> Files
        {
            get;
        }

        public abstract Stream OpenFile(ArchiveFileKey key);

        public abstract IEnumerable<ResourceKey> Resources
        {
            get;
        }

        public abstract Stream OpenResource(ResourceKey resourceKey);

        public override string ToString()
        {
            return Name;
        }

        public virtual void Dispose()
        {
            Image?.Dispose();
        }
    }
}
