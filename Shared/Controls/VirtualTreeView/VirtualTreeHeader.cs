// Taken from https://github.com/dk76/VirtualTreeView

using System;
using System.Collections.Generic;
using System.Windows.Forms;
using System.Drawing;
using System.ComponentModel;
using TrRebootTools.Shared.Controls.VirtualTreeView;

namespace TrRebootTools.Shared.Controls.VirtualTreeView
{
    [Browsable(true)]
    [TypeConverter(typeof(ExpandableObjectConverter))]

    public class VirtualTreeHeader
    {
        private bool FVisible = true;
        private int FHeight = 16;
        private List<VirtualTreeColumn> FColumns;
        private Color FBackColor = Color.White;
        private Color FForeColor = Color.Black;
        private Font FFont = new Font("Tahoma", 8);


        [Category("Behavior")]
        public bool Visible { get { return FVisible; } set { FVisible = value; } }
        [Category("Behavior")]
        public int Height { get { return FHeight; } set { FHeight = value; } }

        [Category("Behavior")]
        //[TypeConverter(typeof(ExpandableObjectConverter))]
        //[DesignerSerializationVisibility(DesignerSerializationVisibility.Content)]
        public List<VirtualTreeColumn> Columns { get { return FColumns; } set { FColumns = value; } }

        [Category("Layout")]
        public Color BackColor { get => FBackColor; set => FBackColor = value; }

        [Category("Layout")]
        public Color ForeColor { get => FForeColor; set => FForeColor = value; }

        [Category("Layout")]
        public Font Font { get => FFont; set => FFont = value; }



        public VirtualTreeHeader()
        {
            if (FColumns == null)
                FColumns = new List<VirtualTreeColumn>();

        }

    }
}
