namespace TrRebootTools.BinaryTemplateGenerator
{
    internal class CField : CDeclaration
    {
        public CField(string type, string name, int? bitLength, int[] arrayDimensions)
            : base(name)
        {
            Type = type;
            BitLength = bitLength;
            ArrayDimensions = arrayDimensions;
        }

        public string Type
        {
            get;
        }

        public int? BitLength
        {
            get;
        }

        public int[] ArrayDimensions
        {
            get;
        }

        public int TotalItemCount
        {
            get
            {
                int count = 1;
                if (ArrayDimensions != null)
                {
                    foreach (int dimension in ArrayDimensions)
                    {
                        count *= dimension;
                    }
                }
                return count;
            }
        }
    }
}
