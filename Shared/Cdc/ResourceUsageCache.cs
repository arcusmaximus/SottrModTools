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
        private record struct ResourceUsage(ulong CollectionNameHash, ulong CollectionLocale, int ResourceIndex);

        private const string FileName = "resourceusage.bin";
        private const int Version = 3;

        private readonly ResourceUsageCache _baseCache;
        private readonly Dictionary<ResourceKey, List<ResourceUsage>> _usages = new();

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
                AddFiles(archiveSet.Files, archiveSet.GetResourceCollection, progress, cancellationToken);
            }
            finally
            {
                progress?.End();
            }
        }

        public void AddArchive(Archive archive)
        {
            AddFiles(archive.Files, archive.GetResourceCollection, null, CancellationToken.None);
        }

        private void AddFiles(IEnumerable<ArchiveFileReference> files, Func<ArchiveFileReference, ResourceCollection> getResourceCollection, ITaskProgress progress, CancellationToken cancellationToken)
        {
            List<ArchiveFileReference> collectionRefs = files.Where(f => CdcHash.Lookup(f.NameHash) != null).ToList();
            int collectionIdx = 0;
            foreach (ArchiveFileReference collectionRef in collectionRefs)
            {
                cancellationToken.ThrowIfCancellationRequested();

                ResourceCollection collection = getResourceCollection(collectionRef);
                if (collection != null)
                    AddResourceCollection(collection);

                collectionIdx++;
                progress?.Report((float)collectionIdx / collectionRefs.Count);
            }
        }

        public void AddResourceCollection(ResourceCollection collection)
        {
            for (int resourceIdx = 0; resourceIdx < collection.ResourceReferences.Count; resourceIdx++)
            {
                AddResourceReference(collection, resourceIdx);
            }
        }

        public void AddResourceReference(ResourceCollection collection, int resourceIdx)
        {
            ResourceReference resourceRef = collection.ResourceReferences[resourceIdx];
            List<ResourceUsage> usages = _usages.GetOrAdd(resourceRef, () => new());

            if (collection.Locale == 0xFFFFFFFFFFFFFFFF)
                usages.RemoveAll(u => u.CollectionNameHash == collection.NameHash);
            else
                usages.RemoveAll(u => u.CollectionNameHash == collection.NameHash && u.CollectionLocale == collection.Locale);

            usages.Add(new ResourceUsage(collection.NameHash, collection.Locale, resourceIdx));
        }

        public IEnumerable<ResourceCollectionItemReference> GetUsages(ArchiveSet archiveSet, ResourceKey resourceKey)
        {
            IEnumerable<ResourceCollectionItemReference> baseUsages = _baseCache?.GetUsages(archiveSet, resourceKey) ?? Array.Empty<ResourceCollectionItemReference>();
            IList<ResourceUsage> usages = (IList<ResourceUsage>)_usages.GetOrDefault(resourceKey) ?? Array.Empty<ResourceUsage>();

            foreach (ResourceCollectionItemReference baseUsage in baseUsages)
            {
                if (!usages.Any(u => u.CollectionNameHash == baseUsage.CollectionReference.NameHash && (u.CollectionLocale == baseUsage.CollectionReference.Locale || u.CollectionLocale == 0xFFFFFFFFFFFFFFFF)))
                    yield return baseUsage;
            }
            
            foreach (ResourceUsage usage in usages)
            {
                yield return new ResourceCollectionItemReference(archiveSet.GetFileReference(usage.CollectionNameHash, usage.CollectionLocale), usage.ResourceIndex);
            }
        }

        public ResourceReference GetResourceReference(ArchiveSet archiveSet, ResourceKey resourceKey)
        {
            ResourceCollectionItemReference collectionItem = GetUsages(archiveSet, resourceKey).FirstOrDefault();
            if (collectionItem == null)
                return null;

            ResourceCollection collection = archiveSet.GetResourceCollection(collectionItem.CollectionReference);
            return collection?.ResourceReferences[collectionItem.ResourceIndex];
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

            int numResources = reader.ReadInt32();
            for (int i = 0; i < numResources; i++)
            {
                ResourceType type = (ResourceType)reader.ReadByte();
                int id = reader.ReadInt32();
                int numUsages = reader.ReadInt32();
                List<ResourceUsage> usages = new List<ResourceUsage>(numUsages);
                for (int j = 0; j < numUsages; j++)
                {
                    ulong collectionNameHash = reader.ReadUInt64();
                    ulong collectionLocale = reader.ReadByte() == 0 ? 0xFFFFFFFFFFFFFFFF : reader.ReadUInt64();
                    int resourceIdx = reader.ReadInt32();
                    usages.Add(new ResourceUsage(collectionNameHash, collectionLocale, resourceIdx));
                }
                _usages.Add(new ResourceKey(type, id), usages);
            }
            return true;
        }

        public void Save(string archiveFolderPath)
        {
            using Stream stream = File.Create(Path.Combine(archiveFolderPath, FileName));
            BinaryWriter writer = new BinaryWriter(stream);

            writer.Write(Version);
            writer.Write(GetArchiveDateHash(archiveFolderPath));

            writer.Write(_usages.Count);
            foreach ((ResourceKey resource, List<ResourceUsage> usages) in _usages)
            {
                writer.Write((byte)resource.Type);
                writer.Write(resource.Id);
                writer.Write(usages.Count);
                foreach (ResourceUsage usage in usages)
                {
                    writer.Write(usage.CollectionNameHash);
                    if (usage.CollectionLocale == 0xFFFFFFFFFFFFFFFF)
                    {
                        writer.Write((byte)0);
                    }
                    else
                    {
                        writer.Write((byte)1);
                        writer.Write(usage.CollectionLocale);
                    }
                    writer.Write(usage.ResourceIndex);
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
