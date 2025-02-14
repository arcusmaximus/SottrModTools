using System;
using System.IO;
using System.Reflection;
using System.Text.RegularExpressions;

namespace TrRebootTools.BinaryTemplateGenerator
{
    public static class Program
    {
        public static void Main(string[] args)
        {
            if (!TryParseArgs(args, out string structName, out int trVersion))
            {
                string assemblyName = Assembly.GetEntryAssembly()!.GetName().Name!;
                Console.WriteLine($"Usage: {assemblyName} <structure name> <TR version 9/10/11>");
                Console.WriteLine($"Example: {assemblyName} dtp::MeshRef 11");
                return;
            }

            string headerFilePath = Path.Combine(Path.GetDirectoryName(Assembly.GetEntryAssembly().Location), $"TR{trVersion}.h");
            if (!File.Exists(headerFilePath))
            {
                Console.WriteLine($"Header file missing (expected at {headerFilePath}).");
                return;
            }

            string templateFilePath = $"tr{trVersion}{Regex.Replace(structName, @"^(\w+::)+", "").ToLower()}.bt";

            try
            {
                Console.WriteLine("Reading header file...");
                TypeLibrary lib;
                using (StreamReader reader = new(headerFilePath))
                {
                    lib = new HeaderReader(reader, trVersion == 9 ? 4 : 8).Read();
                }

                Console.WriteLine("Writing binary template...");
                lib.CalculateAlignmentsAndSizes(structName);
                using (StreamWriter writer = new StreamWriter(templateFilePath))
                {
                    new BinaryTemplateWriter(writer, trVersion).WriteType(structName, lib);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
        }

        private static bool TryParseArgs(string[] args, out string structName, out int trVersion)
        {
            structName = null;
            trVersion = 0;

            if (args.Length != 2)
                return false;

            structName = args[0];
            return int.TryParse(args[1], out trVersion) && trVersion >= 9 && trVersion <= 11;
        }
    }
}
