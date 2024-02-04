using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using SottrModManager.Shared;
using SottrModManager.Shared.Cdc;

namespace SottrExtractor
{
    public partial class MainForm : Form, ITaskProgress
    {
        private readonly ArchiveSet _archiveSet;
        private readonly CancellationTokenSource _cancellationTokenSource = new CancellationTokenSource();
        private bool _closeRequested;

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

        private void MainForm_Load(object sender, EventArgs e)
        {
            _tvFiles.Populate(_archiveSet);
        }

        private void _tvFiles_SelectionChanged(object sender, EventArgs e)
        {
            _btnExtract.Enabled = _tvFiles.SelectedFiles.Count > 0;
        }

        private async void _btnExtract_Click(object sender, EventArgs e)
        {
            try
            {
                ResourceExtractor resourceExtractor = new ResourceExtractor(_archiveSet);
                FileExtractor fileExtractor = new FileExtractor(_archiveSet);
                string baseFolderPath = Path.GetDirectoryName(Assembly.GetEntryAssembly().Location);

                List<ArchiveFileReference> fileRefs = _tvFiles.SelectedFiles;
                MultiStepTaskProgress progress = new MultiStepTaskProgress(this, fileRefs.Count);
                foreach (ArchiveFileReference fileRef in fileRefs)
                {
                    string filePath = GetFilePath(baseFolderPath, fileRef);
                    ResourceCollection collection = Path.GetExtension(filePath) == ".drm" ? _archiveSet.GetResourceCollection(fileRef) : null;
                    if (collection != null)
                        await Task.Run(() => resourceExtractor.Extract(filePath, collection, progress, _cancellationTokenSource.Token));
                    else
                        await Task.Run(() => fileExtractor.Extract(filePath, fileRef, progress, _cancellationTokenSource.Token));
                }
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

        private static string GetFilePath(string baseFolderPath, ArchiveFileReference fileRef)
        {
            string fileName = CdcHash.Lookup(fileRef.NameHash) ?? fileRef.NameHash.ToString("X016");
            if ((fileRef.Locale & 0xFFFFFFF) != 0xFFFFFFF)
            {
                string locales = string.Join(
                    '.',
                    Enum.GetValues(typeof(LocaleLanguage))
                        .Cast<LocaleLanguage>()
                        .Where(l => (fileRef.Locale & (uint)l) != 0)
                        .Select(l => l.ToString().ToLower())
                );
                fileName += "\\" + locales + Path.GetExtension(fileName);
            }
            return Path.Combine(baseFolderPath, fileName);
        }

        private void MainForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (!_progressBar.Visible)
                return;

            _statusBar.Text = "Canceling...";
            _cancellationTokenSource.Cancel();
            _closeRequested = true;
            e.Cancel = true;
        }

        void ITaskProgress.Begin(string statusText)
        {
            if (InvokeRequired)
            {
                Invoke(new MethodInvoker(() => ((ITaskProgress)this).Begin(statusText)));
                return;
            }

            EnableUi(false);
            _lblStatus.Text = statusText;
            _progressBar.Value = 0;
            _progressBar.Visible = true;
        }

        void ITaskProgress.Report(float progress)
        {
            if (InvokeRequired)
            {
                Invoke(new MethodInvoker(() => ((ITaskProgress)this).Report(progress)));
                return;
            }

            _progressBar.Value = (int)(progress * _progressBar.Maximum);
        }

        void ITaskProgress.End()
        {
            if (InvokeRequired)
            {
                Invoke(new MethodInvoker(() => ((ITaskProgress)this).End()));
                return;
            }

            EnableUi(true);
            _lblStatus.Text = string.Empty;
            _progressBar.Visible = false;
            if (_closeRequested)
                Close();
        }

        private void EnableUi(bool enable)
        {
            _tvFiles.Enabled = enable;
            _btnExtract.Enabled = enable;
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
