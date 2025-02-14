namespace TrRebootTools.BinaryTemplateGenerator
{
    internal abstract class CDeclaration
    {
        protected CDeclaration(string name)
        {
            Name = name;
        }

        public string Name
        {
            get;
        }

        public int Alignment
        {
            get;
            set;
        }

        public int Size
        {
            get;
            set;
        }

        public override string ToString() => Name;
    }
}
