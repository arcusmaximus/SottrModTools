using System.IO;

namespace TrRebootTools.Shared.Cdc.Tr2013
{
    internal class Tr2013ResourceRefDefinitions : ResourceRefDefinitions
    {
        public Tr2013ResourceRefDefinitions(ResourceReference resourceRef, Stream stream, bool readSizeOnly)
            : base(resourceRef, stream, readSizeOnly)
        {
        }

        protected override int WideExternalRefSize => 8;

        public override ResourceKey GetExternalRefTarget(int refPos)
        {
            ResourceKey resourceKey = base.GetExternalRefTarget(refPos);
            return Tr2013ResourceCollection.AdjustResourceKeyAfterRead(_resourceRef.ArchiveId, resourceKey);
        }

        public override void SetExternalRefTarget(int refPos, ResourceKey resourceKey)
        {
            resourceKey = Tr2013ResourceCollection.AdjustResourceKeyBeforeWrite(_resourceRef.ArchiveId, resourceKey);
            base.SetExternalRefTarget(refPos, resourceKey);
        }
    }
}
