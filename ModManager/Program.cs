using System;
using System.IO;
using System.Runtime.ExceptionServices;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using SottrModManager.Shared;
using SottrModManager.Shared.Cdc;
using SottrModManager.Mod;

namespace SottrModManager
{
    public static class Program
    {
        [STAThread]
        public static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            string gameFolderPath = GameFolderFinder.Find();
            if (gameFolderPath == null)
                return;

            if (args.Length == 1)
            {
                HandleCommandLine(gameFolderPath, args[0]);
                return;
            }

            Application.Run(new MainForm(gameFolderPath));
        }

        private static void HandleCommandLine(string gameFolderPath, string modPath)
        {
            using ArchiveSet archiveSet = new ArchiveSet(gameFolderPath, true, true);
            ResourceUsageCache resourceUsageCache = new ResourceUsageCache();

            try
            {
                bool reinstallMods = archiveSet.DuplicateArchives.Count > 0;

                if (!resourceUsageCache.Load(gameFolderPath))
                {
                    using ArchiveSet gameArchiveSet = new ArchiveSet(gameFolderPath, true, false);
                    RunTaskWithProgress((progress, cancellationToken) => resourceUsageCache.AddArchiveSet(archiveSet, progress, cancellationToken));
                    resourceUsageCache.Save(gameFolderPath);
                    reinstallMods = true;
                }

                if (reinstallMods)
                {
                    ModInstaller installer = new ModInstaller(archiveSet, resourceUsageCache);
                    RunTaskWithProgress((progress, cancellationToken) => installer.ReinstallAll(progress, cancellationToken));
                }

                InstallMod(archiveSet, resourceUsageCache, modPath);
            }
            catch (Exception ex) when (!(ex is OperationCanceledException))
            {
                MessageBox.Show(ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
            }
        }

        private static void InstallMod(ArchiveSet archiveSet, ResourceUsageCache resourceUsageCache, string modPath)
        {
            ModInstaller installer = new ModInstaller(archiveSet, resourceUsageCache);
            if (File.Exists(modPath))
            {
                string extension = Path.GetExtension(modPath);
                if (extension != ".7z" && extension != ".zip" && extension != ".rar")
                {
                    MessageBox.Show(
                        "Only .zip and .7z files are supported for direct mod installation. Please extract the archive and install the folder instead.",
                        "File not supported",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Exclamation
                    );
                    return;
                }
                RunTaskWithProgress((progress, cancellationToken) => installer.InstallFromZip(modPath, progress, cancellationToken));
            }
            else if (Directory.Exists(modPath))
            {
                RunTaskWithProgress((progress, cancellationToken) => installer.InstallFromFolder(modPath, progress, cancellationToken));
            }
            else
            {
                MessageBox.Show("The specified mod path does not exist.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
            }
        }

        private static void RunTaskWithProgress(Action<ITaskProgress, CancellationToken> action)
        {
            using TaskProgressForm progressForm = new TaskProgressForm();
            ExceptionDispatchInfo exception = null;
            progressForm.Load +=
                async (s, e) =>
                {
                    try
                    {
                        await Task.Run(() => action(progressForm, progressForm.CancellationToken), progressForm.CancellationToken);
                    }
                    catch (Exception ex)
                    {
                        exception = ExceptionDispatchInfo.Capture(ex);
                    }
                    progressForm.Close();
                };
            Application.Run(progressForm);
            exception?.Throw();
        }
    }
}
