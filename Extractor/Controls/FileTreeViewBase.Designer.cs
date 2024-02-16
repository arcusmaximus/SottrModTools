
namespace SottrExtractor.Controls
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
            SottrModManager.Shared.Controls.VirtualTreeView.MiscOptionHelper miscOptionHelper1 = new SottrModManager.Shared.Controls.VirtualTreeView.MiscOptionHelper();
            SottrModManager.Shared.Controls.VirtualTreeView.PaintOptionHelper paintOptionHelper1 = new SottrModManager.Shared.Controls.VirtualTreeView.PaintOptionHelper();
            _tvFiles = new SottrModManager.Shared.Controls.VirtualTreeView.VirtualTreeView();
            _pnlSearch = new System.Windows.Forms.TableLayoutPanel();
            _txtSearch = new System.Windows.Forms.TextBox();
            _pbSearch = new System.Windows.Forms.PictureBox();
            _pnlSearch.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)_pbSearch).BeginInit();
            SuspendLayout();
            // 
            // _tvFiles
            // 
            _tvFiles.Back2Color = System.Drawing.Color.FromArgb(229, 229, 229);
            _tvFiles.BackColor = System.Drawing.SystemColors.Window;
            _tvFiles.ButtonStyle = SottrModManager.Shared.Controls.VirtualTreeView.ButtonStyle.bsRectangle;
            _tvFiles.Dock = System.Windows.Forms.DockStyle.Fill;
            _tvFiles.Header.BackColor = System.Drawing.SystemColors.Window;
            _tvFiles.Header.Font = new System.Drawing.Font("Tahoma", 8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            _tvFiles.Header.ForeColor = System.Drawing.Color.Black;
            _tvFiles.Header.Height = 1;
            _tvFiles.Header.Visible = true;
            _tvFiles.LineColor = System.Drawing.Color.Silver;
            _tvFiles.LineWidth = 1F;
            _tvFiles.Location = new System.Drawing.Point(0, 41);
            _tvFiles.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            _tvFiles.Name = "_tvFiles";
            miscOptionHelper1.Editable = false;
            miscOptionHelper1.MultiSelect = true;
            _tvFiles.Options.Misc = miscOptionHelper1;
            paintOptionHelper1.Back2Color = false;
            paintOptionHelper1.FullVertGridLines = false;
            paintOptionHelper1.ShowButtons = true;
            paintOptionHelper1.ShowHorzGridLines = false;
            _tvFiles.Options.Paint = paintOptionHelper1;
            _tvFiles.ShowHint = true;
            _tvFiles.Size = new System.Drawing.Size(160, 149);
            _tvFiles.TabIndex = 1;
            // 
            // _pnlSearch
            // 
            _pnlSearch.ColumnCount = 2;
            _pnlSearch.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 35F));
            _pnlSearch.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
            _pnlSearch.Controls.Add(_txtSearch, 1, 0);
            _pnlSearch.Controls.Add(_pbSearch, 0, 0);
            _pnlSearch.Dock = System.Windows.Forms.DockStyle.Top;
            _pnlSearch.Location = new System.Drawing.Point(0, 0);
            _pnlSearch.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            _pnlSearch.Name = "_pnlSearch";
            _pnlSearch.RowCount = 1;
            _pnlSearch.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 100F));
            _pnlSearch.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 41F));
            _pnlSearch.Size = new System.Drawing.Size(160, 41);
            _pnlSearch.TabIndex = 0;
            // 
            // _txtSearch
            // 
            _txtSearch.Anchor = System.Windows.Forms.AnchorStyles.Left | System.Windows.Forms.AnchorStyles.Right;
            _txtSearch.Location = new System.Drawing.Point(39, 9);
            _txtSearch.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            _txtSearch.Name = "_txtSearch";
            _txtSearch.Size = new System.Drawing.Size(117, 23);
            _txtSearch.TabIndex = 0;
            // 
            // _pbSearch
            // 
            _pbSearch.Dock = System.Windows.Forms.DockStyle.Fill;
            _pbSearch.Image = Properties.Resources.Search;
            _pbSearch.Location = new System.Drawing.Point(4, 4);
            _pbSearch.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            _pbSearch.Name = "_pbSearch";
            _pbSearch.Size = new System.Drawing.Size(27, 33);
            _pbSearch.SizeMode = System.Windows.Forms.PictureBoxSizeMode.CenterImage;
            _pbSearch.TabIndex = 1;
            _pbSearch.TabStop = false;
            // 
            // FileTreeViewBase
            // 
            AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            Controls.Add(_tvFiles);
            Controls.Add(_pnlSearch);
            Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            Name = "FileTreeViewBase";
            Size = new System.Drawing.Size(160, 190);
            _pnlSearch.ResumeLayout(false);
            _pnlSearch.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)_pbSearch).EndInit();
            ResumeLayout(false);
        }

        #endregion

        protected SottrModManager.Shared.Controls.VirtualTreeView.VirtualTreeView _tvFiles;
        private System.Windows.Forms.TableLayoutPanel _pnlSearch;
        protected System.Windows.Forms.TextBox _txtSearch;
        private System.Windows.Forms.PictureBox _pbSearch;
    }
}
