using System.Drawing;
using System.Windows.Forms;

namespace SottrExtractor.Controls
{
    internal partial class FileTreeViewBase : UserControl
    {
        protected static readonly Image FolderImage = Properties.Resources.Folder;
        protected static readonly Image FileImage = Properties.Resources.File;

        public FileTreeViewBase()
        {
            InitializeComponent();
        }
    }
}
