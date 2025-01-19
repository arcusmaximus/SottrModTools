// Taken from https://github.com/dk76/VirtualTreeView

using System;
using System.Drawing;
using System.ComponentModel;
using System.Runtime.Serialization;
using System.Security.Permissions;
using System.Reflection;

namespace TrRebootTools.Shared.Controls.VirtualTreeView
{
    [Browsable(true)]
    [Serializable]
    [TypeConverter(typeof(ExpandableObjectConverter))]
    public class VirtualTreeColumn : ISerializable
    {

        private string FName = "Column";
        private int FWidth = 50;
        private StringAlignment FLineAlignment = StringAlignment.Center;
        private StringAlignment FAlignment = StringAlignment.Near;
        private StringAlignment FCaptionLineAlignment = StringAlignment.Center;
        private StringAlignment FCaptionAlignment = StringAlignment.Near;

        [Category("Behavior")]
        public string Name { get { return FName; } set { FName = value; } }
        [Category("Behavior")]
        public int Width { get { return FWidth; } set { FWidth = value; } }

        [Category("Alignment")]
        public StringAlignment LineAlignment { get => FLineAlignment; set => FLineAlignment = value; }

        [Category("Alignment")]
        public StringAlignment Alignment { get => FAlignment; set => FAlignment = value; }

        [Category("Alignment")]
        public StringAlignment CaptionLineAlignment { get => FCaptionLineAlignment; set => FCaptionLineAlignment = value; }

        [Category("Alignment")]
        public StringAlignment CaptionAlignment { get => FCaptionAlignment; set => FCaptionAlignment = value; }


        internal FieldInfo fieldInfo = null;

        public VirtualTreeColumn()
        {


        }

        public VirtualTreeColumn(FieldInfo fi)
        {
            fieldInfo = fi;

        }


        public void SetFieldInfo(FieldInfo fi)
        {
            fieldInfo = fi;
        }

        protected VirtualTreeColumn(
        SerializationInfo info, StreamingContext context)
        {
            Name = info.GetString("Name");
            Width = info.GetInt32("Width");
            LineAlignment = (StringAlignment)info.GetInt32("LineAlignment");
            Alignment = (StringAlignment)info.GetInt32("Alignment");
            CaptionLineAlignment = (StringAlignment)info.GetInt32("CaptionLineAlignment");
            CaptionAlignment = (StringAlignment)info.GetInt32("CaptionAlignment");
        }



        public virtual void GetObjectData(
        SerializationInfo info, StreamingContext context)
        {
            info.AddValue("Name", Name);
            info.AddValue("Width", Width);
            info.AddValue("LineAlignment", (int)LineAlignment);
            info.AddValue("Alignment", (int)Alignment);
            info.AddValue("CaptionLineAlignment", (int)CaptionLineAlignment);
            info.AddValue("CaptionAlignment", (int)CaptionAlignment);



        }


    }
}
