using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;

namespace SottrModManager.Shared.Util
{
    public static class IoExtensions
    {
        private static readonly byte[] TextBuffer = new byte[0x400];

        public static string ReadZeroTerminatedString(this BinaryReader reader)
        {
            int length = 0;
            while (reader.BaseStream.Position < reader.BaseStream.Length)
            {
                byte b = reader.ReadByte();
                if (b == 0)
                    break;

                TextBuffer[length++] = b;
            }
            return Encoding.UTF8.GetString(TextBuffer, 0, length);
        }

        public static void WriteZeroTerminatedString(this BinaryWriter writer, string text)
        {
            int length = Encoding.UTF8.GetBytes(text, TextBuffer);
            TextBuffer[length++] = 0;
            writer.Write(TextBuffer, 0, length);
        }

        public static void Align16(this BinaryReader reader)
        {
            while (reader.BaseStream.Position % 16 != 0)
            {
                reader.ReadByte();
            }
        }

        public static void Align16(this BinaryWriter writer)
        {
            while (writer.BaseStream.Position % 16 != 0)
            {
                writer.Write((byte)0);
            }
        }

        public static T ReadStruct<T>(this BinaryReader reader)
            where T : unmanaged
        {
            byte[] data = reader.ReadBytes(Marshal.SizeOf<T>());
            return MemoryMarshal.Read<T>(data);
        }

        public static void WriteStruct<T>(this BinaryWriter writer, ref T data)
            where T : unmanaged
        {
            writer.Write(MemoryMarshal.AsBytes(MemoryMarshal.CreateReadOnlySpan(ref data, 1)));
        }

        public static void CopySegmentTo(this Stream from, long offset, long length, Stream to)
        {
            byte[] buffer = new byte[0x1000];
            from.Position = offset;
            while (from.Position < offset + length)
            {
                int chunkSize = (int)Math.Min(offset + length - from.Position, buffer.Length);
                int readSize = from.Read(buffer, 0, chunkSize);
                to.Write(buffer, 0, chunkSize);
                if (readSize < chunkSize)
                    break;
            }
        }
    }
}
