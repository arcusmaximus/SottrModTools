using System.IO;
using TrRebootTools.Shared.Cdc.Tr2013;

namespace TrRebootTools.Shared.Cdc.Rise
{
    public class RiseLocalsBin : Tr2013LocalsBin
    {
        public RiseLocalsBin(Stream stream)
            : base(stream)
        {
        }

        protected override int PointerSize => 8;
    }
}
