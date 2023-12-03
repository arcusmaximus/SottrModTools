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
        private const int Version = 3;

        private readonly ResourceUsageCache _baseCache;
        private readonly Dictionary<ResourceKey, Dictionary<ArchiveFileKey, int>> _usages = new();

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
            Dictionary<ArchiveFileKey, int> usages = _usages.GetOrAdd(resourceRef, () => new());

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

        public IEnumerable<ResourceCollectionItemReference> GetUsages(ArchiveSet archiveSet, ResourceKey resourceKey)
        {
            IEnumerable<ResourceCollectionItemReference> baseUsages = _baseCache?.GetUsages(archiveSet, resourceKey);
            Dictionary<ArchiveFileKey, int> usages = _usages.GetOrDefault(resourceKey);

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
                Dictionary<ArchiveFileKey, int> usages = new(numUsages);
                for (int j = 0; j < numUsages; j++)
                {
                    ulong collectionNameHash = reader.ReadUInt64();
                    ulong collectionLocale = reader.ReadByte() == 0 ? 0xFFFFFFFFFFFFFFFF : reader.ReadUInt64();
                    int resourceIdx = reader.ReadInt32();
                    usages.Add(new ArchiveFileKey(collectionNameHash, collectionLocale), resourceIdx);
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
            foreach ((ResourceKey resource, Dictionary<ArchiveFileKey, int> usages) in _usages)
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
