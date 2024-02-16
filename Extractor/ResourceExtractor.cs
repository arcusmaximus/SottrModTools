using System.Collections.Generic;
using System.IO;
using System.Threading;
using SottrModManager.Shared;
using SottrModManager.Shared.Cdc;
using SottrModManager.Shared.Util;

namespace SottrExtractor
{
    internal class ResourceExtractor
    {
        private readonly ArchiveSet _archiveSet;

        public ResourceExtractor(ArchiveSet archiveSet)
        {
            _archiveSet = archiveSet;
        }

        public void Extract(string folderPath, ResourceCollection collection, ITaskProgress progress, CancellationToken cancellationToken)
        {
            try
            {
                progress.Begin("Extracting...");

                Directory.CreateDirectory(folderPath);

                GetResourceReferencesRecursive(collection, out Dictionary<string, ResourceReference> refResources, out HashSet<ResourceReference> otherResources);
                int numExtractedResources = 0;
                int numTotalResources = refResources.Count + otherResources.Count;

                foreach ((string collectionName, ResourceReference resourceRef) in refResources)
                {
                    string filePath = Path.Combine(folderPath, collectionName + ResourceNaming.GetExtension(resourceRef.Type, resourceRef.SubType));
                    ExtractResource(filePath, resourceRef, ref numExtractedResources, numTotalResources, progress, cancellationToken);
                }

                foreach (ResourceReference resourceRef in otherResources)
                {
                    string filePath = Path.Combine(folderPath, ResourceNaming.GetFilePath(resourceRef));
                    Directory.CreateDirectory(Path.GetDirectoryName(filePath));
                    ExtractResource(filePath, resourceRef, ref numExtractedResources, numTotalResources, progress, cancellationToken);
                }
            }
            finally
            {
                progress.End();
            }
        }

        private void ExtractResource(string filePath, ResourceReference resourceRef, ref int numExtractedResources, int numTotalResources, ITaskProgress progress, CancellationToken cancellationToken)
        {
            cancellationToken.ThrowIfCancellationRequested();

            using (Stream resourceStream = _archiveSet.OpenResource(resourceRef))
            using (Stream fileStream = File.Create(filePath))
            {
                if (resourceRef.Type == ResourceType.Texture)
                {
                    CdcTexture texture = CdcTexture.Read(resourceStream);
                    texture.WriteAsDds(fileStream);
                }
                else
                {
                    resourceStream.CopyTo(fileStream);
                }
            }

            numExtractedResources++;
            progress.Report((float)numExtractedResources / numTotalResources);
        }

        private void GetResourceReferencesRecursive(ResourceCollection collection, out Dictionary<string, ResourceReference> refResources, out HashSet<ResourceReference> otherResources)
        {
            refResources = new();
            otherResources = new();

            Queue<ResourceCollection> collections = new Queue<ResourceCollection>();
            collections.Enqueue(collection);
            while (collections.Count > 0)
            {
                collection = collections.Dequeue();
                string collectionName = Path.GetFileNameWithoutExtension(CdcHash.Lookup(collection.NameHash));

                foreach (ResourceReference resource in collection.ResourceReferences)
                {
                    if (resource.Type == ResourceType.ObjectReference || resource.Type == ResourceType.GlobalContentReference)
                        refResources[collectionName] = resource;
                    else
                        otherResources.Add(resource);
                }

                foreach (ResourceCollectionDependency dependency in collection.Dependencies)
                {
                    ResourceCollection dependencyCollection = _archiveSet.GetResourceCollection(dependency.FilePath, dependency.Locale);
                    if (dependencyCollection != null)
                        collections.Enqueue(dependencyCollection);
                }
            }
        }
    }
}
