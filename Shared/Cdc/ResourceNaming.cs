using System.IO;

namespace SottrModManager.Shared.Cdc
{
    public static class ResourceNaming
    {
        private static class Extensions
        {
            public const string Animation = ".tr11anim";
            public const string AnimationLib = ".tr11animlib";
            public const string CollisionMesh = ".tr11cmesh";
            public const string CubeLut = ".tr11cubelut";
            public const string Dtp = ".tr11dtp";
            public const string GlobalContentReference = ".tr11contentref";
            public const string Material = ".tr11material";
            public const string Model = ".tr11model";
            public const string ModelData = ".tr11modeldata";
            public const string ObjectReference = ".tr11objectref";
            public const string PsdRes = ".tr11psdres";
            public const string Script = ".tr11script";
            public const string ShaderLib = ".tr11shaderlib";
            public const string ShResource = ".tr11shresource";
            public const string Sound = ".tr11sound";
            public const string Texture = ".dds";
        }

        public static (ResourceType, ResourceSubType) GetType(string filePath)
        {
            return Path.GetExtension(filePath) switch
            {
                Extensions.Animation =>                 (ResourceType.Animation, 0),
                Extensions.AnimationLib =>              (ResourceType.AnimationLib, 0),
                Extensions.CollisionMesh =>             (ResourceType.CollisionMesh, 0),
                Extensions.CubeLut =>                   (ResourceType.Model, ResourceSubType.CubeLut),
                Extensions.Dtp =>                       (ResourceType.Dtp, 0),
                Extensions.GlobalContentReference =>    (ResourceType.GlobalContentReference, 0),
                Extensions.Material =>                  (ResourceType.Material, 0),
                Extensions.Model =>                     (ResourceType.Model, ResourceSubType.Model),
                Extensions.ModelData =>                 (ResourceType.Model, ResourceSubType.ModelData),
                Extensions.ObjectReference =>           (ResourceType.ObjectReference, 0),
                Extensions.PsdRes =>                    (ResourceType.PsdRes, 0),
                Extensions.Script =>                    (ResourceType.Script, 0),
                Extensions.ShaderLib =>                 (ResourceType.ShaderLib, 0),
                Extensions.ShResource =>                (ResourceType.Model, ResourceSubType.ShResource),
                Extensions.Sound =>                     (ResourceType.Sound, 0),
                Extensions.Texture =>                   (ResourceType.Texture, ResourceSubType.Texture),
                _ => (ResourceType.Unknown, 0)
            };
        }

        public static string GetExtension(ResourceType type, ResourceSubType subType)
        {
            return type switch
            {
                ResourceType.Animation =>               Extensions.Animation,
                ResourceType.AnimationLib =>            Extensions.AnimationLib,
                ResourceType.CollisionMesh =>           Extensions.CollisionMesh,
                ResourceType.Dtp =>                     Extensions.Dtp,
                ResourceType.GlobalContentReference =>  Extensions.GlobalContentReference,
                ResourceType.Material =>                Extensions.Material,
                ResourceType.Model => subType switch
                {
                    ResourceSubType.CubeLut =>          Extensions.CubeLut,
                    ResourceSubType.Model =>            Extensions.Model,
                    ResourceSubType.ModelData =>        Extensions.ModelData,
                    ResourceSubType.ShResource =>       Extensions.ShResource,
                    ResourceSubType.Texture =>          Extensions.Texture,
                    _ =>                                Extensions.Model + (int)subType
                },
                
                ResourceType.ObjectReference =>         Extensions.ObjectReference,
                ResourceType.PsdRes =>                  Extensions.PsdRes,
                ResourceType.Script =>                  Extensions.Script,
                ResourceType.ShaderLib =>               Extensions.ShaderLib,
                ResourceType.Sound =>                   Extensions.Sound,
                ResourceType.Texture =>                 Extensions.Texture,
                _ => ".type" + (int)type
            };
        }

        public static bool TryGetResourceKey(string filePath, out ResourceKey resourceKey)
        {
            (ResourceType type, ResourceSubType subType) = GetType(filePath);
            if (type == 0 || !int.TryParse(Path.GetFileNameWithoutExtension(filePath), out int id))
            {
                resourceKey = default;
                return false;
            }

            resourceKey = new ResourceKey(type, subType, id);
            return true;
        }

        public static string GetFilePath(ResourceKey resourceKey)
        {
            return $"{resourceKey.Type}\\{resourceKey.Id}{GetExtension(resourceKey.Type, resourceKey.SubType)}";
        }
    }
}
