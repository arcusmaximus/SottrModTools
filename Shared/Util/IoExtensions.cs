using System;
using System.IO;
using System.Runtime.CompilerServices;
using System.Text;

namespace TrRebootTools.Shared.Util
{
    public static class IoExtensions
    {
        private static readonly byte[] TempBuffer = new byte[0x400];

        public static string ReadZeroTerminatedString(this BinaryReader reader)
        {
            int length = 0;
            while (reader.BaseStream.Position < reader.BaseStream.Length)
            {
                byte b = reader.ReadByte();
                if (b == 0)
                    break;

                TempBuffer[length++] = b;
            }
            return Encoding.UTF8.GetString(TempBuffer, 0, length);
        }

        public static void WriteZeroTerminatedString(this BinaryWriter writer, string text)
        {
            int length = Encoding.UTF8.GetBytes(text, 0, text.Length, TempBuffer, 0);
            TempBuffer[length++] = 0;
            writer.Write(TempBuffer, 0, length);
        }

        public static void Align(this BinaryReader reader, int alignment)
        {
            if (alignment <= 1)
                return;

            while (reader.BaseStream.Position % alignment != 0)
            {
                reader.ReadByte();
            }
        }

        public static void Align(this BinaryWriter writer, int alignment)
        {
            if (alignment <= 1)
                return;

            while (writer.BaseStream.Position % alignment != 0)
            {
                writer.Write((byte)0);
            }
        }

        public static unsafe T ReadStruct<T>(this BinaryReader reader)
            where T : unmanaged
        {
            reader.BaseStream.Read(TempBuffer, 0, Unsafe.SizeOf<T>());
            fixed (byte* pBuffer = TempBuffer)
            {
                return Unsafe.Read<T>(pBuffer);
            }
        }

        public static unsafe void WriteStruct<T>(this BinaryWriter writer, T data)
            where T : unmanaged
        {
            fixed (byte* pBuffer = TempBuffer)
            {
                Unsafe.Write(pBuffer, data);
            }
            writer.BaseStream.Write(TempBuffer, 0, Unsafe.SizeOf<T>());
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

        public static ArraySegment<byte> GetContent(this Stream stream)
        {
            if (stream is MemoryStream memStream && memStream.TryGetBuffer(out ArraySegment<byte> buffer))
                return buffer;

            stream.Position = 0;
            byte[] data = new byte[stream.Length];
            stream.Read(data, 0, data.Length);
            stream.Position = 0;
            return new ArraySegment<byte>(data);
        }
    }
}
