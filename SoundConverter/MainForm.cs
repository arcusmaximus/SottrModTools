using System;
using System.Configuration;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Xml.Linq;

namespace SoundConverter
{
    public partial class MainForm : Form
    {
        private string _wwiseConsolePath;
        private CancellationTokenSource _cancellationTokenSource;

        public MainForm()
        {
            InitializeComponent();
            Font = SystemFonts.MessageBoxFont;
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            _wwiseConsolePath = ConfigurationManager.AppSettings["WwiseConsole"];
            _txtOutputWemFolder.Text = ConfigurationManager.AppSettings["OutputFolder"];

            if (!string.IsNullOrEmpty(_wwiseConsolePath) && File.Exists(_wwiseConsolePath))
                return;

            MessageBox.Show("Please install the Wwise authoring tools (through the Audiokinetic Launcher) and select the location of WwiseConsole.exe", "", MessageBoxButtons.OK, MessageBoxIcon.Information);
            if (_dlgSelectWwiseConsole.ShowDialog() != DialogResult.OK)
            {
                Close();
                return;
            }

            _wwiseConsolePath = _dlgSelectWwiseConsole.FileName;
            Configuration config = ConfigurationManager.OpenExeConfiguration(ConfigurationUserLevel.None);
            config.AppSettings.Settings["WwiseConsole"].Value = _wwiseConsolePath;
            config.Save(ConfigurationSaveMode.Modified);
        }

        private void _lstWavFiles_DragEnter(object sender, DragEventArgs e)
        {
            if (GetDroppedFilesIfAllowed(e) != null)
                e.Effect = DragDropEffects.Copy;
        }

        private void _lstWavFiles_DragDrop(object sender, DragEventArgs e)
        {
            string[] wavFilePaths = GetDroppedFilesIfAllowed(e);
            if (wavFilePaths != null)
                _lstWavFiles.Items.AddRange(wavFilePaths);
        }

        private string[] GetDroppedFilesIfAllowed(DragEventArgs e)
        {
            if (!_pnlOptions.Enabled)
                return null;

            if (e.Data.GetData(DataFormats.FileDrop) is not string[] paths)
                return null;

            foreach (string path in paths)
            {
                if (!File.Exists(path) || Path.GetExtension(path) != ".wav")
                    return null;
            }
            return paths;
        }

        private void _btnAddWavFile_Click(object sender, EventArgs e)
        {
            if (_dlgSelectInputFiles.ShowDialog() != DialogResult.OK)
                return;

            _lstWavFiles.Items.AddRange(_dlgSelectInputFiles.FileNames);
        }

        private void _btnRemoveSelectedWavs_Click(object sender, EventArgs e)
        {
            foreach (int index in _lstWavFiles.SelectedIndices.Cast<int>().OrderByDescending(i => i).ToList())
            {
                _lstWavFiles.Items.RemoveAt(index);
            }
        }

        private void _btnClearWavFiles_Click(object sender, EventArgs e)
        {
            _lstWavFiles.Items.Clear();
        }

        private void _btnBrowseWemFolder_Click(object sender, EventArgs e)
        {
            if (_dlgSelectOutputFolder.ShowDialog() != DialogResult.OK)
                return;

            _txtOutputWemFolder.Text = _dlgSelectOutputFolder.SelectedPath;
        }

        private async void _btnConvert_Click(object sender, EventArgs e)
        {
            if (_lstWavFiles.Items.Count == 0)
            {
                MessageBox.Show("Please select files to convert.", "", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            if (string.IsNullOrWhiteSpace(_txtOutputWemFolder.Text))
            {
                MessageBox.Show("Please specify an output folder.", "", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            if (!Directory.Exists(_txtOutputWemFolder.Text))
            {
                MessageBox.Show("The specified output folder does not exist.", "", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                return;
            }

            _cancellationTokenSource = new();

            string projectFolderPath = Path.Combine(Path.GetDirectoryName(Assembly.GetEntryAssembly().Location), "TempWwiseProject");
            string projectFilePath = Path.Combine(projectFolderPath, Path.GetFileName(projectFolderPath) + ".wproj");
            string outputFolderPath = _txtOutputWemFolder.Text;

            try
            {
                _progressBar.Value = 0;
                _progressBar.Maximum = _lstWavFiles.Items.Count;

                SetWorking(true);

                if (Directory.Exists(projectFolderPath))
                    Directory.Delete(projectFolderPath, true);

                CreateWwiseProject(projectFilePath);
                foreach (string wavFilePath in _lstWavFiles.Items)
                {
                    if (_cancellationTokenSource.Token.IsCancellationRequested)
                        break;

                    await Task.Run(() => ConvertFile(projectFilePath, wavFilePath, outputFolderPath));
                    _progressBar.PerformStep();
                }

                if (!_cancellationTokenSource.Token.IsCancellationRequested)
                    MessageBox.Show("Conversion complete.", "", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
            }
            finally
            {
                if (Directory.Exists(projectFolderPath))
                    Directory.Delete(projectFolderPath, true);

                SetWorking(false);
            }
        }

        private void CreateWwiseProject(string projectFilePath)
        {
            using Process process = Process.Start(
                new ProcessStartInfo
                {
                    FileName = _wwiseConsolePath,
                    Arguments = $"create-new-project \"{projectFilePath}\"",
                    CreateNoWindow = true,
                    UseShellExecute = false
                }
            );
            process.WaitForExit();
        }

        private void ConvertFile(string projectFilePath, string wavFilePath, string outputFolderPath)
        {
            string projectFolderPath = Path.GetDirectoryName(projectFilePath);
            string sourcesFilePath = Path.Combine(projectFolderPath, "sources.wsources");
            XElement sourcesXml =
                new XElement(
                    "ExternalSourcesList",
                    new XAttribute("SchemaVersion", 1),
                    new XElement(
                        "Source",
                        new XAttribute("Path", wavFilePath),
                        new XAttribute("Conversion", "Vorbis Quality High")
                    )
                );
            sourcesXml.Save(sourcesFilePath);

            using Process process = Process.Start(
                new ProcessStartInfo
                {
                    FileName = _wwiseConsolePath,
                    Arguments = $"convert-external-source \"{projectFilePath}\" --source-file \"{sourcesFilePath}\"",
                    CreateNoWindow = true,
                    UseShellExecute = false
                }
            );
            process.WaitForExit();

            string fromWemFilePath = Path.Combine(
                projectFolderPath,
                "GeneratedSoundBanks",
                "Windows",
                Path.ChangeExtension(Path.GetFileName(wavFilePath), ".wem")
            );
            if (!File.Exists(fromWemFilePath))
                return;

            string toWemFilePath = Path.Combine(outputFolderPath, Path.GetFileName(fromWemFilePath));
            if (File.Exists(toWemFilePath))
                File.Delete(toWemFilePath);
            
            File.Move(fromWemFilePath, toWemFilePath);
        }

        private void SetWorking(bool working)
        {
            _pnlOptions.Enabled = !working;
            _btnConvert.Visible = !working;
            _progressBar.Visible = working;
            _btnCancel.Visible = working;
        }

        private void _btnCancel_Click(object sender, EventArgs e)
        {
            _btnCancel.Enabled = false;
            _cancellationTokenSource.Cancel();
        }

        private void MainForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            Configuration config = ConfigurationManager.OpenExeConfiguration(ConfigurationUserLevel.None);
            config.AppSettings.Settings["OutputFolder"].Value = _txtOutputWemFolder.Text;
            config.Save(ConfigurationSaveMode.Modified);
        }
    }
}
