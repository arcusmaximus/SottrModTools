using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using SottrModManager.Shared.Util;

namespace SottrModManager.Shared.Cdc
{
    public class LocalsBin
    {
        public LocalsBin()
        {
        }

        public LocalsBin(Stream stream)
        {
            byte[] data = new byte[stream.Length];
            stream.Read(data, 0, data.Length);
            int numStrings = BitConverter.ToInt32(data, 4);
            for (int i = 0; i < numStrings; i++)
            {
                int keyPos = BitConverter.ToInt32(data, 8 + 8 * i);
                if (keyPos == 0)
                    continue;

                int separatorPos = keyPos;
                while (data[separatorPos] != ' ')
                {
                    separatorPos++;
                }

                int terminatorPos = separatorPos;
                while (data[terminatorPos] != 0)
                {
                    terminatorPos++;
                }

                string key = Encoding.UTF8.GetString(data, keyPos, separatorPos - keyPos);
                string value = Encoding.UTF8.GetString(data, separatorPos + 1, terminatorPos - (separatorPos + 1));
                Strings.Add(key, value);
            }
        }

        public Dictionary<string, string> Strings
        {
            get;
        } = new();

        public void Write(Stream stream)
        {
            byte[] encodeBuffer = new byte[4096];

            BinaryWriter writer = new BinaryWriter(stream);
            writer.Write(0);
            writer.Write(Strings.Count);
            for (int i = 0; i < Strings.Count; i++)
            {
                writer.Write(0L);
            }

            int stringIdx = 0;
            foreach ((string key, string value) in Strings)
            {
                stream.Position = 8 + 8 * stringIdx;
                writer.Write(stream.Length);
                stream.Position = stream.Length;

                int keyLength = Encoding.UTF8.GetBytes(key, 0, key.Length, encodeBuffer, 0);
                writer.Write(encodeBuffer, 0, keyLength);
                writer.Write((byte)' ');

                int valueLength = Encoding.UTF8.GetBytes(value, 0, value.Length, encodeBuffer, 0);
                writer.Write(encodeBuffer, 0, valueLength);
                writer.Write((byte)0);

                stringIdx++;
            }
        }
    }
}
