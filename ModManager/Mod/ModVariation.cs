using SottrModManager.Shared.Cdc;
using System.Collections.Generic;
using System.Drawing;
using System.IO;

namespace SottrModManager.Mod
{
    internal abstract class ModVariation
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

        public abstract ICollection<ArchiveFileKey> Files
        {
            get;
        }

        public abstract Stream OpenFile(ArchiveFileKey key);

        public abstract ICollection<ResourceKey> Resources
        {
            get;
        }

        public abstract Stream OpenResource(ResourceKey resourceKey);

        public override string ToString()
        {
            return Name;
        }
    }
}
