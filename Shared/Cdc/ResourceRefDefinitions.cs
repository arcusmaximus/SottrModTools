using SottrModManager.Shared.Util;
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;

namespace SottrModManager.Shared.Cdc
{
    public class ResourceRefDefinitions
    {
        public record struct InternalRef(int RefPosition, int TargetPosition);
        public record struct ExternalRef(int RefPosition, ResourceKey ResourceKey);

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

        private readonly Stream _stream;
        private readonly BinaryReader _reader;
        private readonly BinaryWriter _writer;

        private readonly Dictionary<int, int> _internalRefDefinitionPosByRefPos = new();
        private readonly Dictionary<int, int> _packedExternalRefDefinitionPosByRefPos = new();

        public ResourceRefDefinitions(Stream stream)
        {
            if (!stream.CanSeek)
                throw new ArgumentException("Stream must be seekable", nameof(stream));

            _stream = stream;
            _reader = new BinaryReader(stream);
            if (stream.CanWrite)
                _writer = new BinaryWriter(stream);

            RefCounts counts = _reader.ReadStruct<RefCounts>();

            Size = GetSize(counts);

            for (int i = 0; i < counts.NumInternalRefs; i++)
            {
                int refDefinitionPos = (int)stream.Position;
                int refOffset = _reader.ReadInt32();
                int targetOffset = _reader.ReadInt32();
                _internalRefDefinitionPosByRefPos[Size + refOffset] = refDefinitionPos;
            }

            for (int i = 0; i < counts.NumWideExternalRefs; i++)
            {
                int refOffset = _reader.ReadInt32();
                ResourceType resourceType = (ResourceType)_reader.ReadInt32();
                int resourceId = _reader.ReadInt32();
                int resourceOffset = _reader.ReadInt32();
            }

            stream.Position += counts.NumIntPatches * 4;
            stream.Position += counts.NumShortPatches * 8;

            for (int i = 0; i < counts.NumPackedExternalRefs; i++)
            {
                int refDefinitionPos = (int)stream.Position;
                int packedRef = _reader.ReadInt32();
                int refOffset = (packedRef & 0x1FFFFFF) * 4;
                _packedExternalRefDefinitionPosByRefPos[Size + refOffset] = refDefinitionPos;
            }
        }

        public int Size
        {
            get;
        }

        public IEnumerable<InternalRef> InternalRefs
        {
            get
            {
                foreach (int refPos in _internalRefDefinitionPosByRefPos.Keys)
                {
                    int targetPos = GetInternalRefTarget(refPos);
                    yield return new InternalRef(refPos, targetPos);
                }
            }
        }

        public int GetInternalRefTarget(int refPos)
        {
            _stream.Position = _internalRefDefinitionPosByRefPos[refPos] + 4;
            return Size + _reader.ReadInt32();
        }

        public void SetInternalRefTarget(int refPos, int targetPos)
        {
            int refDefinitionPos = _internalRefDefinitionPosByRefPos[refPos];
            _stream.Position = refDefinitionPos + 4;
            _writer.Write(targetPos - Size);
        }

        public IEnumerable<ExternalRef> ExternalRefs
        {
            get
            {
                foreach (int refPos in _packedExternalRefDefinitionPosByRefPos.Keys)
                {
                    ResourceKey resourceKey = GetExternalRefTarget(refPos);
                    yield return new ExternalRef(refPos, resourceKey);
                }
            }
        }

        public ResourceKey GetExternalRefTarget(int refPos)
        {
            long prevPos = _stream.Position;

            _stream.Position = _packedExternalRefDefinitionPosByRefPos[refPos];
            int packedRef = _reader.ReadInt32();
            ResourceType resourceType = (ResourceType)(packedRef >> 25);

            _stream.Position = refPos;
            int resourceId = (int)(_reader.ReadUInt32() & 0x7FFFFFFF);

            _stream.Position = prevPos;

            return new ResourceKey(resourceType, resourceId);
        }

        public void SetExternalRefTarget(int refPos, ResourceKey resourceKey)
        {
            if (!_packedExternalRefDefinitionPosByRefPos.ContainsKey(refPos))
                throw new ArgumentException();

            _stream.Position = refPos;
            _writer.Write(resourceKey.Id);
        }

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
