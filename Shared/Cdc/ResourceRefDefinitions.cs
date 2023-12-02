using SottrModManager.Shared.Util;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;

namespace SottrModManager.Shared.Cdc
{
    public class ResourceRefDefinitions
    {
        public record struct InternalRef(int RefOffset, int TargetOffset);
        public record struct ExternalRef(int RefOffset, ResourceKey ResourceKey);

        public ResourceRefDefinitions(Stream stream)
        {
            if (!stream.CanSeek)
            {
                MemoryStream memStream = new MemoryStream();
                stream.CopyTo(memStream);
                memStream.Position = 0;
                stream = memStream;
            }

            BinaryReader reader = new BinaryReader(stream);
            RefCounts counts = reader.ReadStruct<RefCounts>();

            long bodyPos = GetSize(counts);

            for (int i = 0; i < counts.NumInternalRefs; i++)
            {
                int refOffset = reader.ReadInt32();
                int targetOffset = reader.ReadInt32();
                InternalRefs.Add(new InternalRef(refOffset, targetOffset));
            }

            for (int i = 0; i < counts.NumWideExternalRefs; i++)
            {
                int refOffset = reader.ReadInt32();
                ResourceType resourceType = (ResourceType)reader.ReadInt32();
                int resourceId = reader.ReadInt32();
                int resourceOffset = reader.ReadInt32();
                ExternalRefs.Add(new ExternalRef(refOffset, new ResourceKey(resourceType, resourceId)));
            }

            stream.Position += counts.NumIntPatches * 4;
            stream.Position += counts.NumShortPatches * 8;

            for (int i = 0; i < counts.NumPackedExternalRefs; i++)
            {
                int packedRef = reader.ReadInt32();
                ResourceType resourceType = (ResourceType)(packedRef >> 25);
                int refOffset = (packedRef & 0x1FFFFFF) * 4;

                long pos = stream.Position;
                stream.Position = bodyPos + refOffset;
                int resourceId = (int)(reader.ReadUInt32() & 0x7FFFFFFF);
                stream.Position = pos;

                ExternalRefs.Add(new ExternalRef(refOffset, new ResourceKey(resourceType, resourceId)));
            }
        }

        public static int ReadHeaderAndGetSize(Stream stream)
        {
            BinaryReader reader = new BinaryReader(stream);
            RefCounts counts = reader.ReadStruct<RefCounts>();
            return GetSize(counts);
        }

        private static int GetSize(in RefCounts refCounts)
        {
            return Marshal.SizeOf<RefCounts>() + refCounts.NumInternalRefs * 8 +
                                                 refCounts.NumWideExternalRefs * 16 +
                                                 refCounts.NumIntPatches * 4 +
                                                 refCounts.NumShortPatches * 8 +
                                                 refCounts.NumPackedExternalRefs * 4;
        }

        public List<InternalRef> InternalRefs
        {
            get;
        } = new();

        public List<ExternalRef> ExternalRefs
        {
            get;
        } = new();

        [StructLayout(LayoutKind.Sequential)]
        private struct RefCounts
        {
            public int NumInternalRefs;
            public int NumWideExternalRefs;
            public int NumIntPatches;
            public int NumShortPatches;
            public int NumPackedExternalRefs;
        }
    }
}
