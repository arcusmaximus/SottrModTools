using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using SottrExtractor.LogHook;
using SottrModManager.Shared.Cdc;

namespace SottrExtractor
{
    public partial class MainForm : FormWithProgress
    {
        private readonly ArchiveSet _archiveSet;
        private readonly ResourceUsageCache _resourceUsages = new();

        public MainForm()
        {
            InitializeComponent();
        }

        public MainForm(string gameFolderPath)
            : this()
        {
            Version version = Assembly.GetEntryAssembly().GetName().Version;
            Text += $" {version.Major}.{version.Minor}.{version.Build}";

            _archiveSet = new ArchiveSet(gameFolderPath, true, false);
        }

        private async void MainForm_Load(object sender, EventArgs e)
        {
            _tvFiles.Populate(_archiveSet);

            if (!_resourceUsages.Load(_archiveSet.FolderPath))
            {
                await Task.Run(() => _resourceUsages.AddArchiveSet(_archiveSet, this, CancellationTokenSource.Token));
                _resourceUsages.Save(_archiveSet.FolderPath);
            }
        }

        private void _tvFiles_SelectionChanged(object sender, EventArgs e)
        {
            _btnExtract.Enabled = _tvFiles.SelectedFiles.Count > 0;
        }

        private async void _btnExtract_Click(object sender, EventArgs e)
        {
            try
            {
                string folderPath = Path.GetDirectoryName(Assembly.GetEntryAssembly().Location);
                Extractor extractor = new Extractor(_archiveSet);
                await Task.Run(() => extractor.Extract(folderPath, _tvFiles.SelectedFiles, this, CancellationTokenSource.Token));
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

        private void _btnLaunchWithLog_Click(object sender, EventArgs e)
        {
            string exePath = Path.Combine(_archiveSet.FolderPath, "SOTTR.exe");
            if (!File.Exists(exePath))
            {
                MessageBox.Show($"Game not found at {exePath}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                return;
            }

            FileVersionInfo versionInfo = FileVersionInfo.GetVersionInfo(exePath);
            Version version = new Version(versionInfo.FileMajorPart, versionInfo.FileMinorPart, versionInfo.FileBuildPart);
            if (version != Game.ExpectedVersion)
            {
                MessageBox.Show($"Logging only works with version {Game.ExpectedVersion} of the game (you have version {version} installed).",
                    "Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                return;
            }

            using Game game = new Game(exePath);
            try
            {
                game.Start();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to launch game:\r\n" + ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                return;
            }

            using LogForm form = new LogForm(game, _archiveSet, _resourceUsages);
            form.ShowDialog();
        }

        protected override void EnableUi(bool enable)
        {
            _tvFiles.Enabled = enable;
            _btnExtract.Enabled = _tvFiles.SelectedFiles.Count > 0;
            _btnLaunchWithLog.Enabled = enable;
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
                components?.Dispose();

            _archiveSet.Dispose();

            base.Dispose(disposing);
        }
    }
}
