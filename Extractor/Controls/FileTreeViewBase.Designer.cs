
using TrRebootTools.Extractor.Controls;


namespace TrRebootTools.Extractor.Controls
{
    partial class FileTreeViewBase
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

        #region コンポーネント デザイナーで生成されたコード

        /// <summary> 
        /// デザイナー サポートに必要なメソッドです。このメソッドの内容を 
        /// コード エディターで変更しないでください。
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(FileTreeViewBase));
            TrRebootTools.Shared.Controls.VirtualTreeView.MiscOptionHelper miscOptionHelper1 = new TrRebootTools.Shared.Controls.VirtualTreeView.MiscOptionHelper();
            TrRebootTools.Shared.Controls.VirtualTreeView.PaintOptionHelper paintOptionHelper1 = new TrRebootTools.Shared.Controls.VirtualTreeView.PaintOptionHelper();
            this._tvFiles = new TrRebootTools.Shared.Controls.VirtualTreeView.VirtualTreeView();
            this._pnlSearch = new System.Windows.Forms.TableLayoutPanel();
            this._txtSearch = new System.Windows.Forms.TextBox();
            this._pbSearch = new System.Windows.Forms.PictureBox();
            this._pnlSearch.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this._pbSearch)).BeginInit();
            this.SuspendLayout();
            // 
            // _tvFiles
            // 
            this._tvFiles.Back2Color = System.Drawing.Color.FromArgb(((int)(((byte)(229)))), ((int)(((byte)(229)))), ((int)(((byte)(229)))));
            this._tvFiles.BackColor = System.Drawing.SystemColors.Window;
            this._tvFiles.ButtonStyle = TrRebootTools.Shared.Controls.VirtualTreeView.ButtonStyle.bsRectangle;
            this._tvFiles.Dock = System.Windows.Forms.DockStyle.Fill;
            this._tvFiles.Header.BackColor = System.Drawing.SystemColors.Window;
            this._tvFiles.Header.Columns = ((System.Collections.Generic.List<TrRebootTools.Shared.Controls.VirtualTreeView.VirtualTreeColumn>)(resources.GetObject("resource.Columns")));
            this._tvFiles.Header.Font = new System.Drawing.Font("Tahoma", 8F);
            this._tvFiles.Header.ForeColor = System.Drawing.Color.Black;
            this._tvFiles.Header.Height = 1;
            this._tvFiles.Header.Visible = true;
            this._tvFiles.LineColor = System.Drawing.Color.Silver;
            this._tvFiles.LineWidth = 1F;
            this._tvFiles.Location = new System.Drawing.Point(0, 33);
            this._tvFiles.Name = "_tvFiles";
            miscOptionHelper1.Editable = false;
            miscOptionHelper1.MultiSelect = true;
            this._tvFiles.Options.Misc = miscOptionHelper1;
            paintOptionHelper1.Back2Color = false;
            paintOptionHelper1.FullVertGridLines = false;
            paintOptionHelper1.ShowButtons = true;
            paintOptionHelper1.ShowHorzGridLines = false;
            this._tvFiles.Options.Paint = paintOptionHelper1;
            this._tvFiles.ShowHint = true;
            this._tvFiles.Size = new System.Drawing.Size(336, 119);
            this._tvFiles.TabIndex = 1;
            // 
            // _pnlSearch
            // 
            this._pnlSearch.ColumnCount = 2;
            this._pnlSearch.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 30F));
            this._pnlSearch.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
            this._pnlSearch.Controls.Add(this._txtSearch, 1, 0);
            this._pnlSearch.Controls.Add(this._pbSearch, 0, 0);
            this._pnlSearch.Dock = System.Windows.Forms.DockStyle.Top;
            this._pnlSearch.Location = new System.Drawing.Point(0, 0);
            this._pnlSearch.Name = "_pnlSearch";
            this._pnlSearch.RowCount = 1;
            this._pnlSearch.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this._pnlSearch.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 33F));
            this._pnlSearch.Size = new System.Drawing.Size(336, 33);
            this._pnlSearch.TabIndex = 0;
            // 
            // _txtSearch
            // 
            this._txtSearch.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Left | System.Windows.Forms.AnchorStyles.Right)));
            this._txtSearch.Location = new System.Drawing.Point(33, 7);
            this._txtSearch.Name = "_txtSearch";
            this._txtSearch.Size = new System.Drawing.Size(300, 19);
            this._txtSearch.TabIndex = 0;
            // 
            // _pbSearch
            // 
            this._pbSearch.Dock = System.Windows.Forms.DockStyle.Fill;
            this._pbSearch.Image = global::TrRebootTools.Extractor.Properties.Resources.Search;
            this._pbSearch.Location = new System.Drawing.Point(3, 3);
            this._pbSearch.Name = "_pbSearch";
            this._pbSearch.Size = new System.Drawing.Size(24, 27);
            this._pbSearch.SizeMode = System.Windows.Forms.PictureBoxSizeMode.CenterImage;
            this._pbSearch.TabIndex = 1;
            this._pbSearch.TabStop = false;
            // 
            // FileTreeViewBase
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this._tvFiles);
            this.Controls.Add(this._pnlSearch);
            this.Name = "FileTreeViewBase";
            this.Size = new System.Drawing.Size(336, 152);
            this._pnlSearch.ResumeLayout(false);
            this._pnlSearch.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this._pbSearch)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        protected TrRebootTools.Shared.Controls.VirtualTreeView.VirtualTreeView _tvFiles;
        private System.Windows.Forms.TableLayoutPanel _pnlSearch;
        protected System.Windows.Forms.TextBox _txtSearch;
        private System.Windows.Forms.PictureBox _pbSearch;
    }
}
