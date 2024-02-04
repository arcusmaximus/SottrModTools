using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
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

            return Install(new FolderModPackage(modName, extractor.FolderPath, _archiveSet, _gameResourceUsageCache), progress, cancellationToken);
        }

        public InstalledMod InstallFromFolder(string folderPath, ITaskProgress progress, CancellationToken cancellationToken)
        {
            string modName = Path.GetFileName(folderPath);
            Archive existingArchive = _archiveSet.Archives.FirstOrDefault(a => a.ModName == modName);
            if (existingArchive != null)
                _archiveSet.Delete(existingArchive.Id, _gameResourceUsageCache, progress, cancellationToken);

            return Install(new FolderModPackage(folderPath, _archiveSet, _gameResourceUsageCache), progress, cancellationToken);
        }

        public void ReinstallAll(ITaskProgress progress, CancellationToken cancellationToken)
        {
            List<OriginalModInfo> originalMods = new();
            foreach (IGrouping<int, Archive> archivesOfId in _archiveSet.Archives
                                                                        .Concat(_archiveSet.DuplicateArchives)
                                                                        .Where(a => a.ModName != null)
                                                                        .GroupBy(a => a.Id)
                                                                        .OrderByDescending(g => g.First().MetaData.Version))
            {
                _archiveSet.CloseStreams();

                ArchiveMetaData metaData = archivesOfId.First().MetaData;
                OriginalModInfo originalModInfo = new OriginalModInfo
                {
                    ModName = archivesOfId.First().ModName,
                    Enabled = metaData.Enabled,
                    NfoFilePath = metaData.FilePath + ".orig",
                    ArchiveFilePaths = new List<string>()
                };

                _archiveSet.Disable(archivesOfId.Key, _gameResourceUsageCache, progress, cancellationToken);

                File.Delete(originalModInfo.NfoFilePath);
                File.Move(metaData.FilePath, originalModInfo.NfoFilePath);

                foreach (string archiveFilePath in archivesOfId.Select(a => a.BaseFilePath))
                {
                    string origFilePath = archiveFilePath + ".orig";
                    File.Delete(origFilePath);
                    File.Move(archiveFilePath, origFilePath);
                    originalModInfo.ArchiveFilePaths.Add(origFilePath);
                }

                _archiveSet.Delete(archivesOfId.Key, _gameResourceUsageCache, progress, cancellationToken);
                originalMods.Insert(0, originalModInfo);
            }

            foreach (OriginalModInfo originalMod in originalMods)
            {
                using (ModPackage modPackage = new TigerModPackage(originalMod.NfoFilePath, originalMod.ArchiveFilePaths))
                {
                    InstalledMod installedMod = Install(modPackage, null, progress, cancellationToken);
                    if (installedMod == null)
                        continue;

                    if (!originalMod.Enabled)
                        _archiveSet.Disable(installedMod.ArchiveId, _gameResourceUsageCache, progress, cancellationToken);
                }

                File.Delete(originalMod.NfoFilePath);
                foreach (string archiveFilePath in originalMod.ArchiveFilePaths)
                {
                    File.Delete(archiveFilePath);
                }
            }
        }

        private class OriginalModInfo
        {
            public string ModName;
            public bool Enabled;
            public string NfoFilePath;
            public List<string> ArchiveFilePaths;
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
            Dictionary<ulong, Archive> archives = null;
            try
            {
                progress.Begin($"Installing mod {modPackage.Name}...");

                _archiveSet.CloseStreams();
                ResourceUsageCache fullResourceUsageCache = new ResourceUsageCache(_gameResourceUsageCache);
                using (ArchiveSet modArchiveSet = new ArchiveSet(_archiveSet.FolderPath, false, true))
                {
                    fullResourceUsageCache.AddArchiveSet(modArchiveSet, null, CancellationToken.None);
                }

                List<ResourceKey> modResourceKeys = modPackage.Resources.ToList();
                if (modVariation != null)
                    modResourceKeys.AddRange(modVariation.Resources);

                Dictionary<ResourceKey, List<ResourceCollectionItemReference>> modResourceUsages =
                    modResourceKeys.ToDictionary(r => r, r => fullResourceUsageCache.GetUsages(_archiveSet, r).ToList());
                modResourceUsages.RemoveAll(p => p.Value.Count == 0);

                Dictionary<ArchiveFileKey, ResourceCollection> modResourceCollections = modResourceUsages.Values
                                                                                                         .SelectMany(c => c)
                                                                                                         .Select(c => c.CollectionReference)
                                                                                                         .Distinct()
                                                                                                         .ToDictionary(r => (ArchiveFileKey)r, _archiveSet.GetResourceCollection);

                Dictionary<ResourceKey, List<ResourceCollectionItem>> modResourceCollectionItems =
                    modResourceUsages.ToDictionary(
                        p => p.Key,
                        p => p.Value
                              .Select(r => new ResourceCollectionItem(modResourceCollections[r.CollectionReference], r.ResourceIndex))
                              .ToList()
                );

                Dictionary<ArchiveFileKey, HashSet<ResourceKey>> resourceRefsToAdd = GetResourceRefsToAdd(modPackage, modVariation, modResourceKeys, fullResourceUsageCache);
                AddResourceReferencesToCollections(modResourceCollections, modResourceCollectionItems, resourceRefsToAdd);

                IEnumerable<ArchiveFileKey> fileKeys = modResourceCollections.Keys.Concat(modPackage.Files).Concat(modVariation?.Files ?? Enumerable.Empty<ArchiveFileKey>());
                Dictionary<ulong, int> fileCountsByLocale = fileKeys.GroupBy(f => f.Locale).ToDictionary(g => g.Key, g => g.Count());
                fileCountsByLocale.TryAdd(0xFFFFFFFFFFFFFFFF, 0);

                archives = _archiveSet.CreateModArchives(modPackage.Name, fileCountsByLocale);
                AddResourcesToArchive(archives[0xFFFFFFFFFFFFFFFF], modPackage, modVariation, modResourceCollectionItems, progress, cancellationToken);
                AddFilesToArchives(archives, modPackage, modVariation, modResourceCollections.Values);

                foreach (Archive archive in archives.Values.OrderBy(a => a.SubId))
                {
                    _archiveSet.Add(archive, _gameResourceUsageCache, progress, cancellationToken);
                }
                return new InstalledMod(archives.Values.First().Id, modPackage.Name, true);
            }
            catch
            {
                if (archives != null)
                {
                    foreach (Archive archive in archives.Values)
                    {
                        archive.CloseStreams();
                        File.Delete(archive.MetaData.FilePath);
                        File.Delete(archive.BaseFilePath);
                    }
                }
                throw;
            }
            finally
            {
                _archiveSet.CloseStreams();
                progress.End();
            }
        }

        private Dictionary<ArchiveFileKey, HashSet<ResourceKey>> GetResourceRefsToAdd(
            ModPackage modPackage,
            ModVariation modVariation,
            List<ResourceKey> modResourceKeys,
            ResourceUsageCache fullResourceUsageCache)
        {
            Dictionary<ArchiveFileKey, HashSet<ResourceKey>> resourceRefsToAdd = new();
            foreach (ResourceKey modResourceKey in modResourceKeys)
            {
                HashSet<ResourceKey> externalResourceKeys = new();
                CollectExternalResourceKeys(modPackage, modVariation, modResourceKeys, modResourceKey, externalResourceKeys, fullResourceUsageCache);
                if (externalResourceKeys.Count == 0)
                    continue;

                foreach (ResourceCollectionItemReference modResourceUsage in fullResourceUsageCache.GetUsages(_archiveSet, modResourceKey))
                {
                    resourceRefsToAdd.GetOrAdd(modResourceUsage.CollectionReference, () => new()).UnionWith(externalResourceKeys);
                }
            }
            return resourceRefsToAdd;
        }

        private void CollectExternalResourceKeys(
            ModPackage modPackage,
            ModVariation modVariation,
            List<ResourceKey> modResourceKeys,
            ResourceKey resourceKey,
            HashSet<ResourceKey> allExternalResourceKeys,
            ResourceUsageCache fullResourceUsageCache)
        {
            if (!MightHaveRefDefinitions(resourceKey))
                return;

            ResourceReference resourceRef = fullResourceUsageCache.GetResourceReference(_archiveSet, resourceKey);
            if (resourceRef == null || resourceRef.RefDefinitionsSize == 0)
                return;

            List<ResourceKey> externalResourceKeys;
            Stream resourceStream = null;
            try
            {
                if (modResourceKeys.Contains(resourceKey))
                    resourceStream = modVariation?.OpenResource(resourceKey) ?? modPackage.OpenResource(resourceKey);
                else
                    resourceStream = _archiveSet.OpenResource(resourceRef);

                if (!resourceStream.CanSeek)
                {
                    MemoryStream memResourceStream = new MemoryStream();
                    resourceStream.CopyTo(memResourceStream);
                    resourceStream.Close();
                    memResourceStream.Position = 0;
                    resourceStream = memResourceStream;
                }

                externalResourceKeys = new ResourceRefDefinitions(resourceStream).ExternalRefs.Select(r => r.ResourceKey).ToList();
            }
            finally
            {
                resourceStream.Close();
            }

            foreach (ResourceKey externalResourceKey in externalResourceKeys)
            {
                if (resourceKey.SubType == ResourceSubType.Model && externalResourceKey.Type == ResourceType.Model)
                    continue;

                if (allExternalResourceKeys.Add(externalResourceKey))
                    CollectExternalResourceKeys(modPackage, modVariation, modResourceKeys, externalResourceKey, allExternalResourceKeys, fullResourceUsageCache);
            }
        }

        private void AddResourceReferencesToCollections(
            Dictionary<ArchiveFileKey, ResourceCollection> modResourceCollections,
            Dictionary<ResourceKey, List<ResourceCollectionItem>> modResourceCollectionItems,
            Dictionary<ArchiveFileKey, HashSet<ResourceKey>> resourceRefsToAdd)
        {
            foreach ((ArchiveFileKey collectionKey, ICollection<ResourceKey> resourcesForCollection) in resourceRefsToAdd)
            {
                ResourceCollection modCollection = modResourceCollections.GetOrDefault(collectionKey);
                if (modCollection == null)
                    continue;

                foreach (ResourceKey resource in resourcesForCollection)
                {
                    if (modCollection.ResourceReferences.Any(r => r.Type == resource.Type && r.Id == resource.Id))
                        continue;

                    int modCollectionResourceIdx = -1;
                    ResourceCollectionItemReference existingUsage = _gameResourceUsageCache.GetUsages(_archiveSet, resource).FirstOrDefault();
                    if (existingUsage != null)
                    {
                        ResourceCollection sourceCollection = _archiveSet.GetResourceCollection(existingUsage.CollectionReference);
                        if (sourceCollection != null)
                            modCollectionResourceIdx = modCollection.AddResourceReference(sourceCollection, existingUsage.ResourceIndex);
                    }
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

                resourceIdx++;
                progress.Report((float)resourceIdx / modResourceCollectionItems.Count);

                Stream modResourceStream = modVariation?.OpenResource(modResourceKey) ?? modPackage.OpenResource(modResourceKey);
                if (modResourceStream == null)
                    continue;

                try
                {
                    int? refDefinitionsSize = null;
                    if (MightHaveRefDefinitions(modResourceKey))
                    {
                        ResourceReference existingResourceRef = collectionItems[0].ResourceIndex >= 0 ? collectionItems[0].Collection.ResourceReferences[collectionItems[0].ResourceIndex] : null;
                        if (existingResourceRef == null || existingResourceRef.RefDefinitionsSize > 0)
                            refDefinitionsSize = GetResourceRefDefinitionsSize(modPackage, modResourceKey);
                    }

                    ArchiveBlobReference newResource = archive.AddResource(modResourceStream);
                    ResourceReference newResourceRef =
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
                        );
                    foreach (ResourceCollectionItem collectionItem in collectionItems)
                    {
                        if (collectionItem.ResourceIndex < 0)
                            collectionItem.Collection.AddResourceReference(newResourceRef);
                        else
                            collectionItem.Collection.UpdateResourceReference(collectionItem.ResourceIndex, newResourceRef);
                    }

                    offsetInBatch += (int)modResourceStream.Length;
                    offsetInBatch = (offsetInBatch + 0xF) & ~0xF;
                }
                finally
                {
                    modResourceStream.Close();
                }
            }
        }
        
        private static int GetResourceRefDefinitionsSize(ModPackage modPackage, ResourceKey resourceKey)
        {
            using Stream stream = modPackage.OpenResource(resourceKey);
            return ResourceRefDefinitions.ReadHeaderAndGetSize(stream);
        }

        private static void AddFilesToArchives(Dictionary<ulong, Archive> archives, ModPackage modPackage, ModVariation modVariation, IEnumerable<ResourceCollection> resourceCollections)
        {
            SortedDictionary<ArchiveFileKey, object> files = new();

            foreach (ArchiveFileKey fileKey in modPackage.Files)
            {
                files.Add(fileKey, modPackage);
            }

            if (modVariation != null)
            {
                foreach (ArchiveFileKey fileKey in modVariation.Files)
                {
                    files.Add(fileKey, modVariation);
                }
            }

            foreach (ResourceCollection resourceCollection in resourceCollections)
            {
                files.Add(new ArchiveFileKey(resourceCollection.NameHash, resourceCollection.Locale), resourceCollection);
            }

            foreach ((ArchiveFileKey fileKey, object value) in files)
            {
                switch (value)
                {
                    case ModPackage _:
                        AddFileToArchive(archives, fileKey, modPackage.OpenFile(fileKey));
                        break;

                    case ModVariation _:
                        AddFileToArchive(archives, fileKey, modVariation.OpenFile(fileKey));
                        break;

                    case ResourceCollection resourceCollection:
                        MemoryStream collectionStream = new MemoryStream();
                        resourceCollection.Write(collectionStream);
                        collectionStream.TryGetBuffer(out ArraySegment<byte> collectionData);
                        archives[resourceCollection.Locale].AddFile(resourceCollection.NameHash, resourceCollection.Locale, collectionData);
                        break;
                }
            }
        }

        private static void AddFileToArchive(Dictionary<ulong, Archive> archives, ArchiveFileKey fileKey, Stream stream)
        {
            if (stream == null)
                return;

            byte[] data = new byte[stream.Length];
            stream.Read(data);
            stream.Close();
            archives[fileKey.Locale].AddFile(fileKey, data);
        }

        private static bool MightHaveRefDefinitions(ResourceKey resourceKey)
        {
            if (resourceKey.Type == ResourceType.Texture || resourceKey.Type == ResourceType.ShaderLib || resourceKey.SubType == ResourceSubType.ModelData)
                return false;

            return true;
        }
    }
}
