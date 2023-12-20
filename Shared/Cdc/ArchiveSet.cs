using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading;
using SottrModManager.Shared.Util;

namespace SottrModManager.Shared.Cdc
{
    public class ArchiveSet : IDisposable
    {
        public const string ModArchivePrefix = "bigfile._mod.";

        private readonly object _lock = new();
        private readonly Dictionary<(int, int), Archive> _archives = new();
        private readonly List<Archive> _duplicateArchives = new List<Archive>();
        private readonly Dictionary<ArchiveFileKey, ArchiveFileReference> _files = new Dictionary<ArchiveFileKey, ArchiveFileReference>();

        public ArchiveSet(string folderPath, bool includeGame, bool includeMods)
        {
            FolderPath = folderPath;

            foreach (string nfoFilePath in Directory.EnumerateFiles(folderPath))
            {
                if (!nfoFilePath.EndsWith(".nfo") && !nfoFilePath.EndsWith(".nfo.disabled"))
                    continue;

                if (Path.GetFileName(nfoFilePath).StartsWith(ModArchivePrefix) ? !includeMods : !includeGame)
                    continue;

                string archiveFilePath = Regex.Replace(nfoFilePath, @"\.nfo(\.disabled)?$", ".tiger");
                Load(archiveFilePath);

                foreach (string localizationArchivePath in GetLocalizationArchivePaths(archiveFilePath))
                {
                    Load(localizationArchivePath);
                }
            }

            foreach (Archive archive in GetSortedArchives())
            {
                foreach (ArchiveFileReference file in archive.Files)
                {
                    _files[file] = file;
                }
            }
        }

        public string FolderPath
        {
            get;
        }

        public IReadOnlyCollection<Archive> Archives => _archives.Values;

        public IReadOnlyCollection<Archive> DuplicateArchives => _duplicateArchives;

        public Archive GetArchive(int id, int subId)
        {
            return _archives.GetOrDefault((id, subId));
        }

        public IReadOnlyCollection<ArchiveFileReference> Files => _files.Values;

        private void Load(string archiveFilePath)
        {
            if (!File.Exists(archiveFilePath))
                return;

            Archive archive = Archive.Open(archiveFilePath);
            var archiveKey = (archive.Id, archive.SubId);
            if (!_archives.ContainsKey(archiveKey))
                _archives.Add(archiveKey, archive);
            else
                _duplicateArchives.Add(archive);
        }

        public Archive CreateModArchive(string modName, int maxResourceCollections)
        {
            lock (_lock)
            {
                string simplifiedName = Regex.Replace(modName, @"[^-.\w]", "_").ToLower();
                simplifiedName = Regex.Replace(simplifiedName, @"__+", "_").Trim('_');

                int gameId = _archives.Values.First().MetaData.GameId;
                int version = _archives.Values.Max(a => a.MetaData.Version) + 1;
                int id = _archives.Values.Max(a => a.Id) + 1;

                string filePath = Path.Combine(FolderPath, $"{ModArchivePrefix}{simplifiedName}.000.000.tiger");
                Archive archive = Archive.Create(filePath, gameId, version, id, maxResourceCollections);

                string steamId = _archives.Values.First().MetaData.CustomEntries.FirstOrDefault(c => c.StartsWith("steamID:"));
                if (steamId != null)
                    archive.MetaData.CustomEntries.Add(steamId);

                archive.MetaData.CustomEntries.Add("mod:" + modName);
                archive.MetaData.Save();
                return archive;
            }
        }

        public void Add(Archive archive, ResourceUsageCache gameResourceUsageCache, ITaskProgress progress, CancellationToken cancellationToken)
        {
            lock (_lock)
            {
                _archives.Add((archive.Id, archive.SubId), archive);
                List<Archive> sortedArchives = GetSortedArchives();
                int index = sortedArchives.IndexOf(archive);
                if (index >= 0)
                    UpdateResourceReferences(sortedArchives, index + 1, gameResourceUsageCache, progress, cancellationToken);
            }
        }

        public void Enable(Archive archive, ResourceUsageCache gameResourceUsageCache, ITaskProgress progress, CancellationToken cancellationToken)
        {
            lock (_lock)
            {
                try
                {
                    progress.Begin($"Enabling mod {archive.ModName}...");

                    archive.Enabled = true;

                    List<Archive> sortedArchives = GetSortedArchives();
                    int index = sortedArchives.IndexOf(archive);
                    if (index >= 0)
                        UpdateResourceReferences(sortedArchives, index, gameResourceUsageCache, progress, cancellationToken);
                }
                finally
                {
                    progress.End();
                }
            }
        }

        public void Disable(Archive archive, ResourceUsageCache gameResourceUsageCache, ITaskProgress progress, CancellationToken cancellationToken)
        {
            lock (_lock)
            {
                Disable(archive, gameResourceUsageCache, progress, $"Disabling mod {archive.ModName}...", cancellationToken);
            }
        }

        private void Disable(Archive archive, ResourceUsageCache gameResourceUsageCache, ITaskProgress progress, string statusText, CancellationToken cancellationToken)
        {
            try
            {
                progress.Begin(statusText);

                List<Archive> sortedArchives = GetSortedArchives();
                int index = sortedArchives.IndexOf(archive);
                archive.Enabled = false;
                if (index >= 0)
                {
                    sortedArchives.RemoveAt(index);
                    UpdateResourceReferences(sortedArchives, index, gameResourceUsageCache, progress, cancellationToken);
                }
                else
                {
                    UpdateResourceReferences(sortedArchives, sortedArchives.Count, gameResourceUsageCache, progress, cancellationToken);
                }
            }
            finally
            {
                progress.End();
            }
        }

        public void Delete(Archive archive, ResourceUsageCache gameResourceUsageCache, ITaskProgress progress, CancellationToken cancellationToken)
        {
            lock (_lock)
            {
                Disable(archive, gameResourceUsageCache, progress, $"Removing mod {archive.ModName}...", cancellationToken);
                archive.Delete();
                archive.Dispose();
                if (!_duplicateArchives.Remove(archive))
                    _archives.Remove((archive.Id, archive.SubId));
            }
        }

        private void UpdateResourceReferences(List<Archive> sortedArchives, int startIndex, ResourceUsageCache gameResourceUsageCache, ITaskProgress progress, CancellationToken cancellationToken)
        {
            _files.Clear();
            ResourceUsageCache resourceUsageCache = new ResourceUsageCache(gameResourceUsageCache);
            foreach (Archive archive in sortedArchives.Take(startIndex))
            {
                foreach (ArchiveFileReference file in archive.Files)
                {
                    _files[file] = file;
                }
                if (archive.ModName != null && startIndex < sortedArchives.Count)
                    resourceUsageCache.AddArchive(archive);
            }

            int numTotalFiles = 0;
            foreach (Archive archive in sortedArchives.Skip(startIndex))
            {
                numTotalFiles += archive.Files.Count;
            }

            int numUpdatedFiles = 0;
            HashSet<int> archiveIds = sortedArchives.Select(a => a.Id).ToHashSet();
            Dictionary<ResourceKey, ResourceReference> modResourceRefs = new();
            foreach (Archive archive in sortedArchives.Skip(startIndex))
            {
                foreach (ArchiveFileReference file in archive.Files)
                {
                    cancellationToken.ThrowIfCancellationRequested();

                    numUpdatedFiles++;
                    progress.Report((float)numUpdatedFiles / numTotalFiles);

                    ResourceCollection collection = archive.GetResourceCollection(file);
                    if (collection == null)
                    {
                        _files[file] = file;
                        continue;
                    }

                    bool changesMade = false;
                    for (int resourceIdx = 0; resourceIdx < collection.ResourceReferences.Count; resourceIdx++)
                    {
                        ResourceReference resourceRef = collection.ResourceReferences[resourceIdx];
                        if (resourceRef.ArchiveId == archive.Id)
                        {
                            resourceUsageCache.AddResourceReference(collection, resourceIdx);
                            modResourceRefs[resourceRef] = resourceRef;
                        }
                        else if (modResourceRefs.TryGetValue(resourceRef, out ResourceReference modResourceRef))
                        {
                            collection.UpdateResourceReference(resourceIdx, modResourceRef);
                            changesMade = true;
                        }
                        else if (!archiveIds.Contains(resourceRef.ArchiveId))
                        {
                            collection.UpdateResourceReference(resourceIdx, resourceUsageCache.GetResourceReference(this, resourceRef));
                            changesMade = true;
                        }
                    }

                    if (changesMade)
                    {
                        using Stream collectionStream = archive.OpenFile(file);
                        collection.Write(collectionStream);
                    }

                    _files[file] = file;
                }
            }
        }

        public ArchiveFileReference GetFileReference(ArchiveFileKey fileId)
        {
            return GetFileReference(fileId.NameHash, fileId.Locale);
        }

        public ArchiveFileReference GetFileReference(ulong nameHash, ulong locale = 0xFFFFFFFFFFFFFFFF)
        {
            return _files.GetOrDefault(new ArchiveFileKey(nameHash, locale));
        }

        public ArchiveFileReference GetFileReference(string name, ulong locale = 0xFFFFFFFFFFFFFFFF)
        {
            return GetFileReference(CdcHash.Calculate(name), locale);
        }

        public ResourceCollection GetResourceCollection(ArchiveFileReference file)
        {
            return _archives[(file.ArchiveId, file.ArchiveSubId)].GetResourceCollection(file);
        }

        public ResourceCollection GetResourceCollection(ulong nameHash, ulong locale = 0xFFFFFFFFFFFFFFFF)
        {
            ArchiveFileReference fileRef = GetFileReference(nameHash, locale);
            return fileRef != null ? GetResourceCollection(fileRef) : null;
        }

        public ResourceCollection GetResourceCollection(string name, ulong locale = 0xFFFFFFFFFFFFFFFF)
        {
            ArchiveFileReference fileRef = GetFileReference(name, locale);
            return fileRef != null ? GetResourceCollection(fileRef) : null;
        }

        public Stream OpenFile(ArchiveFileReference fileRef)
        {
            return _archives[(fileRef.ArchiveId, fileRef.ArchiveSubId)].OpenFile(fileRef);
        }

        public Stream OpenResource(ResourceReference resourceRef)
        {
            return _archives[(resourceRef.ArchiveId, resourceRef.ArchiveSubId)].OpenResource(resourceRef);
        }

        public List<Archive> GetSortedArchives()
        {
            List<Archive> sortedArchives = _archives.Values.Where(a => a.Enabled).ToList();
            sortedArchives.Sort(CompareArchivePriority);
            return sortedArchives;
        }

        private static int CompareArchivePriority(Archive a, Archive b)
        {
            int comparison = a.MetaData.Version.CompareTo(b.MetaData.Version);
            if (comparison != 0)
                return comparison;

            comparison = b.MetaData.Required.CompareTo(a.MetaData.Required);
            if (comparison != 0)
                return comparison;

            comparison = a.MetaData.PackageId.CompareTo(b.MetaData.PackageId);
            if (comparison != 0)
                return comparison;

            comparison = a.MetaData.Chunk.CompareTo(b.MetaData.Chunk);
            if (comparison != 0)
                return comparison;

            return a.SubId.CompareTo(b.SubId);
        }

        private static IEnumerable<string> GetLocalizationArchivePaths(string baseArchiveFilePath)
        {
            string folderPath = Path.GetDirectoryName(baseArchiveFilePath);

            string specMasksName = Path.GetFileName(baseArchiveFilePath);
            if (specMasksName == "bigfile.000.tiger")
            {
                specMasksName = "game";
            }
            else
            {
                specMasksName = Regex.Replace(specMasksName, @"^bigfile\.", "");
                specMasksName = Regex.Replace(specMasksName, @"\.\d{3}\.\d{3}\.tiger$", "");
            }

            string specMasksFilePath = Path.Combine(folderPath, specMasksName + ".specmasks.toc");
            if (!File.Exists(specMasksFilePath))
                yield break;

            using StreamReader reader = new StreamReader(specMasksFilePath);
            reader.ReadLine();
            string line;
            while ((line = reader.ReadLine()) != null)
            {
                int spacePos = line.IndexOf(' ');
                if (spacePos < 0)
                    continue;

                ulong archiveLocale = ulong.Parse(line.Substring(0, spacePos), NumberStyles.AllowHexSpecifier);
                if (archiveLocale == 0xFFFFFFFFFFFFFFFF)
                    continue;

                string localizationArchiveFileName = line.Substring(spacePos + 1);
                if (!localizationArchiveFileName.EndsWith(".000.tiger"))
                    continue;

                yield return Path.Combine(folderPath, localizationArchiveFileName);
            }
        }

        public void CloseStreams()
        {
            foreach (Archive archive in _archives.Values.Concat(_duplicateArchives))
            {
                archive.CloseStreams();
            }
        }

        public void Dispose()
        {
            foreach (Archive archive in _archives.Values.Concat(_duplicateArchives))
            {
                archive.Dispose();
            }
            _archives.Clear();
            _duplicateArchives.Clear();
        }
    }
}
