using SottrModManager.Shared.Util;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;

namespace SottrModManager.Shared.Cdc
{
    public class WwiseSoundBank
    {
        private delegate Section SectionFactory(string tag, int length, BinaryReader reader);

        private static readonly Dictionary<string, SectionFactory> SectionFactories =
            new Dictionary<string, SectionFactory>
            {
                { "DIDX", (tag, length, reader) => new DataIndexSection(tag, length, reader) }
            };

        private static SectionFactory DefaultSectionFactory = (tag, length, reader) => new UnknownSection(tag, length, reader);

        public WwiseSoundBank(Stream stream)
        {
            BinaryReader reader = new BinaryReader(stream);
            Id = reader.ReadInt32();
            int bankLength = reader.ReadInt32();

            int position = 0;
            while (position < bankLength)
            {
                string sectionTag = Encoding.ASCII.GetString(reader.ReadBytes(4));
                int sectionLength = reader.ReadInt32();

                SectionFactory factory = SectionFactories.GetOrDefault(sectionTag) ?? DefaultSectionFactory;
                Section section = factory(sectionTag, sectionLength, reader);
                Sections.Add(section);

                position += 8 + sectionLength;
            }
        }

        public int Id
        {
            get;
        }

        public List<Section> Sections
        {
            get;
        } = new();

        public T GetSection<T>()
            where T : Section
        {
            return Sections.OfType<T>().FirstOrDefault();
        }

        public void Write(Stream stream)
        {
            BinaryWriter writer = new BinaryWriter(stream);
            writer.Write(Id);
            writer.Write(0);
            foreach (Section section in Sections)
            {
                int sectionOffset = (int)stream.Position;
                writer.Write(Encoding.ASCII.GetBytes(section.Tag));
                writer.Write(0);
                section.Write(writer);
                int sectionLength = (int)stream.Position - sectionOffset - 8;

                stream.Position = sectionOffset + 4;
                writer.Write(sectionLength);
                stream.Position = stream.Length;
            }

            stream.Position = 4;
            writer.Write((int)stream.Length - 8);

            stream.Position = stream.Length;
        }

        public abstract class Section
        {
            public Section(string tag)
            {
                Tag = tag;
            }

            public string Tag
            {
                get;
            }

            public abstract void Write(BinaryWriter writer);

            public override string ToString() => Tag;
        }

        public class DataIndexSection : Section
        {
            public DataIndexSection(string tag, int length, BinaryReader reader)
                : base(tag)
            {
                int numEntries = length / 0xC;
                Entries = new List<DataIndexEntry>(numEntries);
                for (int i = 0; i < numEntries; i++)
                {
                    Entries.Add(reader.ReadStruct<DataIndexEntry>());
                }
            }

            public List<DataIndexEntry> Entries
            {
                get;
            }

            public override void Write(BinaryWriter writer)
            {
                foreach (DataIndexEntry entry in Entries)
                {
                    writer.WriteStruct(entry);
                }
            }
        }

        public class UnknownSection : Section
        {
            public UnknownSection(string tag, int length, BinaryReader reader)
                : base(tag)
            {
                Data = reader.ReadBytes(length);
            }

            public byte[] Data
            {
                get;
            }

            public override void Write(BinaryWriter writer)
            {
                writer.Write(Data);
            }
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct DataIndexEntry
        {
            public int SoundId;
            public int Offset;
            public int Length;
        }
    }
}
