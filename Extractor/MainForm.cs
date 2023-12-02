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
                ResourceExtractor extractor = new ResourceExtractor(_archiveSet);
                string baseFolderPath = Path.GetDirectoryName(Assembly.GetEntryAssembly().Location);

                List<ArchiveFileReference> fileRefs = _tvFiles.SelectedFiles;
                MultiStepTaskProgress progress = new MultiStepTaskProgress(this, fileRefs.Count);
                foreach (ArchiveFileReference fileRef in fileRefs)
                {
                    string filePath = Path.Combine(baseFolderPath, CdcHash.Lookup(fileRef.NameHash));
                    ResourceCollection collection = _archiveSet.GetResourceCollection(fileRef);
                    if (collection != null)
                    {
                        await Task.Run(() => extractor.Extract(filePath, collection, progress, _cancellationTokenSource.Token));
                    }
                    else
                    {
                        progress.Begin(string.Empty);
                        using Stream archiveFileStream = _archiveSet.OpenFile(fileRef);
                        using Stream extractedFileStream = File.Create(filePath);
                        archiveFileStream.CopyTo(extractedFileStream);
                        progress.End();
                    }
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
