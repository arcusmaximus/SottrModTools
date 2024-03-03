namespace SoundConverter
{
    partial class MainForm
    {
        /// <summary>
        /// 必要なデザイナー変数です。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 使用中のリソースをすべてクリーンアップします。
        /// </summary>
        /// <param name="disposing">マネージド リソースを破棄する場合は true を指定し、その他の場合は false を指定します。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows フォーム デザイナーで生成されたコード

        /// <summary>
        /// デザイナー サポートに必要なメソッドです。このメソッドの内容を
        /// コード エディターで変更しないでください。
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
            this._lstInputFiles = new System.Windows.Forms.ListBox();
            this._lblWavFiles = new System.Windows.Forms.Label();
            this._lblOutputFolder = new System.Windows.Forms.Label();
            this._btnAddWavFile = new System.Windows.Forms.Button();
            this._btnRemoveSelectedWavs = new System.Windows.Forms.Button();
            this._btnClearWavFiles = new System.Windows.Forms.Button();
            this._txtOutputFolder = new System.Windows.Forms.TextBox();
            this._btnBrowseWemFolder = new System.Windows.Forms.Button();
            this._btnConvert = new System.Windows.Forms.Button();
            this._progressBar = new System.Windows.Forms.ProgressBar();
            this._btnCancel = new System.Windows.Forms.Button();
            this._pnlOptions = new System.Windows.Forms.Panel();
            this._dlgSelectInputFiles = new System.Windows.Forms.OpenFileDialog();
            this._dlgSelectOutputFolder = new Ookii.Dialogs.WinForms.VistaFolderBrowserDialog();
            this._dlgSelectWwiseConsole = new System.Windows.Forms.OpenFileDialog();
            this._pnlOptions.SuspendLayout();
            this.SuspendLayout();
            // 
            // _lstInputFiles
            // 
            this._lstInputFiles.AllowDrop = true;
            this._lstInputFiles.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this._lstInputFiles.FormattingEnabled = true;
            this._lstInputFiles.IntegralHeight = false;
            this._lstInputFiles.ItemHeight = 12;
            this._lstInputFiles.Location = new System.Drawing.Point(8, 27);
            this._lstInputFiles.Name = "_lstInputFiles";
            this._lstInputFiles.SelectionMode = System.Windows.Forms.SelectionMode.MultiSimple;
            this._lstInputFiles.Size = new System.Drawing.Size(660, 223);
            this._lstInputFiles.TabIndex = 0;
            this._lstInputFiles.DragDrop += new System.Windows.Forms.DragEventHandler(this._lstWavFiles_DragDrop);
            this._lstInputFiles.DragEnter += new System.Windows.Forms.DragEventHandler(this._lstWavFiles_DragEnter);
            // 
            // _lblWavFiles
            // 
            this._lblWavFiles.AutoSize = true;
            this._lblWavFiles.Location = new System.Drawing.Point(6, 10);
            this._lblWavFiles.Name = "_lblWavFiles";
            this._lblWavFiles.Size = new System.Drawing.Size(84, 12);
            this._lblWavFiles.TabIndex = 1;
            this._lblWavFiles.Text = "Input .wav files:";
            // 
            // _lblOutputFolder
            // 
            this._lblOutputFolder.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this._lblOutputFolder.AutoSize = true;
            this._lblOutputFolder.Location = new System.Drawing.Point(6, 320);
            this._lblOutputFolder.Name = "_lblOutputFolder";
            this._lblOutputFolder.Size = new System.Drawing.Size(147, 12);
            this._lblOutputFolder.TabIndex = 2;
            this._lblOutputFolder.Text = "Output folder for .wem files:";
            // 
            // _btnAddWavFile
            // 
            this._btnAddWavFile.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this._btnAddWavFile.Location = new System.Drawing.Point(8, 256);
            this._btnAddWavFile.Name = "_btnAddWavFile";
            this._btnAddWavFile.Size = new System.Drawing.Size(124, 36);
            this._btnAddWavFile.TabIndex = 3;
            this._btnAddWavFile.Text = "Add files...";
            this._btnAddWavFile.UseVisualStyleBackColor = true;
            this._btnAddWavFile.Click += new System.EventHandler(this._btnAddWavFile_Click);
            // 
            // _btnRemoveSelectedWavs
            // 
            this._btnRemoveSelectedWavs.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this._btnRemoveSelectedWavs.Location = new System.Drawing.Point(391, 256);
            this._btnRemoveSelectedWavs.Name = "_btnRemoveSelectedWavs";
            this._btnRemoveSelectedWavs.Size = new System.Drawing.Size(151, 36);
            this._btnRemoveSelectedWavs.TabIndex = 3;
            this._btnRemoveSelectedWavs.Text = "Remove selected";
            this._btnRemoveSelectedWavs.UseVisualStyleBackColor = true;
            this._btnRemoveSelectedWavs.Click += new System.EventHandler(this._btnRemoveSelectedWavs_Click);
            // 
            // _btnClearWavFiles
            // 
            this._btnClearWavFiles.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this._btnClearWavFiles.Location = new System.Drawing.Point(548, 256);
            this._btnClearWavFiles.Name = "_btnClearWavFiles";
            this._btnClearWavFiles.Size = new System.Drawing.Size(120, 36);
            this._btnClearWavFiles.TabIndex = 3;
            this._btnClearWavFiles.Text = "Clear";
            this._btnClearWavFiles.UseVisualStyleBackColor = true;
            this._btnClearWavFiles.Click += new System.EventHandler(this._btnClearWavFiles_Click);
            // 
            // _txtOutputFolder
            // 
            this._txtOutputFolder.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this._txtOutputFolder.Location = new System.Drawing.Point(8, 335);
            this._txtOutputFolder.Name = "_txtOutputFolder";
            this._txtOutputFolder.Size = new System.Drawing.Size(613, 19);
            this._txtOutputFolder.TabIndex = 4;
            // 
            // _btnBrowseWemFolder
            // 
            this._btnBrowseWemFolder.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this._btnBrowseWemFolder.Location = new System.Drawing.Point(627, 334);
            this._btnBrowseWemFolder.Name = "_btnBrowseWemFolder";
            this._btnBrowseWemFolder.Size = new System.Drawing.Size(41, 21);
            this._btnBrowseWemFolder.TabIndex = 5;
            this._btnBrowseWemFolder.Text = "...";
            this._btnBrowseWemFolder.UseVisualStyleBackColor = true;
            this._btnBrowseWemFolder.Click += new System.EventHandler(this._btnBrowseWemFolder_Click);
            // 
            // _btnConvert
            // 
            this._btnConvert.Anchor = System.Windows.Forms.AnchorStyles.Bottom;
            this._btnConvert.Location = new System.Drawing.Point(277, 391);
            this._btnConvert.Name = "_btnConvert";
            this._btnConvert.Size = new System.Drawing.Size(141, 42);
            this._btnConvert.TabIndex = 6;
            this._btnConvert.Text = "Convert";
            this._btnConvert.UseVisualStyleBackColor = true;
            this._btnConvert.Click += new System.EventHandler(this._btnConvert_Click);
            // 
            // _progressBar
            // 
            this._progressBar.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this._progressBar.Location = new System.Drawing.Point(14, 398);
            this._progressBar.Name = "_progressBar";
            this._progressBar.Size = new System.Drawing.Size(558, 29);
            this._progressBar.Step = 1;
            this._progressBar.TabIndex = 7;
            this._progressBar.Visible = false;
            // 
            // _btnCancel
            // 
            this._btnCancel.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this._btnCancel.Location = new System.Drawing.Point(578, 398);
            this._btnCancel.Name = "_btnCancel";
            this._btnCancel.Size = new System.Drawing.Size(102, 29);
            this._btnCancel.TabIndex = 8;
            this._btnCancel.Text = "Cancel";
            this._btnCancel.UseVisualStyleBackColor = true;
            this._btnCancel.Visible = false;
            this._btnCancel.Click += new System.EventHandler(this._btnCancel_Click);
            // 
            // _pnlOptions
            // 
            this._pnlOptions.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this._pnlOptions.Controls.Add(this._btnBrowseWemFolder);
            this._pnlOptions.Controls.Add(this._txtOutputFolder);
            this._pnlOptions.Controls.Add(this._btnClearWavFiles);
            this._pnlOptions.Controls.Add(this._btnRemoveSelectedWavs);
            this._pnlOptions.Controls.Add(this._btnAddWavFile);
            this._pnlOptions.Controls.Add(this._lblOutputFolder);
            this._pnlOptions.Controls.Add(this._lblWavFiles);
            this._pnlOptions.Controls.Add(this._lstInputFiles);
            this._pnlOptions.Location = new System.Drawing.Point(12, 6);
            this._pnlOptions.Name = "_pnlOptions";
            this._pnlOptions.Size = new System.Drawing.Size(670, 379);
            this._pnlOptions.TabIndex = 9;
            // 
            // _dlgSelectInputFiles
            // 
            this._dlgSelectInputFiles.Filter = "Wave files|*.wav";
            this._dlgSelectInputFiles.Multiselect = true;
            // 
            // _dlgSelectWwiseConsole
            // 
            this._dlgSelectWwiseConsole.Filter = "WwiseConsole.exe|WwiseConsole.exe";
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(694, 444);
            this.Controls.Add(this._btnConvert);
            this.Controls.Add(this._pnlOptions);
            this.Controls.Add(this._btnCancel);
            this.Controls.Add(this._progressBar);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MinimumSize = new System.Drawing.Size(590, 360);
            this.Name = "MainForm";
            this.Text = "Wwise Sound Conversion Helper";
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.MainForm_FormClosing);
            this.Load += new System.EventHandler(this.MainForm_Load);
            this._pnlOptions.ResumeLayout(false);
            this._pnlOptions.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.ListBox _lstInputFiles;
        private System.Windows.Forms.Label _lblWavFiles;
        private System.Windows.Forms.Label _lblOutputFolder;
        private System.Windows.Forms.Button _btnAddWavFile;
        private System.Windows.Forms.Button _btnRemoveSelectedWavs;
        private System.Windows.Forms.Button _btnClearWavFiles;
        private System.Windows.Forms.TextBox _txtOutputFolder;
        private System.Windows.Forms.Button _btnBrowseWemFolder;
        private System.Windows.Forms.Button _btnConvert;
        private System.Windows.Forms.ProgressBar _progressBar;
        private System.Windows.Forms.Button _btnCancel;
        private System.Windows.Forms.Panel _pnlOptions;
        private System.Windows.Forms.OpenFileDialog _dlgSelectInputFiles;
        private Ookii.Dialogs.WinForms.VistaFolderBrowserDialog _dlgSelectOutputFolder;
        private System.Windows.Forms.OpenFileDialog _dlgSelectWwiseConsole;
    }
}

