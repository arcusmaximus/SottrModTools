using System;
using System.Collections.Generic;

namespace TrRebootTools.BinaryTemplateGenerator
{
    internal class CEnum : CType
    {
        public CEnum(string name, string? baseType)
            : base(name, baseType != null ? new[] { baseType } : Array.Empty<string>())
        {
        }

        public Dictionary<string, int> Values { get; } = new();
    }
}
