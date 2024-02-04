using SottrModManager.Shared;
using SottrModManager.Shared.Cdc;
using System.IO;
using System.Linq;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Threading;

namespace SottrExtractor
{
    internal class FileExtractor
    {
        private readonly ArchiveSet _archiveSet;

        public FileExtractor(ArchiveSet archiveSet)
        {
            _archiveSet = archiveSet;
        }

        public void Extract(string filePath, ArchiveFileReference fileRef, ITaskProgress progress, CancellationToken cancellationToken)
        {
            try
            {
                progress.Begin("Extracting...");

                using Stream archiveFileStream = _archiveSet.OpenFile(fileRef);

                string folderPath = Path.GetDirectoryName(filePath);
                Directory.CreateDirectory(folderPath);

                if (Path.GetFileName(folderPath) == "locals.bin")
                {
                    filePath = Path.ChangeExtension(filePath, ".json");
                    using Stream extractedFileStream = File.Create(filePath);
                    ExtractLocalsBin(archiveFileStream, extractedFileStream);
                }
                else
                {
                    using Stream extractedFileStream = File.Create(filePath);
                    archiveFileStream.CopyTo(extractedFileStream);
                }
            }
            finally
            {
                progress.End();
            }
        }

        private void ExtractLocalsBin(Stream archiveFileStream, Stream extractedFileStream)
        {
            LocalsBin locals = new LocalsBin(archiveFileStream);

            using Utf8JsonWriter writer = new Utf8JsonWriter(extractedFileStream, new JsonWriterOptions { Indented = true, Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping });
            writer.WriteStartObject();
            foreach ((string key, string value) in locals.Strings.OrderBy(s => s.Key))
            {
                writer.WriteString(key, value);
            }
            writer.WriteEndObject();
        }
    }
}
