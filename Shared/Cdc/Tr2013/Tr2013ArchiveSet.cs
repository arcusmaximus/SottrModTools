using System.Collections.Generic;
using System.Linq;

namespace TrRebootTools.Shared.Cdc.Tr2013
{
    internal class Tr2013ArchiveSet : ArchiveSet
    {
        private const int Patch2ArchiveId = 67;
        private const string Patch2ArchiveName = "patch2.000.tiger";

        private const int Patch3ArchiveId = 69;

        public Tr2013ArchiveSet(string folderPath, bool includeGame, bool includeMods)
            : base(folderPath, includeGame, includeMods)
        {
        }

        public override CdcGame Game => CdcGame.Tr2013;

        protected override bool SupportsMetaData => false;

        protected override bool RequiresSpecMaskFiles => false;

        public override List<Archive> GetSortedArchives()
        {
            return Archives.Where(a => a.Id <= Patch2ArchiveId)
                           .OrderBy(a => a.Id)
                           .Concat(base.GetSortedArchives())
                           .ToList();
        }

        public override void GetFlattenedModArchiveDetails(out int archiveId, out string archiveFileName)
        {
            archiveId = Patch2ArchiveId;
            archiveFileName = Patch2ArchiveName;
        }

        protected override string MakeLocaleSuffix(ulong locale)
        {
            string language = CdcGameInfo.Get(Game).LocaleToLanguageName(locale);
            return language != null ? "_" + language : "";
        }
    }
}
