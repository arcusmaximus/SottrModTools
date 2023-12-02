using System.Collections.Generic;
using System.IO;
using System.Reflection;
using SottrModManager.Shared.Util;

namespace SottrModManager.Shared.Cdc
{
    public static class CdcHash
    {
        private static readonly Dictionary<ulong, string> LookupTable = new();

        static CdcHash()
        {
            string exeFolderPath = Path.GetDirectoryName(Assembly.GetEntryAssembly().Location);
            foreach (string filePath in Directory.EnumerateFiles(exeFolderPath, "*.list"))
            {
                using StreamReader reader = new StreamReader(filePath);
                string line;
                while ((line = reader.ReadLine()) != null)
                {
                    LookupTable[Calculate(line)] = line;
                }
            }
        }

        public static ulong Calculate(string str)
        {
            ulong dwHash = 0xCBF29CE484222325;
            foreach (char c in str)
            {
                dwHash = (dwHash ^ c) * 0x100000001B3;
            }
            return dwHash;
        }

        public static string Lookup(ulong hash)
        {
            return LookupTable.GetOrDefault(hash);
        }

        public static IEnumerable<ulong> Hashes => LookupTable.Keys;
    }
}
