namespace SottrExtractor.LogHook
{
    partial class LogForm
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(LogForm));
            SottrModManager.Shared.Controls.VirtualTreeView.MiscOptionHelper miscOptionHelper1 = new SottrModManager.Shared.Controls.VirtualTreeView.MiscOptionHelper();
            SottrModManager.Shared.Controls.VirtualTreeView.PaintOptionHelper paintOptionHelper1 = new SottrModManager.Shared.Controls.VirtualTreeView.PaintOptionHelper();
            SottrModManager.Shared.Controls.VirtualTreeView.MiscOptionHelper miscOptionHelper2 = new SottrModManager.Shared.Controls.VirtualTreeView.MiscOptionHelper();
            SottrModManager.Shared.Controls.VirtualTreeView.PaintOptionHelper paintOptionHelper2 = new SottrModManager.Shared.Controls.VirtualTreeView.PaintOptionHelper();
            this._tcMain = new System.Windows.Forms.TabControl();
            this._tpFiles = new System.Windows.Forms.TabPage();
            this._tvFiles = new SottrExtractor.LogHook.LogListView();
            this._tpAnimations = new System.Windows.Forms.TabPage();
            this._tvAnimations = new SottrExtractor.LogHook.LogListView();
            this._toolStrip = new System.Windows.Forms.ToolStrip();
            this._btnEnableLogging = new System.Windows.Forms.ToolStripButton();
            this._btnClearLists = new System.Windows.Forms.ToolStripButton();
            this._btnExtract = new System.Windows.Forms.Button();
            this._tcMain.SuspendLayout();
            this._tpFiles.SuspendLayout();
            this._tpAnimations.SuspendLayout();
            this._toolStrip.SuspendLayout();
            this.SuspendLayout();
            // 
            // _tcMain
            // 
            this._tcMain.Controls.Add(this._tpFiles);
            this._tcMain.Controls.Add(this._tpAnimations);
            this._tcMain.Dock = System.Windows.Forms.DockStyle.Fill;
            this._tcMain.Location = new System.Drawing.Point(0, 25);
            this._tcMain.Margin = new System.Windows.Forms.Padding(4);
            this._tcMain.Name = "_tcMain";
            this._tcMain.SelectedIndex = 0;
            this._tcMain.Size = new System.Drawing.Size(869, 399);
            this._tcMain.TabIndex = 0;
            this._tcMain.SelectedIndexChanged += new System.EventHandler(this._tcMain_SelectedIndexChanged);
            // 
            // _tpFiles
            // 
            this._tpFiles.Controls.Add(this._tvFiles);
            this._tpFiles.Location = new System.Drawing.Point(4, 24);
            this._tpFiles.Margin = new System.Windows.Forms.Padding(4);
            this._tpFiles.Name = "_tpFiles";
            this._tpFiles.Padding = new System.Windows.Forms.Padding(4);
            this._tpFiles.Size = new System.Drawing.Size(861, 371);
            this._tpFiles.TabIndex = 0;
            this._tpFiles.Text = "Files";
            this._tpFiles.UseVisualStyleBackColor = true;
            // 
            // _tvFiles
            // 
            this._tvFiles.Back2Color = System.Drawing.Color.FromArgb(((int)(((byte)(229)))), ((int)(((byte)(229)))), ((int)(((byte)(229)))));
            this._tvFiles.BackColor = System.Drawing.SystemColors.Window;
            this._tvFiles.ButtonStyle = SottrModManager.Shared.Controls.VirtualTreeView.ButtonStyle.bsRectangle;
            this._tvFiles.Dock = System.Windows.Forms.DockStyle.Fill;
            this._tvFiles.Header.BackColor = System.Drawing.SystemColors.ButtonFace;
            this._tvFiles.Header.Columns = ((System.Collections.Generic.List<SottrModManager.Shared.Controls.VirtualTreeView.VirtualTreeColumn>)(resources.GetObject("resource.Columns")));
            this._tvFiles.Header.Font = new System.Drawing.Font("Tahoma", 8F);
            this._tvFiles.Header.ForeColor = System.Drawing.Color.Black;
            this._tvFiles.Header.Height = 16;
            this._tvFiles.Header.Visible = true;
            this._tvFiles.LineColor = System.Drawing.Color.Silver;
            this._tvFiles.LineWidth = 1F;
            this._tvFiles.Location = new System.Drawing.Point(4, 4);
            this._tvFiles.Margin = new System.Windows.Forms.Padding(4);
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
            this._tvFiles.Size = new System.Drawing.Size(853, 363);
            this._tvFiles.TabIndex = 0;
            this._tvFiles.OnGetNodeCellText += new SottrModManager.Shared.Controls.VirtualTreeView.GetNodeCellText(this.GetFileNodeCellText);
            this._tvFiles.OnSelectionChanged += new System.EventHandler(this._tvFiles_OnSelectionChanged);
            // 
            // _tpAnimations
            // 
            this._tpAnimations.Controls.Add(this._tvAnimations);
            this._tpAnimations.Location = new System.Drawing.Point(4, 24);
            this._tpAnimations.Margin = new System.Windows.Forms.Padding(4);
            this._tpAnimations.Name = "_tpAnimations";
            this._tpAnimations.Padding = new System.Windows.Forms.Padding(4);
            this._tpAnimations.Size = new System.Drawing.Size(861, 371);
            this._tpAnimations.TabIndex = 1;
            this._tpAnimations.Text = "Animations";
            this._tpAnimations.UseVisualStyleBackColor = true;
            // 
            // _tvAnimations
            // 
            this._tvAnimations.Back2Color = System.Drawing.Color.FromArgb(((int)(((byte)(229)))), ((int)(((byte)(229)))), ((int)(((byte)(229)))));
            this._tvAnimations.BackColor = System.Drawing.SystemColors.Window;
            this._tvAnimations.ButtonStyle = SottrModManager.Shared.Controls.VirtualTreeView.ButtonStyle.bsRectangle;
            this._tvAnimations.Dock = System.Windows.Forms.DockStyle.Fill;
            this._tvAnimations.Header.BackColor = System.Drawing.SystemColors.ButtonFace;
            this._tvAnimations.Header.Columns = ((System.Collections.Generic.List<SottrModManager.Shared.Controls.VirtualTreeView.VirtualTreeColumn>)(resources.GetObject("resource.Columns1")));
            this._tvAnimations.Header.Font = new System.Drawing.Font("Tahoma", 8F);
            this._tvAnimations.Header.ForeColor = System.Drawing.Color.Black;
            this._tvAnimations.Header.Height = 16;
            this._tvAnimations.Header.Visible = true;
            this._tvAnimations.LineColor = System.Drawing.Color.Silver;
            this._tvAnimations.LineWidth = 1F;
            this._tvAnimations.Location = new System.Drawing.Point(4, 4);
            this._tvAnimations.Margin = new System.Windows.Forms.Padding(4);
            this._tvAnimations.Name = "_tvAnimations";
            miscOptionHelper2.Editable = false;
            miscOptionHelper2.MultiSelect = true;
            this._tvAnimations.Options.Misc = miscOptionHelper2;
            paintOptionHelper2.Back2Color = false;
            paintOptionHelper2.FullVertGridLines = false;
            paintOptionHelper2.ShowButtons = true;
            paintOptionHelper2.ShowHorzGridLines = false;
            this._tvAnimations.Options.Paint = paintOptionHelper2;
            this._tvAnimations.ShowHint = true;
            this._tvAnimations.Size = new System.Drawing.Size(853, 363);
            this._tvAnimations.TabIndex = 2;
            this._tvAnimations.OnGetNodeCellText += new SottrModManager.Shared.Controls.VirtualTreeView.GetNodeCellText(this.GetAnimationNodeCellText);
            this._tvAnimations.OnSelectionChanged += new System.EventHandler(this._tvAnimations_OnSelectionChanged);
            // 
            // _toolStrip
            // 
            this._toolStrip.GripStyle = System.Windows.Forms.ToolStripGripStyle.Hidden;
            this._toolStrip.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this._btnEnableLogging,
            this._btnClearLists});
            this._toolStrip.Location = new System.Drawing.Point(0, 0);
            this._toolStrip.Name = "_toolStrip";
            this._toolStrip.Size = new System.Drawing.Size(869, 25);
            this._toolStrip.TabIndex = 3;
            this._toolStrip.Text = "toolStrip1";
            // 
            // _btnEnableLogging
            // 
            this._btnEnableLogging.Checked = true;
            this._btnEnableLogging.CheckOnClick = true;
            this._btnEnableLogging.CheckState = System.Windows.Forms.CheckState.Checked;
            this._btnEnableLogging.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this._btnEnableLogging.Image = ((System.Drawing.Image)(resources.GetObject("_btnEnableLogging.Image")));
            this._btnEnableLogging.ImageTransparentColor = System.Drawing.Color.Magenta;
            this._btnEnableLogging.Name = "_btnEnableLogging";
            this._btnEnableLogging.Size = new System.Drawing.Size(23, 22);
            this._btnEnableLogging.ToolTipText = "Toggle logging";
            this._btnEnableLogging.Click += new System.EventHandler(this._btnEnableLogging_Click);
            // 
            // _btnClearLists
            // 
            this._btnClearLists.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image;
            this._btnClearLists.Image = ((System.Drawing.Image)(resources.GetObject("_btnClearLists.Image")));
            this._btnClearLists.ImageTransparentColor = System.Drawing.Color.Magenta;
            this._btnClearLists.Name = "_btnClearLists";
            this._btnClearLists.Size = new System.Drawing.Size(23, 22);
            this._btnClearLists.ToolTipText = "Clear lists";
            this._btnClearLists.Click += new System.EventHandler(this._btnClearLists_Click);
            // 
            // _btnExtract
            // 
            this._btnExtract.Dock = System.Windows.Forms.DockStyle.Bottom;
            this._btnExtract.Enabled = false;
            this._btnExtract.Location = new System.Drawing.Point(0, 424);
            this._btnExtract.Margin = new System.Windows.Forms.Padding(4);
            this._btnExtract.Name = "_btnExtract";
            this._btnExtract.Size = new System.Drawing.Size(869, 69);
            this._btnExtract.TabIndex = 4;
            this._btnExtract.Text = "Extract";
            this._btnExtract.UseVisualStyleBackColor = true;
            this._btnExtract.Click += new System.EventHandler(this._btnExtract_Click);
            // 
            // LogForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(869, 515);
            this.Controls.Add(this._tcMain);
            this.Controls.Add(this._btnExtract);
            this.Controls.Add(this._toolStrip);
            this.Margin = new System.Windows.Forms.Padding(5);
            this.MinimumSize = new System.Drawing.Size(406, 340);
            this.Name = "LogForm";
            this.ShowIcon = false;
            this.Text = "Log";
            this.Controls.SetChildIndex(this._toolStrip, 0);
            this.Controls.SetChildIndex(this._btnExtract, 0);
            this.Controls.SetChildIndex(this._tcMain, 0);
            this._tcMain.ResumeLayout(false);
            this._tpFiles.ResumeLayout(false);
            this._tpAnimations.ResumeLayout(false);
            this._toolStrip.ResumeLayout(false);
            this._toolStrip.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.TabControl _tcMain;
        private System.Windows.Forms.TabPage _tpFiles;
        private LogListView _tvFiles;
        private System.Windows.Forms.TabPage _tpAnimations;
        private LogListView _tvAnimations;
        private System.Windows.Forms.ToolStrip _toolStrip;
        private System.Windows.Forms.ToolStripButton _btnClearLists;
        private System.Windows.Forms.Button _btnExtract;
        private System.Windows.Forms.ToolStripButton _btnEnableLogging;
    }
}