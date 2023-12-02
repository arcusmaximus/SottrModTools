using SottrModManager.Shared.Util;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;

namespace SottrModManager.Shared.Cdc
{
    public class ResourceCollection
    {
        private ResourceCollectionHeader _header;
        private byte[] _name;
        private readonly List<ResourceIdentification> _resourceIdentifications = new();
        private readonly List<ResourceCollectionDependency> _dependencies = new();
        private readonly List<ResourceLocation> _resourceLocations = new();
        private List<ResourceReference> _resourceReferences;

        public ResourceCollection(ulong nameHash, ulong locale, Stream stream)
        {
            NameHash = nameHash;
            Locale = locale;

            BinaryReader reader = new BinaryReader(stream);
            _header = reader.ReadStruct<ResourceCollectionHeader>();
            if (_header.Version != 23)
                throw new NotSupportedException("Only version 23 .drm files are supported");

            for (int i = 0; i < _header.NumResources; i++)
            {
                _resourceIdentifications.Add(reader.ReadStruct<ResourceIdentification>());
            }

            _name = reader.ReadBytes(_header.NameLength);

            long dependenciesStart = stream.Position;
            while (stream.Position < dependenciesStart + _header.DependenciesLength)
            {
                ulong dependencyLocale = reader.ReadUInt64();
                string dependencyFilePath = reader.ReadZeroTerminatedString();
                _dependencies.Add(new ResourceCollectionDependency(dependencyFilePath, dependencyLocale));
            }

            for (int i = 0; i < _header.NumResources; i++)
            {
                _resourceLocations.Add(reader.ReadStruct<ResourceLocation>());
            }
        }

        public ulong NameHash
        {
            get;
        }

        public ulong Locale
        {
            get;
        }

        public IEnumerable<ResourceCollectionDependency> Dependencies
        {
            get
            {
                foreach (ResourceCollectionDependency dependency in _dependencies)
                {
                    string filePath = "pcx64-w\\" + dependency.FilePath;
                    if (!filePath.Contains('.'))
                        filePath += ".drm";

                    yield return new ResourceCollectionDependency(filePath, dependency.Locale);
                }
            }
        }

        public IReadOnlyList<ResourceReference> ResourceReferences
        {
            get
            {
                if (_resourceReferences == null)
                {
                    _resourceReferences = new List<ResourceReference>();
                    for (int i = 0; i < _resourceIdentifications.Count; i++)
                    {
                        ResourceIdentification identification = _resourceIdentifications[i];
                        ResourceLocation location = _resourceLocations[i];
                        _resourceReferences.Add(
                            new ResourceReference(
                                identification.Id,
                                (ResourceType)identification.Type,
                                (ResourceSubType)identification.SubType,
                                location.ArchiveId,
                                location.ArchiveSubId,
                                location.ArchivePart,
                                location.OffsetInArchive,
                                location.SizeInArchive,
                                location.OffsetInBatch,
                                identification.RefDefinitionsSize,
                                identification.BodySize
                            )
                        );
                    }
                }
                return _resourceReferences;
            }
        }

        public int AddResourceReference(ResourceCollection otherCollection, int otherResourceId)
        {
            int resourceIdx = _resourceIdentifications.Count;
            _resourceIdentifications.Add(otherCollection._resourceIdentifications[otherResourceId]);
            _resourceLocations.Add(otherCollection._resourceLocations[otherResourceId]);
            _resourceReferences = null;
            return resourceIdx;
        }

        public void UpdateResourceReference(int resourceIdx, ResourceReference resourceRef)
        {
            ResourceIdentification identification = _resourceIdentifications[resourceIdx];
            if (resourceRef.RefDefinitionsSize != null)
            {
                identification.RefDefinitionsSize = resourceRef.RefDefinitionsSize.Value;
                identification.BodySize = resourceRef.BodySize;
            }
            else
            {
                identification.BodySize = resourceRef.BodySize - identification.RefDefinitionsSize;
            }
            _resourceIdentifications[resourceIdx] = identification;

            ResourceLocation location = _resourceLocations[resourceIdx];
            location.ArchiveId = (byte)resourceRef.ArchiveId;
            location.ArchiveSubId = (byte)resourceRef.ArchiveSubId;
            location.ArchivePart = (short)resourceRef.ArchivePart;
            location.OffsetInArchive = resourceRef.Offset;
            location.SizeInArchive = resourceRef.Length;
            location.OffsetInBatch = resourceRef.OffsetInBatch;
            _resourceLocations[resourceIdx] = location;

            if (_resourceReferences != null)
                _resourceReferences[resourceIdx] = resourceRef;
        }

        public void Write(Stream stream)
        {
            BinaryWriter writer = new BinaryWriter(stream);

            _header.NumResources = _resourceIdentifications.Count;
            _header.NameLength = _name.Length;
            _header.DependenciesLength = _dependencies.Sum(d => 8 + d.FilePath.Length + 1);
            writer.WriteStruct(ref _header);

            for (int i = 0; i < _header.NumResources; i++)
            {
                ResourceIdentification identification = _resourceIdentifications[i];
                writer.WriteStruct(ref identification);
            }

            writer.Write(_name);

            foreach (ResourceCollectionDependency dependency in _dependencies)
            {
                writer.Write(dependency.Locale);
                writer.WriteZeroTerminatedString(dependency.FilePath);
            }

            for (int i = 0; i < _header.NumResources; i++)
            {
                ResourceLocation location = _resourceLocations[i];
                writer.WriteStruct(ref location);
            }
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct ResourceCollectionHeader
        {
            public int Version;
            public int DependenciesLength;
            public int NameLength;
            public int PaddingLength;
            public int Size;
            public int Flags;
            public int NumResources;
            public int Primary;
            public ulong Locale;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct ResourceIdentification
        {
            public int BodySize;
            public byte Type;
            public byte Flags;
            public short Padding;
            public int SubTypeAndRefDefinitionsSize;
            public int Id;
            public ulong Locale;

            public int SubType
            {
                get { return (SubTypeAndRefDefinitionsSize & 0xFF) >> 1; }
                set { SubTypeAndRefDefinitionsSize = (SubTypeAndRefDefinitionsSize & 0x7FFFFF01) | (value << 1); }
            }

            public int RefDefinitionsSize
            {
                get { return SubTypeAndRefDefinitionsSize >> 8; }
                set { SubTypeAndRefDefinitionsSize = (SubTypeAndRefDefinitionsSize & 0xFF) | (value << 8); }
            }
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct ResourceLocation
        {
            public int Unknown1;
            public int Unknown2;
            public short ArchivePart;
            public byte ArchiveId;
            public byte ArchiveSubId;
            public int OffsetInArchive;
            public int SizeInArchive;
            public int OffsetInBatch;
        }
    }
}
