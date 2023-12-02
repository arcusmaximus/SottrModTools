namespace SottrModManager
{
    partial class VariationSelectionForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            _lblIntro = new System.Windows.Forms.Label();
            _lstVariation = new System.Windows.Forms.ListBox();
            _btnOK = new System.Windows.Forms.Button();
            _btnCancel = new System.Windows.Forms.Button();
            _pbPreview = new System.Windows.Forms.PictureBox();
            _txtDescription = new System.Windows.Forms.TextBox();
            _spltDetails = new System.Windows.Forms.SplitContainer();
            ((System.ComponentModel.ISupportInitialize)_pbPreview).BeginInit();
            ((System.ComponentModel.ISupportInitialize)_spltDetails).BeginInit();
            _spltDetails.Panel1.SuspendLayout();
            _spltDetails.Panel2.SuspendLayout();
            _spltDetails.SuspendLayout();
            SuspendLayout();
            // 
            // _lblIntro
            // 
            _lblIntro.Anchor = System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left | System.Windows.Forms.AnchorStyles.Right;
            _lblIntro.Location = new System.Drawing.Point(12, 9);
            _lblIntro.Name = "_lblIntro";
            _lblIntro.Size = new System.Drawing.Size(662, 35);
            _lblIntro.TabIndex = 0;
            _lblIntro.Text = "(Intro)";
            // 
            // _lstVariation
            // 
            _lstVariation.Anchor = System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left;
            _lstVariation.FormattingEnabled = true;
            _lstVariation.IntegralHeight = false;
            _lstVariation.ItemHeight = 15;
            _lstVariation.Location = new System.Drawing.Point(12, 38);
            _lstVariation.Name = "_lstVariation";
            _lstVariation.Size = new System.Drawing.Size(216, 400);
            _lstVariation.TabIndex = 0;
            _lstVariation.SelectedIndexChanged += _lstVariation_SelectedIndexChanged;
            // 
            // _btnOK
            // 
            _btnOK.Anchor = System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right;
            _btnOK.Enabled = false;
            _btnOK.Location = new System.Drawing.Point(440, 444);
            _btnOK.Name = "_btnOK";
            _btnOK.Size = new System.Drawing.Size(114, 42);
            _btnOK.TabIndex = 2;
            _btnOK.Text = "OK";
            _btnOK.UseVisualStyleBackColor = true;
            _btnOK.Click += _btnOK_Click;
            // 
            // _btnCancel
            // 
            _btnCancel.Anchor = System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right;
            _btnCancel.Location = new System.Drawing.Point(560, 444);
            _btnCancel.Name = "_btnCancel";
            _btnCancel.Size = new System.Drawing.Size(114, 42);
            _btnCancel.TabIndex = 3;
            _btnCancel.Text = "Cancel";
            _btnCancel.UseVisualStyleBackColor = true;
            _btnCancel.Click += _btnCancel_Click;
            // 
            // _pbPreview
            // 
            _pbPreview.Dock = System.Windows.Forms.DockStyle.Fill;
            _pbPreview.Location = new System.Drawing.Point(0, 0);
            _pbPreview.Name = "_pbPreview";
            _pbPreview.Size = new System.Drawing.Size(440, 269);
            _pbPreview.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom;
            _pbPreview.TabIndex = 3;
            _pbPreview.TabStop = false;
            // 
            // _txtDescription
            // 
            _txtDescription.Dock = System.Windows.Forms.DockStyle.Fill;
            _txtDescription.Location = new System.Drawing.Point(0, 0);
            _txtDescription.Multiline = true;
            _txtDescription.Name = "_txtDescription";
            _txtDescription.ReadOnly = true;
            _txtDescription.Size = new System.Drawing.Size(440, 127);
            _txtDescription.TabIndex = 0;
            // 
            // _spltDetails
            // 
            _spltDetails.Anchor = System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left | System.Windows.Forms.AnchorStyles.Right;
            _spltDetails.FixedPanel = System.Windows.Forms.FixedPanel.Panel2;
            _spltDetails.Location = new System.Drawing.Point(234, 38);
            _spltDetails.Name = "_spltDetails";
            _spltDetails.Orientation = System.Windows.Forms.Orientation.Horizontal;
            // 
            // _spltDetails.Panel1
            // 
            _spltDetails.Panel1.Controls.Add(_pbPreview);
            // 
            // _spltDetails.Panel2
            // 
            _spltDetails.Panel2.Controls.Add(_txtDescription);
            _spltDetails.Size = new System.Drawing.Size(440, 400);
            _spltDetails.SplitterDistance = 269;
            _spltDetails.TabIndex = 1;
            // 
            // VariationSelectionForm
            // 
            AcceptButton = _btnOK;
            AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            CancelButton = _btnCancel;
            ClientSize = new System.Drawing.Size(686, 498);
            Controls.Add(_spltDetails);
            Controls.Add(_btnCancel);
            Controls.Add(_btnOK);
            Controls.Add(_lstVariation);
            Controls.Add(_lblIntro);
            MinimumSize = new System.Drawing.Size(490, 350);
            Name = "VariationSelectionForm";
            ShowIcon = false;
            Text = "Select mod variation";
            ((System.ComponentModel.ISupportInitialize)_pbPreview).EndInit();
            _spltDetails.Panel1.ResumeLayout(false);
            _spltDetails.Panel2.ResumeLayout(false);
            _spltDetails.Panel2.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)_spltDetails).EndInit();
            _spltDetails.ResumeLayout(false);
            ResumeLayout(false);
        }

        #endregion

        private System.Windows.Forms.Label _lblIntro;
        private System.Windows.Forms.ListBox _lstVariation;
        private System.Windows.Forms.Button _btnOK;
        private System.Windows.Forms.Button _btnCancel;
        private System.Windows.Forms.PictureBox _pbPreview;
        private System.Windows.Forms.TextBox _txtDescription;
        private System.Windows.Forms.SplitContainer _spltDetails;
    }
}