using System;

namespace TrRebootTools.BinaryTemplateGenerator
{
    internal class CPrimitive : CType
    {
        public CPrimitive(string name, int size)
            : base(name, Array.Empty<string>())
        {
            Alignment = size;
            Size = size;
        }
    }
}
