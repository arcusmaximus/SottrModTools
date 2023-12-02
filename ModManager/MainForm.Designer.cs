using SottrModManager.Controls;

namespace SottrModManager
{
    partial class MainForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
            _pnlToolbar = new System.Windows.Forms.TableLayoutPanel();
            _btnReinstall = new System.Windows.Forms.Button();
            _btnRemove = new System.Windows.Forms.Button();
            _btnAddFromZip = new System.Windows.Forms.Button();
            _btnAddFromFolder = new System.Windows.Forms.Button();
            _toolTip = new System.Windows.Forms.ToolTip(components);
            _statusBar = new System.Windows.Forms.StatusStrip();
            _lblStatus = new System.Windows.Forms.ToolStripStatusLabel();
            _progressBar = new System.Windows.Forms.ToolStripProgressBar();
            _lvMods = new BindableListView();
            _colModName = new System.Windows.Forms.ColumnHeader();
            _folderBrowser = new Ookii.Dialogs.WinForms.VistaFolderBrowserDialog();
            _fileBrowser = new System.Windows.Forms.OpenFileDialog();
            _pnlToolbar.SuspendLayout();
            _statusBar.SuspendLayout();
            SuspendLayout();
            // 
            // _pnlToolbar
            // 
            _pnlToolbar.ColumnCount = 4;
            _pnlToolbar.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 93F));
            _pnlToolbar.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 93F));
            _pnlToolbar.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 93F));
            _pnlToolbar.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
            _pnlToolbar.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 23F));
            _pnlToolbar.Controls.Add(_btnReinstall, 3, 0);
            _pnlToolbar.Controls.Add(_btnRemove, 2, 0);
            _pnlToolbar.Controls.Add(_btnAddFromZip, 0, 0);
            _pnlToolbar.Controls.Add(_btnAddFromFolder, 1, 0);
            _pnlToolbar.Dock = System.Windows.Forms.DockStyle.Top;
            _pnlToolbar.Location = new System.Drawing.Point(0, 0);
            _pnlToolbar.Margin = new System.Windows.Forms.Padding(4);
            _pnlToolbar.Name = "_pnlToolbar";
            _pnlToolbar.RowCount = 1;
            _pnlToolbar.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 100F));
            _pnlToolbar.Size = new System.Drawing.Size(748, 100);
            _pnlToolbar.TabIndex = 1;
            // 
            // _btnReinstall
            // 
            _btnReinstall.Anchor = System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right;
            _btnReinstall.FlatStyle = System.Windows.Forms.FlatStyle.Popup;
            _btnReinstall.Image = Properties.Resources.Reinstall;
            _btnReinstall.Location = new System.Drawing.Point(658, 4);
            _btnReinstall.Margin = new System.Windows.Forms.Padding(4);
            _btnReinstall.Name = "_btnReinstall";
            _btnReinstall.Size = new System.Drawing.Size(86, 92);
            _btnReinstall.TabIndex = 3;
            _toolTip.SetToolTip(_btnReinstall, "Reinstall all mods (may fix game crashes if things worked before)");
            _btnReinstall.UseVisualStyleBackColor = true;
            _btnReinstall.Click += _btnReinstall_Click;
            // 
            // _btnRemove
            // 
            _btnRemove.Dock = System.Windows.Forms.DockStyle.Fill;
            _btnRemove.FlatStyle = System.Windows.Forms.FlatStyle.Popup;
            _btnRemove.Image = (System.Drawing.Image)resources.GetObject("_btnRemove.Image");
            _btnRemove.Location = new System.Drawing.Point(190, 4);
            _btnRemove.Margin = new System.Windows.Forms.Padding(4);
            _btnRemove.Name = "_btnRemove";
            _btnRemove.Size = new System.Drawing.Size(85, 92);
            _btnRemove.TabIndex = 2;
            _toolTip.SetToolTip(_btnRemove, "Uninstall selected mods");
            _btnRemove.UseVisualStyleBackColor = true;
            _btnRemove.Click += _btnRemove_Click;
            // 
            // _btnAddFromZip
            // 
            _btnAddFromZip.Dock = System.Windows.Forms.DockStyle.Fill;
            _btnAddFromZip.FlatStyle = System.Windows.Forms.FlatStyle.Popup;
            _btnAddFromZip.Image = Properties.Resources.AddZip;
            _btnAddFromZip.Location = new System.Drawing.Point(4, 4);
            _btnAddFromZip.Margin = new System.Windows.Forms.Padding(4);
            _btnAddFromZip.Name = "_btnAddFromZip";
            _btnAddFromZip.Size = new System.Drawing.Size(85, 92);
            _btnAddFromZip.TabIndex = 0;
            _toolTip.SetToolTip(_btnAddFromZip, "Install mod from archive file (.7z/.zip/.rar)...");
            _btnAddFromZip.UseVisualStyleBackColor = true;
            _btnAddFromZip.Click += _btnAddFromZip_Click;
            // 
            // _btnAddFromFolder
            // 
            _btnAddFromFolder.Dock = System.Windows.Forms.DockStyle.Fill;
            _btnAddFromFolder.FlatStyle = System.Windows.Forms.FlatStyle.Popup;
            _btnAddFromFolder.Image = (System.Drawing.Image)resources.GetObject("_btnAddFromFolder.Image");
            _btnAddFromFolder.Location = new System.Drawing.Point(97, 4);
            _btnAddFromFolder.Margin = new System.Windows.Forms.Padding(4);
            _btnAddFromFolder.Name = "_btnAddFromFolder";
            _btnAddFromFolder.Size = new System.Drawing.Size(85, 92);
            _btnAddFromFolder.TabIndex = 1;
            _toolTip.SetToolTip(_btnAddFromFolder, "Install mod from folder...");
            _btnAddFromFolder.UseVisualStyleBackColor = true;
            _btnAddFromFolder.Click += _btnAddFromFolder_Click;
            // 
            // _statusBar
            // 
            _statusBar.Items.AddRange(new System.Windows.Forms.ToolStripItem[] { _lblStatus, _progressBar });
            _statusBar.Location = new System.Drawing.Point(0, 516);
            _statusBar.Name = "_statusBar";
            _statusBar.Padding = new System.Windows.Forms.Padding(1, 0, 16, 0);
            _statusBar.Size = new System.Drawing.Size(748, 22);
            _statusBar.TabIndex = 2;
            _statusBar.Text = "statusStrip1";
            // 
            // _lblStatus
            // 
            _lblStatus.Name = "_lblStatus";
            _lblStatus.Size = new System.Drawing.Size(731, 17);
            _lblStatus.Spring = true;
            _lblStatus.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // _progressBar
            // 
            _progressBar.Maximum = 1000;
            _progressBar.Name = "_progressBar";
            _progressBar.Size = new System.Drawing.Size(117, 20);
            _progressBar.Style = System.Windows.Forms.ProgressBarStyle.Continuous;
            _progressBar.Visible = false;
            // 
            // _lvMods
            // 
            _lvMods.AllowDrop = true;
            _lvMods.CheckBoxes = true;
            _lvMods.CheckedMember = null;
            _lvMods.Columns.AddRange(new System.Windows.Forms.ColumnHeader[] { _colModName });
            _lvMods.DataSource = null;
            _lvMods.DisplayMember = null;
            _lvMods.Dock = System.Windows.Forms.DockStyle.Fill;
            _lvMods.ForeColorMember = null;
            _lvMods.FullRowSelect = true;
            _lvMods.Location = new System.Drawing.Point(0, 100);
            _lvMods.Name = "_lvMods";
            _lvMods.Size = new System.Drawing.Size(748, 416);
            _lvMods.TabIndex = 3;
            _lvMods.UseCompatibleStateImageBehavior = false;
            _lvMods.View = System.Windows.Forms.View.Details;
            _lvMods.DragDrop += _lvMods_DragDrop;
            _lvMods.DragEnter += _lvMods_DragEnter;
            _lvMods.KeyDown += _lvMods_KeyDown;
            // 
            // _colModName
            // 
            _colModName.Text = "Mod";
            // 
            // _fileBrowser
            // 
            _fileBrowser.Filter = "Archives|*.7z;*.zip;*.rar";
            _fileBrowser.Title = "Select the mod file to install";
            // 
            // MainForm
            // 
            AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            ClientSize = new System.Drawing.Size(748, 538);
            Controls.Add(_lvMods);
            Controls.Add(_statusBar);
            Controls.Add(_pnlToolbar);
            Icon = (System.Drawing.Icon)resources.GetObject("$this.Icon");
            Margin = new System.Windows.Forms.Padding(4);
            MinimumSize = new System.Drawing.Size(417, 390);
            Name = "MainForm";
            Text = "SOTTR Mod Manager";
            FormClosing += MainForm_FormClosing;
            Load += MainForm_Load;
            Resize += MainForm_Resize;
            _pnlToolbar.ResumeLayout(false);
            _statusBar.ResumeLayout(false);
            _statusBar.PerformLayout();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private System.Windows.Forms.Button _btnAddFromFolder;
        private System.Windows.Forms.TableLayoutPanel _pnlToolbar;
        private System.Windows.Forms.ToolTip _toolTip;
        private System.Windows.Forms.Button _btnAddFromZip;
        private System.Windows.Forms.StatusStrip _statusBar;
        private System.Windows.Forms.ToolStripStatusLabel _lblStatus;
        private System.Windows.Forms.ToolStripProgressBar _progressBar;
        private BindableListView _lvMods;
        private System.Windows.Forms.ColumnHeader _colModName;
        private Ookii.Dialogs.WinForms.VistaFolderBrowserDialog _folderBrowser;
        private System.Windows.Forms.OpenFileDialog _fileBrowser;
        private System.Windows.Forms.Button _btnReinstall;
        private System.Windows.Forms.Button _btnRemove;
    }
}