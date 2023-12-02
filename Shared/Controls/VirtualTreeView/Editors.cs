// Taken from https://github.com/dk76/VirtualTreeView

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace SottrModManager.Shared.Controls.VirtualTreeView
{

    public interface IEditor
    {
        void setText(string s);
        string getText();
        void PrepareEdit(Rectangle r);
        Control getEdit();
        void Focus();

        VirtualTreeNode getNode();
        int getColumn();

        void setEdit(Control edit);

    }



    public class Editor : IEditor
    {

        protected string FText = "";
        protected Control FEdit = null;
        protected VirtualTreeView FTree = null;
        protected VirtualTreeNode FNode = null;
        protected int FColumn = -1;

        protected int FCntNewText = 0;


        public void setEdit(Control edit)
        {
            FEdit = edit;

            FEdit.LostFocus += FEdit_LostFocus;

        }

        private void FEdit_LostFocus(object sender, EventArgs e)
        {
            var ke = new KeyEventArgs(Keys.Return);
            if (FCntNewText == 0)
                editOnKeyUp(sender, ke);
            FCntNewText++;
        }

        public void setText(string s) { FText = s; }
        virtual public string getText() { return FText; }

        public Editor(VirtualTreeView tree, VirtualTreeNode node, int column)
        {
            FTree = tree;
            FNode = node;
            FColumn = column;

        }

        public VirtualTreeNode getNode() { return FNode; }
        public int getColumn() { return FColumn; }

        public void PrepareEdit(Rectangle r)
        {
            FEdit.Top = r.Top;
            FEdit.Left = r.Left;
            FEdit.Width = r.Width;
            FEdit.Height = r.Height;
            FEdit.KeyUp += editOnKeyUp;
        }

        public Control getEdit() { return FEdit; }
        public void Focus() { FEdit.Focus(); }


        protected void editOnKeyUp(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Return)
            {
                getEdit().LostFocus -= FEdit_LostFocus;

                VirtualTreeNode node = FNode;
                int column = FColumn;

                string s = getText();



                if (FCntNewText == 0 && FText != s)
                    FTree.NewText(node, column, s);
                FCntNewText++;
                FTree.RemoveControl(getEdit());
                FTree.EndUpdate();
                e.Handled = true;
                FEdit.KeyUp -= editOnKeyUp;



            }
            else
            if (e.KeyCode == Keys.Escape)
            {

                getEdit().LostFocus -= FEdit_LostFocus;

                FTree.RemoveControl(getEdit());


                FTree.EndUpdate();
                FTree.ReDrawTree();
                e.Handled = true;
            }

        }

    }


    public class TextEditor : Editor, IEditor
    {

        public TextEditor(VirtualTreeView tree, VirtualTreeNode node, int column) : base(tree, node, column)
        {

            var edit = new TextBox();
            setEdit(edit);

        }




        public new void setText(string s)
        {
            FText = s;
            (FEdit as TextBox).Text = s;
        }

        public override string getText() { return (FEdit as TextBox).Text; }
    }


    public class DateEditor : Editor, IEditor
    {

        public DateEditor(VirtualTreeView tree, VirtualTreeNode node, int column) : base(tree, node, column)
        {

            var edit = new DateTimePicker();
            setEdit(edit);

        }

        public new void setText(string s)
        {
            FText = s;

            DateTime dt;
            if (DateTime.TryParse(FText, out dt))
            {
                (FEdit as DateTimePicker).Value = dt;

            }


        }
        override public string getText()
        {
            return (FEdit as DateTimePicker).Value.ToString("dd.MM.YY");
        }


    }




}
