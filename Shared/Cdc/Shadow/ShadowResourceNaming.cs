using System.Collections.Generic;

namespace TrRebootTools.Shared.Cdc.Shadow
{
    internal class ShadowResourceNaming : ResourceNaming
    {
        private static readonly Dictionary<(ResourceType, ResourceSubType), string[]> _mappings =
            new()
            {
                { (ResourceType.Animation, 0), new[] { ".tr11anim" } },
                { (ResourceType.AnimationLib, 0), new[] { ".tr11animlib" } },
                { (ResourceType.CollisionMesh, 0), new[] { ".tr11cmesh" } },
                { (ResourceType.Dtp, 0), new[] { ".tr11dtp" } },
                { (ResourceType.GlobalContentReference, 0), new[] { ".tr11contentref" } },
                { (ResourceType.Material, 0), new[] { ".tr11material" } },
                { (ResourceType.Model, ResourceSubType.CubeLut), new[] { ".tr11cubelut" } },
                { (ResourceType.Model, ResourceSubType.Model), new[] { ".tr11model" } },
                { (ResourceType.Model, ResourceSubType.ModelData), new[] { ".tr11modeldata" } },
                { (ResourceType.Model, ResourceSubType.ShResource), new[] { ".tr11shresource" } },
                { (ResourceType.ObjectReference, 0), new[] { ".tr11objectref" } },
                { (ResourceType.PsdRes, 0), new[] { ".tr11psdres" } },
                { (ResourceType.Script, 0), new[] { ".tr11script" } },
                { (ResourceType.ShaderLib, 0), new[] { ".tr11shaderlib" } },
                { (ResourceType.SoundBank, 0), new[] { ".bnk" } },
                { (ResourceType.Texture, 0), new[] { ".dds" } }
            };

        protected override Dictionary<(ResourceType, ResourceSubType), string[]> Mappings => _mappings;
    }
}
