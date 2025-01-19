using System;
using System.Configuration;
using System.Windows.Forms;
using TrRebootTools.Shared.Cdc;

namespace TrRebootTools.Shared.Forms
{
    public partial class GameSelectionForm : Form
    {
        private CdcGame? _selectedGame;

        public GameSelectionForm()
        {
            InitializeComponent();
        }

        private void _btnTr2013_Click(object sender, EventArgs e)
        {
            _selectedGame = CdcGame.Tr2013;
            Close();
        }

        private void _btnRise_Click(object sender, EventArgs e)
        {
            _selectedGame = CdcGame.Rise;
            Close();
        }

        private void _btnShadow_Click(object sender, EventArgs e)
        {
            _selectedGame = CdcGame.Shadow;
            Close();
        }

        public static CdcGame? GetGame(bool forcePrompt)
        {
            string lastSelectedGame = ConfigurationManager.AppSettings["SelectedGame"];
            if (forcePrompt || string.IsNullOrEmpty(lastSelectedGame) || !Enum.TryParse(lastSelectedGame, out CdcGame game))
            {
                using GameSelectionForm form = new();
                form.ShowDialog();
                if (form._selectedGame == null)
                    return null;

                game = form._selectedGame.Value;
            }

            Configuration config = ConfigurationManager.OpenExeConfiguration(ConfigurationUserLevel.None);
            config.AppSettings.Settings["SelectedGame"].Value = game.ToString();
            config.Save(ConfigurationSaveMode.Modified);
            return game;
        }
    }
}
