namespace TrRebootTools.BinaryTemplateGenerator
{
    internal abstract class CType : CDeclaration
    {
        protected CType(string name, string[] baseTypes)
            : base(name)
        {
            BaseTypes = baseTypes;
        }

        public string[] BaseTypes
        {
            get;
        }
    }
}
