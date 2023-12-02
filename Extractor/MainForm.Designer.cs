
using SottrExtractor.Controls;

namespace SottrExtractor
{
    partial class MainForm
    {
        /// <summary>
        /// 必要なデザイナー変数です。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        #region Windows フォーム デザイナーで生成されたコード

        /// <summary>
        /// デザイナー サポートに必要なメソッドです。このメソッドの内容を
        /// コード エディターで変更しないでください。
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
            _statusBar = new System.Windows.Forms.StatusStrip();
            _lblStatus = new System.Windows.Forms.ToolStripStatusLabel();
            _progressBar = new System.Windows.Forms.ToolStripProgressBar();
            _tvFiles = new ArchiveFileTreeView();
            _btnExtract = new System.Windows.Forms.Button();
            _statusBar.SuspendLayout();
            SuspendLayout();
            // 
            // _statusBar
            // 
            _statusBar.Items.AddRange(new System.Windows.Forms.ToolStripItem[] { _lblStatus, _progressBar });
            _statusBar.Location = new System.Drawing.Point(0, 616);
            _statusBar.Name = "_statusBar";
            _statusBar.Padding = new System.Windows.Forms.Padding(1, 0, 16, 0);
            _statusBar.Size = new System.Drawing.Size(623, 22);
            _statusBar.TabIndex = 0;
            // 
            // _lblStatus
            // 
            _lblStatus.Name = "_lblStatus";
            _lblStatus.Size = new System.Drawing.Size(606, 17);
            _lblStatus.Spring = true;
            _lblStatus.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // _progressBar
            // 
            _progressBar.Name = "_progressBar";
            _progressBar.Size = new System.Drawing.Size(117, 20);
            _progressBar.Visible = false;
            // 
            // _tvFiles
            // 
            _tvFiles.Dock = System.Windows.Forms.DockStyle.Fill;
            _tvFiles.Location = new System.Drawing.Point(0, 0);
            _tvFiles.Margin = new System.Windows.Forms.Padding(5);
            _tvFiles.Name = "_tvFiles";
            _tvFiles.Size = new System.Drawing.Size(623, 554);
            _tvFiles.TabIndex = 0;
            _tvFiles.SelectionChanged += _tvFiles_SelectionChanged;
            // 
            // _btnExtract
            // 
            _btnExtract.Dock = System.Windows.Forms.DockStyle.Bottom;
            _btnExtract.Enabled = false;
            _btnExtract.Location = new System.Drawing.Point(0, 554);
            _btnExtract.Margin = new System.Windows.Forms.Padding(4);
            _btnExtract.Name = "_btnExtract";
            _btnExtract.Size = new System.Drawing.Size(623, 62);
            _btnExtract.TabIndex = 2;
            _btnExtract.Text = "Extract";
            _btnExtract.UseVisualStyleBackColor = true;
            _btnExtract.Click += _btnExtract_Click;
            // 
            // MainForm
            // 
            AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            ClientSize = new System.Drawing.Size(623, 638);
            Controls.Add(_tvFiles);
            Controls.Add(_btnExtract);
            Controls.Add(_statusBar);
            Icon = (System.Drawing.Icon)resources.GetObject("$this.Icon");
            Margin = new System.Windows.Forms.Padding(4);
            MinimumSize = new System.Drawing.Size(639, 428);
            Name = "MainForm";
            Text = "SOTTR Extractor";
            FormClosing += MainForm_FormClosing;
            Load += MainForm_Load;
            _statusBar.ResumeLayout(false);
            _statusBar.PerformLayout();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion
        private System.Windows.Forms.StatusStrip _statusBar;
        private System.Windows.Forms.ToolStripStatusLabel _lblStatus;
        private System.Windows.Forms.ToolStripProgressBar _progressBar;
        private ArchiveFileTreeView _tvFiles;
        private System.Windows.Forms.Button _btnExtract;
    }
}

