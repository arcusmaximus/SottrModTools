using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using SottrModManager.Shared;
using SottrModManager.Shared.Cdc;
using SottrModManager.Shared.Util;

namespace SottrExtractor
{
    public static class Program
    {
        [STAThread]
        public static void Main()
        {
            /*
            MergeSkeleton(
                @"E:\Projects\SottrModTools\Build\Debug\net6.0-windows\_mod\320005.tr11dtp",
                @"E:\Projects\SottrModTools\Build\Debug\net6.0-windows\pcx64-w\paperdoll_piece_tr11_lara_tactical_head.drm\Dtp\321418.tr11dtp",
                @"E:\Projects\SottrModTools\Build\Debug\net6.0-windows\pcx64-w\paperdoll_piece_tr11_lara_aod_legs.drm\Dtp\320005.tr11dtp"
            );
            return;
            */

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            string gameFolderPath = GameFolderFinder.Find();
            if (gameFolderPath == null)
                return;

            Application.Run(new MainForm(gameFolderPath));
        }

        private static void MergeSkeleton(string outputFilePath, string input1FilePath, string input2FilePath)
        {
            File.Copy(input2FilePath, outputFilePath, true);
            using Skeleton skeleton1 = OpenSkeleton(input1FilePath);
            using Skeleton skeleton2 = OpenSkeleton(outputFilePath);

            Dictionary<ushort, ushort> localToGlobalBoneIdMapping1 = new();
            foreach ((ushort globalBoneId, ushort localBoneId1) in skeleton1.GlobalToLocalBoneIdMapping)
            {
                localToGlobalBoneIdMapping1.Add(localBoneId1, globalBoneId);

                if (!skeleton2.GlobalToLocalBoneIdMapping.ContainsKey(globalBoneId))
                {
                    Bone bone2 = skeleton1.Bones[localBoneId1];
                    if (bone2.parentBoneId >= 0)
                    {
                        ushort parentGlobalBoneId = localToGlobalBoneIdMapping1[(ushort)bone2.parentBoneId];
                        bone2.parentBoneId = skeleton2.GlobalToLocalBoneIdMapping[parentGlobalBoneId];
                    }
                    skeleton2.Bones.Add(bone2);
                    skeleton2.BoneBytes.Add(skeleton1.BoneBytes[localBoneId1]);
                    skeleton2.GlobalToLocalBoneIdMapping.Add(globalBoneId, (ushort)(skeleton2.Bones.Count - 1));
                }
            }

            BinaryWriter writer = new BinaryWriter(skeleton2.Stream);
            skeleton2.Stream.Position = skeleton2.RefDefinitions.GetInternalRefTarget(skeleton2.RefDefinitions.Size);
            writer.Write(skeleton2.Bones.Count);
            skeleton2.Stream.Position += 4;
            skeleton2.RefDefinitions.SetInternalRefTarget((int)skeleton2.Stream.Position, (int)skeleton2.Stream.Length);
            skeleton2.Stream.Position = skeleton2.Stream.Length;
            foreach (Bone bone in skeleton2.Bones)
            {
                Bone bone_ = bone;
                writer.WriteStruct(ref bone_);
            }

            skeleton2.Stream.Position = skeleton2.RefDefinitions.Size + 0x28;
            writer.Write(skeleton2.GlobalToLocalBoneIdMapping.Count);
            skeleton2.Stream.Position += 4;
            skeleton2.RefDefinitions.SetInternalRefTarget((int)skeleton2.Stream.Position, (int)skeleton2.Stream.Length);
            skeleton2.Stream.Position = skeleton2.Stream.Length;
            foreach ((ushort globalBoneId, ushort localBoneId) in skeleton2.GlobalToLocalBoneIdMapping)
            {
                writer.Write(globalBoneId);
                writer.Write(localBoneId);
            }

            skeleton2.RefDefinitions.SetInternalRefTarget(skeleton2.RefDefinitions.Size + 0x68, (int)skeleton2.Stream.Length);
            skeleton2.Stream.Position = skeleton2.Stream.Length;
            foreach (byte boneByte in skeleton2.BoneBytes)
            {
                writer.Write(boneByte);
            }
        }

        private static Skeleton OpenSkeleton(string filePath)
        {
            Stream stream = File.Open(filePath, FileMode.Open, FileAccess.ReadWrite);
            BinaryReader reader = new BinaryReader(stream);
            ResourceRefDefinitions refDefinitions = new ResourceRefDefinitions(stream);

            stream.Position = refDefinitions.GetInternalRefTarget((int)stream.Position);
            int numBones = reader.ReadInt32();
            stream.Position += 4;
            stream.Position = refDefinitions.GetInternalRefTarget((int)stream.Position);

            List<Bone> bones = new List<Bone>(numBones);
            for (int i = 0; i < numBones; i++)
            {
                bones.Add(reader.ReadStruct<Bone>());
            }

            stream.Position = refDefinitions.Size + 0x28;
            int numMappings = reader.ReadInt32();
            stream.Position += 4;
            stream.Position = refDefinitions.GetInternalRefTarget((int)stream.Position);
            Dictionary<ushort, ushort> globalToLocalBoneIdMapping = new();
            for (int i = 0; i < numMappings; i++)
            {
                ushort globalBoneId = reader.ReadUInt16();
                ushort localBoneId = reader.ReadUInt16();
                globalToLocalBoneIdMapping.Add(globalBoneId, localBoneId);
            }

            stream.Position = refDefinitions.GetInternalRefTarget(refDefinitions.Size + 0x68);
            List<byte> boneBytes = new List<byte>(numBones);
            for (int i = 0; i < numBones; i++)
            {
                boneBytes.Add(reader.ReadByte());
            }

            return new Skeleton
            {
                Stream = stream,
                RefDefinitions = refDefinitions,
                Bones = bones,
                BoneBytes = boneBytes,
                GlobalToLocalBoneIdMapping = globalToLocalBoneIdMapping
            };
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct Vector
        {
            public float x, y, z, w;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct Quaternion
        {
            public float x, y, z, w;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct Bone
        {
            public Vector position;
            public Quaternion orientation;
            public float distanceFromParent;
            public int flags;
            public int parentBoneId;
            public int field_2C;
            public int field_30;
            public int field_34;
            public int field_38;
            public int field_3C;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct BoneIdMapping
        {
            public ushort globalId;
            public ushort localId;
        }

        private class Skeleton : IDisposable
        {
            public Stream Stream;
            public ResourceRefDefinitions RefDefinitions;
            public List<Bone> Bones;
            public List<byte> BoneBytes;
            public Dictionary<ushort, ushort> GlobalToLocalBoneIdMapping;

            public void Dispose()
            {
                Stream.Dispose();
            }
        }
    }
}
