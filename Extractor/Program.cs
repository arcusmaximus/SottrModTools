using System;
using System.Windows.Forms;
using SottrModManager.Shared;

namespace SottrExtractor
{
    public static class Program
    {
        [STAThread]
        public static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            string gameFolderPath = GameFolderFinder.Find();
            if (gameFolderPath == null)
                return;

            Application.Run(new MainForm(gameFolderPath));
        }

        /*
        private static void ScanObjects(ArchiveSet archiveSet)
        {
            foreach (ulong drmFileHash in CdcHash.Hashes)
            {
                string drmFilePath = CdcHash.Lookup(drmFileHash);
                if (drmFilePath == null || !drmFilePath.EndsWith(".drm"))
                    continue;

                ResourceCollection collection = archiveSet.GetResourceCollection(drmFileHash);
                if (collection == null)
                    continue;

                ResourceReference objectRefRef = collection.ResourceReferences.FirstOrDefault(r => r.Type == ResourceType.ObjectReference);
                if (objectRefRef == null)
                    continue;

                int objectDtpId;
                Stream objectRefStream = new MemoryStream();
                using (Stream resourceStream = archiveSet.OpenResource(objectRefRef))
                {
                    resourceStream.CopyTo(objectRefStream);
                    objectRefStream.Position = 0;
                }
                ResourceRefDefinitions refDefs = new ResourceRefDefinitions(objectRefStream);
                objectDtpId = refDefs.ExternalRefs.First().ResourceKey.Id;

                ResourceReference objectRef = collection.ResourceReferences.First(r => r.Type == ResourceType.Dtp && r.Id == objectDtpId);
                Stream objectStream = new MemoryStream();
                using (Stream resourceStream = archiveSet.OpenResource(objectRef))
                {
                    resourceStream.CopyTo(objectStream);
                    objectStream.Position = 0;
                }

                ResourceRefDefinitions objectRefDefs = new ResourceRefDefinitions(objectStream);
                BinaryReader objectReader = new BinaryReader(objectStream);

                objectStream.Position += 0x38;
                int numComponentTypes = objectReader.ReadInt32();

                objectStream.Position += 4;
                int componentsPos = objectRefDefs.GetInternalRefTarget((int)objectStream.Position);

                int numActionGraphs = 0;
                int actionGraphsPos = 0;
                for (int i = 0; i < numComponentTypes; i++)
                {
                    objectStream.Position = componentsPos + i * 0x10;
                    int componentType = objectReader.ReadInt32();
                    if (componentType != 0x2777E1B3)
                        continue;

                    numActionGraphs = objectReader.ReadInt32();
                    actionGraphsPos = objectRefDefs.GetInternalRefTarget((int)objectStream.Position);
                    break;
                }

                if (numActionGraphs == 0)
                    continue;

                for (int i = 0; i < numActionGraphs; i++)
                {
                    ResourceKey actionGraphKey = objectRefDefs.GetExternalRefTarget(actionGraphsPos + 0x70 * i + 0x60);
                    ResourceReference actionGraphRef = collection.ResourceReferences.FirstOrDefault(r => r.Type == ResourceType.Dtp && r.Id == actionGraphKey.Id);
                    if (actionGraphRef != null)
                        ScanAndPatchActionGraph(actionGraphRef, archiveSet);
                }
            }
        }

        private static void ScanAndPatchActionGraph(ResourceReference actionGraphRef, ArchiveSet archiveSet)
        {
            Stream memStream = new MemoryStream();
            using (Stream resourceStream = archiveSet.OpenResource(actionGraphRef))
            {
                resourceStream.CopyTo(memStream);
                memStream.Position = 0;
            }

            ResourceRefDefinitions refDefs = new ResourceRefDefinitions(memStream);
            BinaryReader reader = new BinaryReader(memStream);
            BinaryWriter writer = new BinaryWriter(memStream);
            
            memStream.Position = refDefs.GetInternalRefTarget((int)memStream.Position + 0x18);
            int numNodes = reader.ReadInt32();
            int nodesPos = refDefs.GetInternalRefTarget((int)memStream.Position + 4);
            bool changesMade = false;
            for (int i = 0; i < numNodes; i++)
            {
                int nodePos = nodesPos + i * 0x20;
                memStream.Position = nodePos;
                short type = reader.ReadInt16();
                if (type != 0xCE)
                    continue;

                int argsPos;
                try
                {
                    argsPos = refDefs.GetInternalRefTarget(nodePos + 8);
                }
                catch
                {
                    continue;
                }
                int skipTimePos = argsPos + 0x60;
                memStream.Position = skipTimePos;
                float skipTime = reader.ReadSingle();
                if (skipTime <= 2)
                    continue;

                memStream.Position = skipTimePos;
                writer.Write(2f);
                changesMade = true;
            }

            if (!changesMade)
                return;

            using Stream fileStream = File.Create(Path.Combine(@"E:\Projects\SottrModTools\Build\Debug\net6.0-windows\_skip", actionGraphRef.Id + ".tr11dtp"));
            memStream.Position = 0;
            memStream.CopyTo(fileStream);
        }
        */

        /*
        private static void ExtractFlashFiles()
        {
            const string baseFolderPath = @"E:\Projects\SottrModTools\Build\Debug\net6.0-windows\pcx64-w\campsite_menus.drm";
            Dictionary<int, string> swfs = ReadIndex(baseFolderPath);

            foreach ((int dtpId, string relativeSwfPath) in swfs)
            {
                string dtpFilePath = Path.Combine(baseFolderPath, "Dtp", dtpId + ".tr11dtp");
                if (!File.Exists(dtpFilePath))
                    continue;

                ReadSwfDtp(dtpFilePath, out byte[] swf, out Dictionary<int, string> textures);

                string swfFilePath = Path.Combine(baseFolderPath, "Swf", relativeSwfPath + ".swf");
                string swfFolderPath = Path.GetDirectoryName(swfFilePath);
                Directory.CreateDirectory(swfFolderPath);
                File.WriteAllBytes(swfFilePath, swf);

                foreach ((int textureId, string relativeTextureFilePath) in textures)
                {
                    string srcTexturePath = Path.Combine(baseFolderPath, "Texture", textureId + ".dds");
                    if (!File.Exists(srcTexturePath))
                        continue;

                    string dstTexturePath = Path.Combine(swfFolderPath, relativeTextureFilePath + ".dds");
                    Directory.CreateDirectory(Path.GetDirectoryName(dstTexturePath));
                    File.Copy(srcTexturePath, dstTexturePath, true);
                }
            }
        }

        private static Dictionary<int, string> ReadIndex(string folderPath)
        {
            Dictionary<int, string> index = new();

            string contentRefFilePath = Path.Combine(folderPath, Path.GetFileNameWithoutExtension(folderPath) + ".tr11contentref");
            using Stream contentRefStream = File.OpenRead(contentRefFilePath);
            var indexRef = new ResourceRefDefinitions(contentRefStream).ExternalRefs.First();

            string indexFilePath = Path.Combine(folderPath, "Dtp", indexRef.ResourceKey.Id + ".tr11dtp");
            using Stream indexStream = File.OpenRead(indexFilePath);
            var indexRefs = new ResourceRefDefinitions(indexStream);
            indexStream.Position = indexRefs.GetInternalRefTarget((int)indexStream.Position) + 8;
            BinaryReader indexReader = new BinaryReader(indexStream);
            for (int i = 0; i < 2; i++)
            {
                int numFiles = indexReader.ReadInt32();
                indexStream.Position += 4;
                int setReturnPos = (int)indexStream.Position + 8;
                indexStream.Position = indexRefs.GetInternalRefTarget((int)indexStream.Position);

                for (int j = 0; j < numFiles; j++)
                {
                    indexStream.Position += 0x10;
                    int dtpId = indexReader.ReadInt32();
                    indexStream.Position += 0x220 - 0x14;
                    int fileReturnPos = (int)indexStream.Position + 8;
                    indexStream.Position = indexRefs.GetInternalRefTarget((int)indexStream.Position);

                    string filePath = indexReader.ReadZeroTerminatedString();
                    index[dtpId] = filePath;

                    indexStream.Position = fileReturnPos;
                }

                indexStream.Position = setReturnPos;
            }

            return index;
        }

        private static void ReadSwfDtp(string dtpFilePath, out byte[] swf, out Dictionary<int, string> textures)
        {
            using Stream stream = File.OpenRead(dtpFilePath);
            BinaryReader reader = new BinaryReader(stream);

            ResourceRefDefinitions refs = null;
            int numInternalRefs = reader.ReadInt32();
            stream.Position -= 4;
            if (numInternalRefs == 0)
                refs = new ResourceRefDefinitions(stream);
            
            int swfLength = reader.ReadInt32();
            swf = reader.ReadBytes(swfLength);

            textures = new();
            if (refs == null)
                return;

            stream.Position = (stream.Position + 3) & ~3;
            int numTextures = reader.ReadInt32();
            int padding = reader.ReadInt32();
            if (padding != 0)
                stream.Position -= 4;

            for (int i = 0; i < numTextures; i++)
            {
                long texturePos = stream.Position;
                string textureFilePath = reader.ReadZeroTerminatedString();
                stream.Position = texturePos + 0x100;

                int textureId = refs.GetExternalRefTarget((int)stream.Position).Id;
                stream.Position += 8;

                textures.Add(textureId, textureFilePath);
            }
        }
        */
    }
}
