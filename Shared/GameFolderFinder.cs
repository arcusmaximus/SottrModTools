using System;
using System.Configuration;
using System.IO;
using System.Windows.Forms;
using Microsoft.Win32;

namespace SottrModManager.Shared
{
    public static class GameFolderFinder
    {
        public static string Find()
        {
            Func<string>[] getters =
            {
                GetGameFolderFromConfiguration,
                GetGameFolderFromRegistry,
                GetGameFolderFromFileBrowser
            };
            foreach (Func<string> getter in getters)
            {
                string gameFolderPath = getter();
                if (string.IsNullOrEmpty(gameFolderPath) || !File.Exists(Path.Combine(gameFolderPath, "SOTTR.exe")))
                    continue;

                Configuration config = ConfigurationManager.OpenExeConfiguration(ConfigurationUserLevel.None);
                config.AppSettings.Settings["GameFolder"].Value = gameFolderPath;
                config.Save(ConfigurationSaveMode.Modified);
                ConfigurationManager.RefreshSection(config.AppSettings.SectionInformation.Name);
                return gameFolderPath;
            }

            return null;
        }

        private static string GetGameFolderFromConfiguration()
        {
            return ConfigurationManager.AppSettings["GameFolder"];
        }

        private static string GetGameFolderFromRegistry()
        {
            using RegistryKey uninstallKey = Registry.LocalMachine.OpenSubKey(@"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall");
            if (uninstallKey == null)
                return null;

            foreach (string appName in uninstallKey.GetSubKeyNames())
            {
                using RegistryKey appKey = uninstallKey.OpenSubKey(appName);
                if (appKey?.GetValue("DisplayName") as string == "Shadow of the Tomb Raider")
                    return appKey.GetValue("InstallLocation") as string;
            }

            return null;
        }

        private static string GetGameFolderFromFileBrowser()
        {
            MessageBox.Show(
                "Could not automatically determine the Shadow of the Tomb Raider installation folder. Please select it manually.",
                "SOTTR Mod Manager",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );

            while (true)
            {
                using OpenFileDialog dialog = new OpenFileDialog
                {
                    Filter = "SOTTR.exe|SOTTR.exe",
                    FileName = "SOTTR.exe"
                };
                if (dialog.ShowDialog() != DialogResult.OK)
                    return null;

                string folderPath = Path.GetDirectoryName(dialog.FileName);
                if (File.Exists(Path.Combine(folderPath, "SOTTR.exe")))
                    return folderPath;

                MessageBox.Show("Could not find SOTTR.exe in the selected folder.", "Game not found", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
            }
        }
    }
}
