using SottrModManager.Shared;
using SottrModManager.Shared.Cdc;
using SottrModManager.Shared.Controls.VirtualTreeView;
using SottrModManager.Shared.Util;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace SottrExtractor.LogHook
{
    internal partial class LogForm : FormWithProgress
    {
        private class FileLogEntry
        {
            public FileLogEntry(DateTime timestamp, ArchiveFileKey key, string path, string soundBank)
            {
                Timestamp = timestamp;
                Key = key;
                Path = path;
                SoundBank = soundBank;
            }

            public DateTime Timestamp { get; }
            public ArchiveFileKey Key { get; }
            public string Path { get; }
            public string SoundBank { get; }

            public override bool Equals(object other)
            {
                return Key == ((FileLogEntry)other).Key;
            }

            public override int GetHashCode()
            {
                return Key.GetHashCode();
            }
        }

        private class AnimationLogEntry
        {
            public AnimationLogEntry(DateTime timestamp, string drm, int id, string name)
            {
                Timestamp = timestamp;
                Drm = drm;
                Id = id;
                Name = name;
            }

            public DateTime Timestamp { get; }
            public string Drm { get; }
            public int Id { get; }
            public string Name { get; }

            public override bool Equals(object other)
            {
                return Id == ((AnimationLogEntry)other).Id;
            }

            public override int GetHashCode()
            {
                return Id;
            }
        }

        private readonly Game _game;
        private readonly ArchiveSet _archiveSet;
        private readonly ResourceUsageCache _resourceUsages;
        private bool _enableLogging = true;

        public LogForm()
        {
            InitializeComponent();
        }

        public LogForm(Game game, ArchiveSet archiveSet, ResourceUsageCache resourceUsages)
            : this()
        {
            _game = game;
            _archiveSet = archiveSet;
            _resourceUsages = resourceUsages;

            _game.Events.OpeningFile += HandleOpeningFile;
            _game.Events.PlayingAnimation += HandlePlayingAnimation;

            _tvFiles.Header.Columns.Add(new VirtualTreeColumn { Name = "Time", Width = 100 });
            _tvFiles.Header.Columns.Add(new VirtualTreeColumn { Name = "File", Width = 400 });
            _tvFiles.Header.Columns.Add(new VirtualTreeColumn { Name = "SoundBank", Width = 300 });

            _tvAnimations.Header.Columns.Add(new VirtualTreeColumn { Name = "Time", Width = 100 });
            _tvAnimations.Header.Columns.Add(new VirtualTreeColumn { Name = "DRM", Width = 300 });
            _tvAnimations.Header.Columns.Add(new VirtualTreeColumn { Name = "ID", Width = 100 });
            _tvAnimations.Header.Columns.Add(new VirtualTreeColumn { Name = "Name", Width = 300 });
        }

        private void HandleOpeningFile(ArchiveFileKey key, string path)
        {
            if (!_enableLogging)
                return;

            if (InvokeRequired)
            {
                BeginInvoke(() => HandleOpeningFile(key, path));
                return;
            }

            string soundBank = Path.GetExtension(path) == ".wem" ? GetSoundBank(path) : null;
            _tvFiles.AppendNode(new FileLogEntry(DateTime.Now, key, path, soundBank));
        }

        private string GetSoundBank(string soundFilePath)
        {
            if (!int.TryParse(Path.GetFileNameWithoutExtension(soundFilePath), out int soundId))
                return null;

            var soundUsages = _resourceUsages.GetSoundUsages(soundId);
            WwiseSoundBankItemReference soundUsage = soundUsages.FirstOrDefault(u => u.Type == WwiseSoundBankItemReferenceType.DataIndex) ?? soundUsages.FirstOrDefault();
            if (soundUsage == null)
                return null;

            ResourceCollectionItemReference bankUsage = _resourceUsages.GetResourceUsages(_archiveSet, new ResourceKey(ResourceType.SoundBank, soundUsage.BankResourceId)).FirstOrDefault();
            if (bankUsage == null)
                return null;

            string drmPath = CdcHash.Lookup(bankUsage.CollectionReference.NameHash);
            if (drmPath == null)
                return null;

            return Path.GetFileName(drmPath);
        }

        private void GetFileNodeCellText(VirtualTreeView tree, VirtualTreeNode node, int column, out string cellText)
        {
            FileLogEntry entry = tree.GetNodeData<FileLogEntry>(node);
            if (entry == null)
            {
                cellText = "";
                return;
            }

            cellText = column switch
            {
                0 => entry.Timestamp.ToShortTimeString(),
                1 => entry.Path,
                2 => entry.SoundBank,
                _ => ""
            };
        }

        private void HandlePlayingAnimation(int id, string name)
        {
            if (!_enableLogging)
                return;

            if (InvokeRequired)
            {
                BeginInvoke(() => HandlePlayingAnimation(id, name));
                return;
            }

            string drmName = null;
            ResourceCollectionItemReference usage = _resourceUsages.GetResourceUsages(_archiveSet, new ResourceKey(ResourceType.Animation, id)).FirstOrDefault();
            if (usage != null)
            {
                string drmPath = CdcHash.Lookup(usage.CollectionReference.NameHash);
                if (drmPath != null)
                    drmName = Path.GetFileName(drmPath);
            }
            _tvAnimations.AppendNode(new AnimationLogEntry(DateTime.Now, drmName, id, name));
        }

        private void GetAnimationNodeCellText(VirtualTreeView tree, VirtualTreeNode node, int column, out string cellText)
        {
            AnimationLogEntry entry = tree.GetNodeData<AnimationLogEntry>(node);
            if (entry == null)
            {
                cellText = "";
                return;
            }

            cellText = column switch
            {
                0 => entry.Timestamp.ToShortTimeString(),
                1 => entry.Drm,
                2 => entry.Id.ToString(),
                3 => entry.Name,
                _ => ""
            };
        }

        private void _btnEnableLogging_Click(object sender, EventArgs e)
        {
            _enableLogging = _btnEnableLogging.Checked;
        }

        private void _btnClearLists_Click(object sender, EventArgs e)
        {
            _tvFiles.Clear();
            _tvAnimations.Clear();
        }

        private void _tcMain_SelectedIndexChanged(object sender, EventArgs e)
        {
            UpdateExtractButton();
        }

        private void _tvFiles_OnSelectionChanged(object sender, EventArgs e)
        {
            UpdateExtractButton();
        }

        private void _tvAnimations_OnSelectionChanged(object sender, EventArgs e)
        {
            UpdateExtractButton();
        }

        private void UpdateExtractButton()
        {
            _btnExtract.Enabled = _tcMain.Enabled && (_tcMain.SelectedTab == _tpFiles ? _tvFiles : _tvAnimations).SelectedNodes.Any();
        }

        private async void _btnExtract_Click(object sender, EventArgs e)
        {
            try
            {
                if (_tcMain.SelectedTab == _tpFiles)
                    await ExtractFilesAsync();
                else if (_tcMain.SelectedTab == _tpAnimations)
                    await ExtractAnimationsAsync();

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
            }
            finally
            {
                _archiveSet.CloseStreams();
            }
        }

        private async Task ExtractFilesAsync()
        {
            List<ArchiveFileReference> fileRefs = new();
            foreach (VirtualTreeNode node in _tvFiles.SelectedNodes)
            {
                ArchiveFileReference fileRef = _archiveSet.GetFileReference(_tvFiles.GetNodeData<FileLogEntry>(node).Key);
                if (fileRef != null)
                    fileRefs.Add(fileRef);
            }
            
            string folderPath = Path.GetDirectoryName(Assembly.GetEntryAssembly().Location);
            Extractor extractor = new Extractor(_archiveSet);
            await Task.Run(() => extractor.Extract(folderPath, fileRefs, this, CancellationTokenSource.Token));

        }

        private async Task ExtractAnimationsAsync()
        {
            Dictionary<string, ResourceReference> animRefs = new();
            foreach (VirtualTreeNode node in _tvAnimations.SelectedNodes)
            {
                AnimationLogEntry entry = _tvAnimations.GetNodeData<AnimationLogEntry>(node);
                ResourceReference resourceRef = _resourceUsages.GetResourceReference(_archiveSet, new ResourceKey(ResourceType.Animation, entry.Id));
                if (resourceRef != null)
                    animRefs[entry.Name] = resourceRef;
            }

            string folderPath = Path.Combine(Path.GetDirectoryName(Assembly.GetEntryAssembly().Location), "Animations");
            await Task.Run(() => ExtractAnimations(folderPath, animRefs, this));
        }

        private void ExtractAnimations(string baseFolderPath, Dictionary<string, ResourceReference> animRefs, ITaskProgress progress)
        {
            try
            {
                progress.Begin("Extracting...");

                int numExtracted = 0;
                foreach ((string name, ResourceReference resourceRef) in animRefs)
                {
                    string folderPath = Path.Combine(baseFolderPath, name);
                    Directory.CreateDirectory(folderPath);

                    string filePath = Path.Combine(folderPath, ResourceNaming.GetFileName(resourceRef));
                    using Stream resourceStream = _archiveSet.OpenResource(resourceRef);
                    using Stream fileStream = File.Create(filePath);
                    resourceStream.CopyTo(fileStream);

                    numExtracted++;
                    progress.Report((float)numExtracted / animRefs.Count);
                }

            }
            finally
            {
                progress.End();
            }
        }

        protected override void EnableUi(bool enable)
        {
            _tcMain.Enabled = enable;
            UpdateExtractButton();
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                components?.Dispose();
                _game.Events.OpeningFile -= HandleOpeningFile;
                _game.Events.PlayingAnimation -= HandlePlayingAnimation;
            }
            
            base.Dispose(disposing);
        }
    }
}
