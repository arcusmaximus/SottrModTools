using System.Drawing;
using System.Windows.Forms;

namespace TrRebootTools.Extractor.Controls
{
    internal partial class FileTreeViewBase : UserControl
    {
        protected static readonly Image FolderImage = TrRebootTools.Extractor.Properties.Resources.Folder;
        protected static readonly Image FileImage = TrRebootTools.Extractor.Properties.Resources.File;

        public FileTreeViewBase()
        {
            InitializeComponent();
        }
    }
}
