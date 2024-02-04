using System;
using System.Windows.Forms;
using SottrModManager.Shared;

namespace SottrExtractor
{
    public static class Program
    {
        [STAThread]
        public static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            string gameFolderPath = GameFolderFinder.Find();
            if (gameFolderPath == null)
                return;

            Application.Run(new MainForm(gameFolderPath));
        }
    }
}
