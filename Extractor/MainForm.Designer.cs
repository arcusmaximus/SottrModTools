
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
            this.components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
            this._tvFiles = new SottrExtractor.Controls.ArchiveFileTreeView();
            this._btnExtract = new System.Windows.Forms.Button();
            this._pnlButtons = new System.Windows.Forms.TableLayoutPanel();
            this._btnLaunchWithLog = new System.Windows.Forms.Button();
            this._toolTip = new System.Windows.Forms.ToolTip(this.components);
            this._pnlButtons.SuspendLayout();
            this.SuspendLayout();
            // 
            // _tvFiles
            // 
            this._tvFiles.Dock = System.Windows.Forms.DockStyle.Fill;
            this._tvFiles.Location = new System.Drawing.Point(0, 0);
            this._tvFiles.Margin = new System.Windows.Forms.Padding(4);
            this._tvFiles.Name = "_tvFiles";
            this._tvFiles.Size = new System.Drawing.Size(534, 430);
            this._tvFiles.TabIndex = 0;
            this._tvFiles.SelectionChanged += new System.EventHandler(this._tvFiles_SelectionChanged);
            // 
            // _btnExtract
            // 
            this._btnExtract.Dock = System.Windows.Forms.DockStyle.Fill;
            this._btnExtract.Enabled = false;
            this._btnExtract.Location = new System.Drawing.Point(3, 3);
            this._btnExtract.Name = "_btnExtract";
            this._btnExtract.Size = new System.Drawing.Size(458, 52);
            this._btnExtract.TabIndex = 2;
            this._btnExtract.Text = "Extract";
            this._btnExtract.UseVisualStyleBackColor = true;
            this._btnExtract.Click += new System.EventHandler(this._btnExtract_Click);
            // 
            // _pnlButtons
            // 
            this._pnlButtons.ColumnCount = 2;
            this._pnlButtons.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this._pnlButtons.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 70F));
            this._pnlButtons.Controls.Add(this._btnExtract, 0, 0);
            this._pnlButtons.Controls.Add(this._btnLaunchWithLog, 1, 0);
            this._pnlButtons.Dock = System.Windows.Forms.DockStyle.Bottom;
            this._pnlButtons.Location = new System.Drawing.Point(0, 430);
            this._pnlButtons.Name = "_pnlButtons";
            this._pnlButtons.RowCount = 1;
            this._pnlButtons.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this._pnlButtons.Size = new System.Drawing.Size(534, 58);
            this._pnlButtons.TabIndex = 3;
            // 
            // _btnLaunchWithLog
            // 
            this._btnLaunchWithLog.Dock = System.Windows.Forms.DockStyle.Fill;
            this._btnLaunchWithLog.Image = ((System.Drawing.Image)(resources.GetObject("_btnLaunchWithLog.Image")));
            this._btnLaunchWithLog.Location = new System.Drawing.Point(467, 3);
            this._btnLaunchWithLog.Name = "_btnLaunchWithLog";
            this._btnLaunchWithLog.Size = new System.Drawing.Size(64, 52);
            this._btnLaunchWithLog.TabIndex = 3;
            this._toolTip.SetToolTip(this._btnLaunchWithLog, "Launch game and log files/animations");
            this._btnLaunchWithLog.UseVisualStyleBackColor = true;
            this._btnLaunchWithLog.Click += new System.EventHandler(this._btnLaunchWithLog_Click);
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(534, 510);
            this.Controls.Add(this._tvFiles);
            this.Controls.Add(this._pnlButtons);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MinimumSize = new System.Drawing.Size(550, 350);
            this.Name = "MainForm";
            this.Text = "SOTTR Extractor";
            this.Load += new System.EventHandler(this.MainForm_Load);
            this.Controls.SetChildIndex(this._pnlButtons, 0);
            this.Controls.SetChildIndex(this._tvFiles, 0);
            this._pnlButtons.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private ArchiveFileTreeView _tvFiles;
        private System.Windows.Forms.Button _btnExtract;
        private System.Windows.Forms.TableLayoutPanel _pnlButtons;
        private System.Windows.Forms.Button _btnLaunchWithLog;
        private System.Windows.Forms.ToolTip _toolTip;
    }
}

