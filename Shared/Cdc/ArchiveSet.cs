using System;
using System.Collections.Generic;
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

            Dictionary<int, ArchiveMetaData> metaDatas = new();
            foreach (string nfoFilePath in Directory.EnumerateFiles(folderPath))
            {
                if (!nfoFilePath.EndsWith(".nfo") && !nfoFilePath.EndsWith(".nfo.disabled"))
                    continue;

                if (Path.GetFileName(nfoFilePath).StartsWith(ModArchivePrefix) ? !includeMods : !includeGame)
                    continue;

                ArchiveMetaData metaData = ArchiveMetaData.Load(nfoFilePath);
                metaDatas[metaData.DlcIndex] = metaData;
            }

            foreach (string archiveFilePath in Directory.EnumerateFiles(folderPath, "*.tiger"))
            {
                using Stream stream = File.OpenRead(archiveFilePath);
                using BinaryReader reader = new BinaryReader(stream);
                var header = reader.ReadStruct<Archive.ArchiveHeader>();
                ArchiveMetaData metaData = metaDatas.GetOrDefault(header.Id);
                if (metaData != null)
                    Load(archiveFilePath, metaData);
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

        private void Load(string archiveFilePath, ArchiveMetaData metaData)
        {
            Archive archive = Archive.Open(archiveFilePath, metaData);
            var archiveKey = (archive.Id, archive.SubId);
            if (!_archives.ContainsKey(archiveKey))
                _archives.Add(archiveKey, archive);
            else
                _duplicateArchives.Add(archive);
        }

        public Dictionary<ulong, Archive> CreateModArchives(string modName, Dictionary<ulong, int> maxFilesByLocale)
        {
            lock (_lock)
            {
                string simplifiedName = Regex.Replace(modName, @"[^-.\w]", "_").ToLower();
                simplifiedName = Regex.Replace(simplifiedName, @"__+", "_").Trim('_');

                int gameId = _archives.Values.First().MetaData.GameId;
                int version = _archives.Values.Max(a => a.MetaData.Version) + 1;
                int id = _archives.Values.Max(a => a.Id) + 1;
                string steamId = _archives.Values.First().MetaData.CustomEntries.FirstOrDefault(c => c.StartsWith("steamID:"));

                string nfoFilePath = Path.Combine(FolderPath, $"{ModArchivePrefix}{simplifiedName}.000.000.nfo");
                ArchiveMetaData metaData = ArchiveMetaData.Create(nfoFilePath, gameId, version, id, id);
                if (steamId != null)
                    metaData.CustomEntries.Add(steamId);

                metaData.CustomEntries.Add("mod:" + modName);
                metaData.Save();

                int subId = 0;

                Dictionary<ulong, Archive> archives = new();
                SpecMasksToc toc = new SpecMasksToc();
                foreach ((ulong locale, int maxFiles) in maxFilesByLocale.OrderByDescending(p => p.Key))
                {
                    string archiveFileName = $"{ModArchivePrefix}{simplifiedName}.000{MakeLocaleSuffix(locale)}.000.tiger";
                    toc.Entries.Add(locale, archiveFileName);
                    archives.Add(locale, Archive.Create(Path.Combine(FolderPath, archiveFileName), metaData, subId, maxFiles));
                    subId++;
                }

                if (toc.Entries.Count > 1)
                    toc.Write(SpecMasksToc.GetFilePathForArchive(Path.ChangeExtension(nfoFilePath, ".tiger")));

                return archives;
            }
        }

        private static string MakeLocaleSuffix(ulong locale)
        {
            if (locale == 0xFFFFFFFFFFFFFFFF)
                return "";

            int textFlags = (int)(locale & 0xFFFFFFF);
            string textLanguage;
            if (textFlags == 0xFFFFFFF)
                textLanguage = "alltxt";
            else
                textLanguage = Enum.GetValues(typeof(LocaleLanguage)).Cast<LocaleLanguage>().First(l => (textFlags & (int)l) != 0).ToString().ToLower();

            int voiceFlags = (int)((locale >> 28) & 0xFFFFFFF);
            string voiceLanguage;
            if (voiceFlags == 0xFFFFFFF)
                voiceLanguage = "allvo";
            else
                voiceLanguage = Enum.GetValues(typeof(LocaleLanguage)).Cast<LocaleLanguage>().First(l => (voiceFlags & (int)l) != 0).ToString().ToLower();

            int platformFlags = (int)(locale >> 56);
            string platform = platformFlags switch
            {
                0xFF => "allplt",
                0x20 => "neutral",
                _ => platformFlags.ToString("X02")
            };

            return $"_{textLanguage}_{voiceLanguage}_{platform}";
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

        public void Enable(int archiveId, ResourceUsageCache gameResourceUsageCache, ITaskProgress progress, CancellationToken cancellationToken)
        {
            lock (_lock)
            {
                Archive archive = _archives[(archiveId, 0)];
                if (archive.MetaData.Enabled)
                    return;

                try
                {
                    progress.Begin($"Enabling mod {archive.ModName}...");

                    archive.MetaData.Enabled = true;

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

        public void Disable(int archiveId, ResourceUsageCache gameResourceUsageCache, ITaskProgress progress, CancellationToken cancellationToken)
        {
            lock (_lock)
            {
                Archive archive = _archives[(archiveId, 0)];
                Disable(archiveId, gameResourceUsageCache, progress, $"Disabling mod {archive.ModName}...", cancellationToken);
            }
        }

        private void Disable(int archiveId, ResourceUsageCache gameResourceUsageCache, ITaskProgress progress, string statusText, CancellationToken cancellationToken)
        {
            Archive archive = _archives[(archiveId, 0)];
            if (!archive.MetaData.Enabled)
                return;

            try
            {
                progress.Begin(statusText);

                List<Archive> sortedArchives = GetSortedArchives();
                int index = sortedArchives.IndexOf(archive);
                archive.MetaData.Enabled = false;
                if (index >= 0)
                {
                    while (index < sortedArchives.Count && sortedArchives[index].Id == archiveId)
                    {
                        sortedArchives.RemoveAt(index);
                    }
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

        public void Delete(int archiveId, ResourceUsageCache gameResourceUsageCache, ITaskProgress progress, CancellationToken cancellationToken)
        {
            lock (_lock)
            {
                Disable(archiveId, gameResourceUsageCache, progress, $"Removing mod {_archives[(archiveId, 0)].ModName}...", cancellationToken);

                foreach (Archive archive in _archives.Values.Where(a => a.Id == archiveId).Concat(_duplicateArchives.Where(a => a.Id == archiveId)).ToList())
                {
                    archive.Delete();
                    archive.Dispose();
                    if (!_duplicateArchives.Remove(archive))
                        _archives.Remove((archive.Id, archive.SubId));
                }
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
            List<Archive> sortedArchives = _archives.Values.Where(a => a.MetaData.Enabled).ToList();
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
