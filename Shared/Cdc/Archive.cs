using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using SottrModManager.Shared.Util;

namespace SottrModManager.Shared.Cdc
{
    public class Archive : IDisposable
    {
        private static readonly byte[] Platform =
        {
            0x70, 0x63, 0x78, 0x36, 0x34, 0x2D, 0x77, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        };

        private const int MaxResourceChunkSize = 0x40000;

        private static readonly byte[] NonLastResourceEndMarker =
        {
            0x4E, 0x45, 0x58, 0x54, 0x10, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        };

        private static readonly byte[] LastResourceEndMarker =
        {
            0x4E, 0x45, 0x58, 0x54, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        };

        private int _numParts = 1;
        private List<Stream> _partStreams;
        private readonly List<ArchiveFileReference> _fileRefs = new List<ArchiveFileReference>();
        private int _maxFiles;

        private Archive(string baseFilePath, ArchiveMetaData metaData)
        {
            BaseFilePath = baseFilePath;
            MetaData = metaData;
        }

        public static Archive Create(string baseFilePath, ArchiveMetaData metaData, int subId, int maxFiles)
        {
            Archive archive = new Archive(baseFilePath, metaData)
                              {
                                  Id = metaData.PackageId,
                                  SubId = subId,
                                  _maxFiles = maxFiles
                              };

            Stream stream = File.Open(baseFilePath, FileMode.Create, FileAccess.ReadWrite, FileShare.ReadWrite);
            archive._partStreams = new List<Stream> { stream };

            BinaryWriter writer = new BinaryWriter(stream);
            ArchiveHeader header =
                new ArchiveHeader
                {
                    Magic = 0x53464154,
                    Version = 5,
                    NumParts = 1,
                    Id = archive.Id,
                    SubId = archive.SubId
                };
            writer.WriteStruct(ref header);
            writer.Write(Platform);

            ArchiveFileEntry fileEntry = new ArchiveFileEntry();
            for (int i = 0; i < maxFiles; i++)
            {
                writer.WriteStruct(ref fileEntry);
            }

            return archive;
        }

        public static Archive Open(string baseFilePath, ArchiveMetaData metaData)
        {
            Archive archive = new Archive(baseFilePath, metaData);

            using Stream stream = File.OpenRead(baseFilePath);
            BinaryReader reader = new BinaryReader(stream);
            
            ArchiveHeader header = reader.ReadStruct<ArchiveHeader>();
            if (header.Magic != 0x53464154)
                throw new InvalidDataException("Invalid magic in tiger file");

            if (header.Version != 5)
                throw new NotSupportedException("Only version 5 archive files are supported");

            archive._numParts = header.NumParts;
            archive._maxFiles = header.NumFiles;
            archive.Id = header.Id;
            archive.SubId = header.SubId;

            stream.Position = 0x38;
            for (int i = 0; i < header.NumFiles; i++)
            {
                ArchiveFileEntry entry = reader.ReadStruct<ArchiveFileEntry>();
                archive._fileRefs.Add(
                    new ArchiveFileReference(
                        entry.NameHash,
                        entry.Locale,
                        entry.ArchiveId,
                        entry.ArchiveSubId,
                        entry.ArchivePart,
                        entry.Offset,
                        entry.UncompressedSize
                    )
                );
            }

            return archive;
        }

        private List<Stream> PartStreams
        {
            get
            {
                if (_partStreams == null)
                {
                    _partStreams = new List<Stream>();
                    for (int i = 0; i < _numParts; i++)
                    {
                        string partFilePath = GetPartFilePath(i);
                        _partStreams.Add(File.Open(partFilePath, FileMode.Open, FileAccess.ReadWrite, FileShare.ReadWrite));
                    }
                }
                return _partStreams;
            }
        }

        public string BaseFilePath
        {
            get;
        }

        public int Id
        {
            get;
            private set;
        }

        public int SubId
        {
            get;
            private set;
        }

        public ArchiveMetaData MetaData
        {
            get;
        }

        public string ModName
        {
            get
            {
                string entry = MetaData.CustomEntries.FirstOrDefault(c => c.StartsWith("mod:"));
                return entry?.Substring("mod:".Length);
            }
        }

        public IReadOnlyCollection<ArchiveFileReference> Files => _fileRefs;

        public ResourceCollection GetResourceCollection(ArchiveFileReference file)
        {
            if (file.ArchiveId != Id || file.ArchiveSubId != SubId)
                throw new ArgumentException();

            Stream stream = PartStreams[file.ArchivePart];
            stream.Position = file.Offset;
            try
            {
                return new ResourceCollection(file.NameHash, file.Locale, stream);
            }
            catch
            {
                return null;
            }
        }

        public Stream OpenFile(ArchiveFileReference fileRef)
        {
            if (fileRef.ArchiveId != Id || fileRef.ArchiveSubId != SubId)
                throw new ArgumentException();

            return new WindowedStream(PartStreams[fileRef.ArchivePart], fileRef.Offset, fileRef.Length);
        }

        public Stream OpenResource(ResourceReference resourceRef)
        {
            if (resourceRef.ArchiveId != Id || resourceRef.ArchiveSubId != SubId)
                throw new ArgumentException();

            Stream stream = PartStreams[resourceRef.ArchivePart];
            return new ResourceReadStream(stream, resourceRef, true);
        }

        public ArchiveFileReference AddFile(ArchiveFileKey identifier, byte[] data)
        {
            return AddFile(identifier.NameHash, identifier.Locale, data);
        }

        public ArchiveFileReference AddFile(ArchiveFileKey identifier, ArraySegment<byte> data)
        {
            return AddFile(identifier.NameHash, identifier.Locale, data);
        }

        public ArchiveFileReference AddFile(ulong nameHash, ulong locale, byte[] data)
        {
            return AddFile(nameHash, locale, new ArraySegment<byte>(data));
        }

        public ArchiveFileReference AddFile(ulong nameHash, ulong locale, ArraySegment<byte> data)
        {
            if (_fileRefs.Count == _maxFiles)
                throw new InvalidOperationException("Can't add any further files");

            Stream contentStream = PartStreams.Last();
            BinaryWriter contentWriter = new BinaryWriter(contentStream);
            int offset = (int)contentStream.Length;
            contentStream.Position = offset;
            contentWriter.Write(data.Array, data.Offset, data.Count);

            Stream indexStream = PartStreams[0];
            BinaryWriter indexWriter = new BinaryWriter(indexStream);
            indexStream.Position = 0x38 + _fileRefs.Count * Marshal.SizeOf<ArchiveFileEntry>();

            ArchiveFileEntry entry =
                new ArchiveFileEntry
                {
                    NameHash = nameHash,
                    Locale = locale,
                    ArchiveId = (byte)Id,
                    ArchiveSubId = (byte)SubId,
                    ArchivePart = 0,
                    Offset = offset,
                    UncompressedSize = data.Count
                };
            indexWriter.WriteStruct(ref entry);

            ArchiveFileReference fileRef = new ArchiveFileReference(nameHash, locale, Id, SubId, 0, offset, data.Count);
            _fileRefs.Add(fileRef);
            indexStream.Position = 0xC;
            indexWriter.Write(_fileRefs.Count);

            return fileRef;
        }

        public ArchiveBlobReference AddResource(Stream contentStream)
        {
            int archivePart = PartStreams.Count - 1;
            Stream partStream = PartStreams[archivePart];
            partStream.Position = partStream.Length;

            BinaryWriter writer = new BinaryWriter(partStream);
            writer.Align16();

            partStream.Position -= 0x10;
            BinaryReader reader = new BinaryReader(partStream);
            byte[] prevMarker = reader.ReadBytes(0x10);
            if (prevMarker.SequenceEqual(LastResourceEndMarker))
            {
                partStream.Position -= 0x10;
                writer.Write(NonLastResourceEndMarker);
            }

            int resourceOffset = (int)partStream.Position;
            WriteResource(contentStream, writer);
            int resourceLength = (int)partStream.Position - resourceOffset;

            writer.Write(LastResourceEndMarker);

            return new ArchiveBlobReference(Id, SubId, archivePart, resourceOffset, resourceLength);
        }

        private void WriteResource(Stream contentStream, BinaryWriter writer)
        {
            if (contentStream is ResourceReadStream resourceStream)
            {
                Stream archivePartStream = resourceStream.ArchivePartStream;
                ResourceReference resourceRef = resourceStream.ResourceReference;
                archivePartStream.CopySegmentTo(resourceRef.Offset, resourceRef.Length, writer.BaseStream);
                return;
            }

            Stream partStream = writer.BaseStream;

            int numChunks = (int)(contentStream.Length / MaxResourceChunkSize);
            if (contentStream.Length % MaxResourceChunkSize != 0)
                numChunks++;

            writer.Write(0x4D524443);      // Magic
            writer.Write(0);               // Type
            writer.Write(numChunks);
            writer.Write(0);

            int chunkSizesOffset = (int)partStream.Position;
            for (int i = 0; i < numChunks; i++)
            {
                writer.Write(0);
                writer.Write(0);
            }
            writer.Align16();

            long remainingSize = contentStream.Length;
            byte[] uncompressedChunkData = new byte[MaxResourceChunkSize];
            for (int i = 0; i < numChunks; i++)
            {
                int uncompressedChunkSize = (int)Math.Min(remainingSize, MaxResourceChunkSize);
                contentStream.Read(uncompressedChunkData, 0, uncompressedChunkSize);

                int chunkOffset = (int)partStream.Position;
                writer.Write((byte)0x78);
                writer.Write((byte)0x9C);
                using (DeflateStream compressor = new DeflateStream(partStream, CompressionMode.Compress, true))
                {
                    compressor.Write(uncompressedChunkData, 0, uncompressedChunkSize);
                }
                writer.Write(0);
                int compressedChunkSize = (int)partStream.Position - chunkOffset;

                partStream.Position = chunkSizesOffset;
                writer.Write(uncompressedChunkSize << 8 | 0x02);
                writer.Write(compressedChunkSize);
                chunkSizesOffset += 8;

                partStream.Position = partStream.Length;
                writer.Align16();

                remainingSize -= uncompressedChunkSize;
            }
        }

        public string GetPartFilePath(int part)
        {
            return BaseFilePath.Replace(".000.tiger", $".{part:d03}.tiger");
        }

        public void CloseStreams()
        {
            if (_partStreams == null)
                return;

            foreach (Stream stream in _partStreams)
            {
                stream.Dispose();
            }
            _partStreams = null;
        }

        public void Delete()
        {
            if (SubId == 0)
            {
                File.Delete(MetaData.FilePath);
                File.Delete(SpecMasksToc.GetFilePathForArchive(BaseFilePath));
            }

            Dispose();
            for (int i = 0; i < _numParts; i++)
            {
                File.Delete(GetPartFilePath(i));
            }
        }

        public override string ToString()
        {
            return Path.GetFileName(BaseFilePath);
        }

        public void Dispose()
        {
            CloseStreams();
        }

        [StructLayout(LayoutKind.Sequential)]
        internal struct ArchiveHeader
        {
            public int Magic;
            public int Version;
            public int NumParts;
            public int NumFiles;
            public int Id;
            public int SubId;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct ArchiveFileEntry
        {
            public ulong NameHash;
            public ulong Locale;
            public int UncompressedSize;
            public int CompressedSize;
            public short ArchivePart;
            public byte ArchiveId;
            public byte ArchiveSubId;
            public int Offset;
        }
    }
}
