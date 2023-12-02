namespace SottrModManager.Shared.Cdc
{
    public class ArchiveFileReference : ArchiveBlobReference
    {
        public ArchiveFileReference(ulong nameHash, ulong locale, int archiveId, int archiveSubId, int archivePart, int offset, int length)
            : base(archiveId, archiveSubId, archivePart, offset, length)
        {
            NameHash = nameHash;
            Locale = locale;
        }

        public ulong NameHash
        {
            get;
        }

        public ulong Locale
        {
            get;
        }

        public static implicit operator ArchiveFileIdentifier(ArchiveFileReference file)
        {
            return new ArchiveFileIdentifier(file.NameHash, file.Locale);
        }
    }
}
