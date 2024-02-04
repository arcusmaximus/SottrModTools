namespace SottrModManager.Shared.Cdc
{
    public enum ResourceType
    {
        Unknown = 0,
        Animation = 2,
        PsdRes = 4,
        Texture = 5,
        Sound = 6,
        Dtp = 7,
        Script = 8,
        ShaderLib = 9,
        Material = 10,
        GlobalContentReference = 11,
        Model = 12,
        CollisionMesh = 13,
        ObjectReference = 14,
        AnimationLib = 15
    }

    public enum ResourceSubType
    {
        Texture = 5,
        Model = 26,
        ModelData = 27,
        ShResource = 116,
        CubeLut = 117
    }

    public enum LocaleLanguage
    {
        En = 1,
        Fr = 2,
        De = 4,
        It = 8,
        Es419 = 0x10,
        Es = 0x20,
        Ja = 0x40,
        Pt = 0x80,
        Pl = 0x100,
        Ru = 0x200,
        Ko = 0x800,
        ZhHant = 0x1000,
        ZhHans = 0x2000,
        Ar = 0x8000
    }
}
