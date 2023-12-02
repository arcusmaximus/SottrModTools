namespace SottrModManager.Shared.Cdc
{
    public class ResourceReference : ArchiveBlobReference
    {
        public ResourceReference(
            int resourceId,
            ResourceType type,
            ResourceSubType subType,
            int archiveId,
            int archiveSubId,
            int archivePart,
            int offsetInArchive,
            int sizeInArchive,
            int offsetInBatch,
            int? refDefinitionsSize,
            int bodySize)
            : base(archiveId, archiveSubId, archivePart, offsetInArchive, sizeInArchive)
        {
            Id = resourceId;
            Type = type;
            SubType = subType;
            OffsetInBatch = offsetInBatch;
            RefDefinitionsSize = refDefinitionsSize;
            BodySize = bodySize;
        }

        public int Id
        {
            get;
        }

        public ResourceType Type
        {
            get;
        }

        public ResourceSubType SubType
        {
            get;
        }

        public int OffsetInBatch
        {
            get;
        }

        public int? RefDefinitionsSize
        {
            get;
        }

        public int BodySize
        {
            get;
        }

        public override string ToString()
        {
            return $"{Type}:{Id} -> Archive {ArchiveId}:{ArchiveSubId}:{ArchivePart}, Offset {Offset:X}, OffsetInBatch {OffsetInBatch:X}";
        }

        public static implicit operator ResourceKey(ResourceReference resourceRef)
        {
            return new ResourceKey(resourceRef.Type, resourceRef.SubType, resourceRef.Id);
        }
    }
}
