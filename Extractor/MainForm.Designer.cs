
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
            this._statusBar = new System.Windows.Forms.StatusStrip();
            this._lblStatus = new System.Windows.Forms.ToolStripStatusLabel();
            this._progressBar = new System.Windows.Forms.ToolStripProgressBar();
            this._tvFiles = new SottrExtractor.Controls.ArchiveFileTreeView();
            this._btnExtract = new System.Windows.Forms.Button();
            this._statusBar.SuspendLayout();
            this.SuspendLayout();
            // 
            // _statusBar
            // 
            this._statusBar.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this._lblStatus,
            this._progressBar});
            this._statusBar.Location = new System.Drawing.Point(0, 488);
            this._statusBar.Name = "_statusBar";
            this._statusBar.Size = new System.Drawing.Size(534, 22);
            this._statusBar.TabIndex = 0;
            // 
            // _lblStatus
            // 
            this._lblStatus.Name = "_lblStatus";
            this._lblStatus.Size = new System.Drawing.Size(519, 17);
            this._lblStatus.Spring = true;
            this._lblStatus.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // _progressBar
            // 
            this._progressBar.Name = "_progressBar";
            this._progressBar.Size = new System.Drawing.Size(100, 16);
            this._progressBar.Visible = false;
            // 
            // _tvFiles
            // 
            this._tvFiles.Dock = System.Windows.Forms.DockStyle.Fill;
            this._tvFiles.Location = new System.Drawing.Point(0, 0);
            this._tvFiles.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this._tvFiles.Name = "_tvFiles";
            this._tvFiles.Size = new System.Drawing.Size(534, 438);
            this._tvFiles.TabIndex = 0;
            this._tvFiles.SelectionChanged += new System.EventHandler(this._tvFiles_SelectionChanged);
            // 
            // _btnExtract
            // 
            this._btnExtract.Dock = System.Windows.Forms.DockStyle.Bottom;
            this._btnExtract.Enabled = false;
            this._btnExtract.Location = new System.Drawing.Point(0, 438);
            this._btnExtract.Name = "_btnExtract";
            this._btnExtract.Size = new System.Drawing.Size(534, 50);
            this._btnExtract.TabIndex = 2;
            this._btnExtract.Text = "Extract";
            this._btnExtract.UseVisualStyleBackColor = true;
            this._btnExtract.Click += new System.EventHandler(this._btnExtract_Click);
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(534, 510);
            this.Controls.Add(this._tvFiles);
            this.Controls.Add(this._btnExtract);
            this.Controls.Add(this._statusBar);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MinimumSize = new System.Drawing.Size(550, 350);
            this.Name = "MainForm";
            this.Text = "SOTTR Extractor";
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.MainForm_FormClosing);
            this.Load += new System.EventHandler(this.MainForm_Load);
            this._statusBar.ResumeLayout(false);
            this._statusBar.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private System.Windows.Forms.StatusStrip _statusBar;
        private System.Windows.Forms.ToolStripStatusLabel _lblStatus;
        private System.Windows.Forms.ToolStripProgressBar _progressBar;
        private ArchiveFileTreeView _tvFiles;
        private System.Windows.Forms.Button _btnExtract;
    }
}

