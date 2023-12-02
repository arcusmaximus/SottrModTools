using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading;
using System.Windows.Forms;
using SottrModManager.Shared;
using SottrModManager.Shared.Cdc;
using SottrModManager.Shared.Util;
using SottrModManager.Util;

namespace SottrModManager.Mod
{
    internal class ModInstaller
    {
        private record struct ResourceCollectionItem(ResourceCollection Collection, int ResourceIndex);

        private readonly ArchiveSet _archiveSet;
        private readonly ResourceUsageCache _gameResourceUsageCache;

        public ModInstaller(ArchiveSet archiveSet, ResourceUsageCache gameResourceUsageCache)
        {
            _archiveSet = archiveSet;
            _gameResourceUsageCache = gameResourceUsageCache;
        }

        public InstalledMod InstallFromZip(string filePath, ITaskProgress progress, CancellationToken cancellationToken)
        {
            string modName = Regex.Replace(Path.GetFileNameWithoutExtension(filePath), @"-\d+$", "");
            if (IsModAlreadyInstalled(modName))
                return null;

            using ZipTempExtractor extractor = new ZipTempExtractor(filePath);
            extractor.Extract(progress, cancellationToken);

            return Install(new FolderModPackage(modName, extractor.FolderPath), progress, cancellationToken);
        }

        public InstalledMod InstallFromFolder(string folderPath, ITaskProgress progress, CancellationToken cancellationToken)
        {
            string modName = Path.GetFileName(folderPath);
            Archive existingArchive = _archiveSet.Archives.FirstOrDefault(a => a.ModName == modName);
            if (existingArchive != null)
                _archiveSet.Delete(existingArchive, _gameResourceUsageCache, progress, cancellationToken);

            return Install(new FolderModPackage(folderPath), progress, cancellationToken);
        }

        public void ReinstallAll(ITaskProgress progress, CancellationToken cancellationToken)
        {
            List<ArchiveInfo> originalArchives = new List<ArchiveInfo>();
            foreach (Archive archive in _archiveSet.Archives
                                                   .Concat(_archiveSet.DuplicateArchives)
                                                   .Where(a => a.ModName != null)
                                                   .OrderByDescending(a => a.MetaData.Version))
            {
                archive.CloseStreams();
                ArchiveInfo archiveInfo = new ArchiveInfo
                {
                    NfoFilePath = Path.Combine(_archiveSet.FolderPath, "_orig_" + Path.GetFileName(archive.NfoFilePath)),
                    BaseFilePath = Path.Combine(_archiveSet.FolderPath, "_orig_" + Path.GetFileName(archive.BaseFilePath)),
                    ModName = archive.ModName,
                    Enabled = archive.Enabled
                };

                File.Delete(archiveInfo.NfoFilePath);
                File.Move(archive.NfoFilePath, archiveInfo.NfoFilePath);

                File.Delete(archiveInfo.BaseFilePath);
                File.Move(archive.BaseFilePath, archiveInfo.BaseFilePath);

                _archiveSet.Delete(archive, _gameResourceUsageCache, progress, cancellationToken);
                originalArchives.Insert(0, archiveInfo);
            }

            foreach (ArchiveInfo archiveInfo in originalArchives)
            {
                using (ModPackage modPackage = new TigerModPackage(archiveInfo.BaseFilePath))
                {
                    InstalledMod installedMod = Install(modPackage, null, progress, cancellationToken);
                    if (installedMod == null)
                        continue;

                    if (!archiveInfo.Enabled)
                    {
                        Archive archive = _archiveSet.GetArchive(installedMod.ArchiveId, 0);
                        _archiveSet.Disable(archive, _gameResourceUsageCache, progress, cancellationToken);
                    }
                }

                File.Delete(archiveInfo.NfoFilePath);
                File.Delete(archiveInfo.BaseFilePath);
            }
        }

        private struct ArchiveInfo
        {
            public string NfoFilePath;
            public string BaseFilePath;
            public string ModName;
            public bool Enabled;
        }

        private bool IsModAlreadyInstalled(string modName)
        {
            if (_archiveSet.Archives.Any(a => a.ModName == modName))
            {
                MessageBox.Show($"The mod {modName} is already installed.", "", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return true;
            }
            return false;
        }

        private InstalledMod Install(ModPackage modPackage, ITaskProgress progress, CancellationToken cancellationToken)
        {
            ModVariation modVariation = null;
            if (modPackage.Variations != null && modPackage.Variations.Count > 0)
            {
                using VariationSelectionForm form = new VariationSelectionForm(modPackage);
                if (form.ShowDialog() != DialogResult.OK)
                    return null;

                modVariation = form.SelectedVariation;
            }
            return Install(modPackage, modVariation, progress, cancellationToken);
        }

        private InstalledMod Install(ModPackage modPackage, ModVariation modVariation, ITaskProgress progress, CancellationToken cancellationToken)
        {
            ResourceUsageCache fullResourceUsageCache = new ResourceUsageCache(_gameResourceUsageCache);
            using (ArchiveSet modArchiveSet = new ArchiveSet(_archiveSet.FolderPath, false, true))
            {
                fullResourceUsageCache.AddArchiveSet(modArchiveSet, null, CancellationToken.None);
            }

            Archive archive = null;
            try
            {
                progress.Begin($"Installing mod {modPackage.Name}...");

                IEnumerable<ResourceKey> modResources = modPackage.Resources;
                if (modVariation != null)
                    modResources = modResources.Concat(modVariation.Resources);

                Dictionary<ResourceKey, List<ResourceCollectionItemReference>> modResourceUsages =
                    modResources.ToDictionary(r => r, r => fullResourceUsageCache.GetUsages(_archiveSet, r).ToList());

                Dictionary<ulong, ResourceCollection> modResourceCollections = modResourceUsages.Values
                                                                                                .SelectMany(c => c)
                                                                                                .Select(c => c.CollectionReference)
                                                                                                .Distinct()
                                                                                                .ToDictionary(r => r.NameHash, _archiveSet.GetResourceCollection);

                Dictionary<ResourceKey, List<ResourceCollectionItem>> modResourceCollectionItems =
                    modResourceUsages.ToDictionary(
                        p => p.Key,
                        p => p.Value
                              .Select(r => new ResourceCollectionItem(modResourceCollections[r.CollectionReference.NameHash], r.ResourceIndex))
                              .ToList()
                );

                Dictionary<ulong, HashSet<ResourceKey>> resourceRefsToAdd = GetResourceRefsToAdd(modPackage, modVariation, modResourceCollections, modResources);
                AddResourceReferencesToCollections(modResourceCollections, modResourceCollectionItems, resourceRefsToAdd);
                
                archive = _archiveSet.CreateModArchive(modPackage.Name, 1 + modResourceCollections.Count);
                AddResourcesToArchive(archive, modPackage, modVariation, modResourceCollectionItems, progress, cancellationToken);
                AddResourceCollectionsToArchive(archive, modResourceCollections.Values);

                _archiveSet.Add(archive, _gameResourceUsageCache, progress, cancellationToken);
                return new InstalledMod(archive.Id, modPackage.Name, true);
            }
            catch
            {
                if (archive != null)
                {
                    archive.CloseStreams();
                    File.Delete(Path.ChangeExtension(archive.BaseFilePath, ".nfo"));
                    File.Delete(archive.BaseFilePath);
                }
                throw;
            }
            finally
            {
                _archiveSet.CloseStreams();
                progress.End();
            }
        }

        private Dictionary<ulong, HashSet<ResourceKey>> GetResourceRefsToAdd(
            ModPackage modPackage,
            ModVariation modVariation,
            Dictionary<ulong, ResourceCollection> modResourceCollections,
            IEnumerable<ResourceKey> modResources)
        {
            Dictionary<ulong, HashSet<ResourceKey>> resourcesToAdd = new();

            foreach (ResourceKey modelResource in modResources.Where(r => r.Type == ResourceType.Model && r.SubType == ResourceSubType.Model))
            {
                List<ResourceKey> materialResources;
                using (Stream modResourceStream = modVariation?.OpenResource(modelResource) ?? modPackage.OpenResource(modelResource))
                {
                    materialResources = new ResourceRefDefinitions(modResourceStream).ExternalRefs
                                                                                     .Select(r => r.ResourceKey)
                                                                                     .Where(r => r.Type == ResourceType.Material)
                                                                                     .ToList();
                }

                foreach (ResourceCollectionItemReference modelUsage in _gameResourceUsageCache.GetUsages(_archiveSet, modelResource))
                {
                    ResourceCollection collection = modResourceCollections[modelUsage.CollectionReference.NameHash];
                    foreach (ResourceKey materialResource in materialResources)
                    {
                        if (collection.ResourceReferences.Any(r => ((ResourceKey)r).Equals(materialResource)))
                            continue;

                        resourcesToAdd.GetOrAdd(collection.NameHash, () => new HashSet<ResourceKey>())
                                      .UnionWith(GetResourceKeysRecursive(materialResource));
                    }
                }
            }

            return resourcesToAdd;
        }

        private IEnumerable<ResourceKey> GetResourceKeysRecursive(ResourceKey rootResourceKey)
        {
            Queue<ResourceKey> resourceKeyQueue = new();
            resourceKeyQueue.Enqueue(rootResourceKey);

            while (resourceKeyQueue.Count > 0)
            {
                ResourceKey resourceKey = resourceKeyQueue.Dequeue();
                yield return resourceKey;

                ResourceReference resourceRef = _gameResourceUsageCache.GetResourceReference(_archiveSet, resourceKey);
                if (resourceRef == null || resourceRef.RefDefinitionsSize == 0)
                    continue;

                using Stream resourceStream = _archiveSet.OpenResource(resourceRef);
                ResourceRefDefinitions refDefinitions = new ResourceRefDefinitions(resourceStream);
                foreach (ResourceRefDefinitions.ExternalRef externalRef in refDefinitions.ExternalRefs)
                {
                    resourceKeyQueue.Enqueue(externalRef.ResourceKey);
                }
            }
        }

        private void AddResourceReferencesToCollections(
            Dictionary<ulong, ResourceCollection> modResourceCollections,
            Dictionary<ResourceKey, List<ResourceCollectionItem>> modResourceCollectionItems,
            Dictionary<ulong, HashSet<ResourceKey>> resourceRefsToAdd)
        {
            foreach ((ulong collectionNameHash, ICollection<ResourceKey> resourcesForCollection) in resourceRefsToAdd)
            {
                ResourceCollection modCollection = modResourceCollections.GetOrDefault(collectionNameHash);
                if (modCollection == null)
                    continue;

                foreach (ResourceKey resource in resourcesForCollection)
                {
                    if (modCollection.ResourceReferences.Any(r => r.Type == resource.Type && r.Id == resource.Id))
                        continue;

                    ResourceCollectionItemReference existingUsage = _gameResourceUsageCache.GetUsages(_archiveSet, resource).FirstOrDefault();
                    if (existingUsage == null)
                        continue;

                    ResourceCollection sourceCollection = _archiveSet.GetResourceCollection(existingUsage.CollectionReference);
                    if (sourceCollection == null)
                        continue;

                    int modCollectionResourceIdx = modCollection.AddResourceReference(sourceCollection, existingUsage.ResourceIndex);
                    modResourceCollectionItems.GetOrAdd(resource, () => new()).Add(new ResourceCollectionItem(modCollection, modCollectionResourceIdx));
                }
            }
        }

        private void AddResourcesToArchive(
            Archive archive,
            ModPackage modPackage,
            ModVariation modVariation,
            Dictionary<ResourceKey, List<ResourceCollectionItem>> modResourceCollectionItems,
            ITaskProgress progress,
            CancellationToken cancellationToken)
        {
            int resourceIdx = 0;
            int offsetInBatch = 0;
            foreach ((ResourceKey modResourceKey, List<ResourceCollectionItem> collectionItems) in modResourceCollectionItems)
            {
                cancellationToken.ThrowIfCancellationRequested();

                Stream modResourceStream = modVariation?.OpenResource(modResourceKey) ?? modPackage.OpenResource(modResourceKey);
                if (modResourceStream != null)
                {
                    try
                    {
                        int? refDefinitionsSize = null;

                        if (modResourceKey.Type == ResourceType.Texture && !(modPackage is TigerModPackage))
                            ConvertTexture(ref modResourceStream, collectionItems);
                        else if (modResourceKey.Type == ResourceType.Model && modResourceKey.SubType == ResourceSubType.Model)
                            refDefinitionsSize = GetResourceRefDefinitionsSize(modPackage, modResourceKey);

                        ArchiveBlobReference newResource = archive.AddResource(modResourceStream);
                        foreach (ResourceCollectionItem collectionItem in collectionItems)
                        {
                            collectionItem.Collection.UpdateResourceReference(
                                collectionItem.ResourceIndex,
                                new ResourceReference(
                                    modResourceKey.Id,
                                    modResourceKey.Type,
                                    modResourceKey.SubType,
                                    newResource.ArchiveId,
                                    newResource.ArchiveSubId,
                                    newResource.ArchivePart,
                                    newResource.Offset,
                                    newResource.Length,
                                    offsetInBatch,
                                    refDefinitionsSize,
                                    (int)modResourceStream.Length - (refDefinitionsSize ?? 0)
                                )
                            );
                        }

                        offsetInBatch += (int)modResourceStream.Length;
                        offsetInBatch = (offsetInBatch + 0xF) & ~0xF;
                    }
                    finally
                    {
                        modResourceStream.Close();
                    }
                }

                resourceIdx++;
                progress.Report((float)resourceIdx / modResourceCollectionItems.Count);
            }
        }

        private void ConvertTexture(ref Stream modResourceStream, List<ResourceCollectionItem> collectionItems)
        {
            Stream textureStream = new MemoryStream();
            CdcTexture texture = CdcTexture.ReadFromDds(modResourceStream);

            uint originalFormat = GetOriginalTextureFormat(collectionItems);
            if (CdcTexture.IsSrgbFormat(originalFormat))
                texture.Header.Format = CdcTexture.MapRegularFormatToSrgb(texture.Header.Format);

            texture.Write(textureStream);
            textureStream.Position = 0;

            modResourceStream.Close();
            modResourceStream = textureStream;
        }

        private uint GetOriginalTextureFormat(List<ResourceCollectionItem> collectionItems)
        {
            if (collectionItems.Count == 0)
                return 0;

            Stream origTextureStream = _archiveSet.OpenResource(collectionItems[0].Collection.ResourceReferences[collectionItems[0].ResourceIndex]);
            BinaryReader reader = new BinaryReader(origTextureStream);
            CdcTexture.CdcTextureHeader header = reader.ReadStruct<CdcTexture.CdcTextureHeader>();
            return header.Format;
        }
        
        private static int GetResourceRefDefinitionsSize(ModPackage modPackage, ResourceKey resourceKey)
        {
            using Stream stream = modPackage.OpenResource(resourceKey);
            return ResourceRefDefinitions.ReadHeaderAndGetSize(stream);
        }

        private void AddResourceCollectionsToArchive(Archive archive, IEnumerable<ResourceCollection> resourceCollections)
        {
            foreach (ResourceCollection resourceCollection in resourceCollections.OrderBy(r => r.NameHash))
            {
                MemoryStream collectionStream = new MemoryStream();
                resourceCollection.Write(collectionStream);
                collectionStream.TryGetBuffer(out ArraySegment<byte> collectionData);
                archive.AddFile(resourceCollection.NameHash, 0xFFFFFFFFFFFFFFFF, collectionData);
            }
        }
    }
}
