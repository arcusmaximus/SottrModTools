#include "tr11common.hexpat"

bitfield ShaderTextureSlot
{
    padding : 11;
    slot : 5;
} [[inline]];

struct ShaderTexture
{
    ExternalRef textureRef;
    u32;
    ShaderTextureSlot slot;
    padding[2];
} [[color("C0C000")]];

struct ShaderConstant
{
    float x;
    float y;
    float z;
    float w;
} [[format("formatShaderConstant"), color("00D0D0")]];

fn formatShaderConstant(ShaderConstant constant)
{
    return std::format("({}, {}, {}, {})", constant.x, constant.y, constant.z, constant.w);
};

struct ShaderSet
{
    ExternalRef pixelOrHullShader;
    ExternalRef vertexOrDomainShader;
    u32 flags;
    
    u8 numPsTextures_;
    u8 numPsTextureRanges;
    u8 numPsTextures;
    u8 psTextureRangeStartIdx;
    InternalRef psTexturesRef;
    if (psTexturesRef.targetPos >= 0)
        ShaderTexture psTextures[numPsTextures] @ psTexturesRef.targetPos;
    u32 numPsConstants;
    padding[4];
    InternalRef psConstantsRef;
    if (psConstantsRef.targetPos >= 0)
        ShaderConstant psConstants[numPsConstants] @ psConstantsRef.targetPos;
    
    u8 numVsTextures_;
    u8 numVsTextureRanges;
    u8 numVsTextures;
    u8 vsTextureRangeStartIdx;
    padding[4];
    InternalRef vsTexturesRef;
    if (vsTexturesRef.targetPos >= 0)
        ShaderTexture vsTextures[numVsTextures] @ vsTexturesRef.targetPos;
    u32 numVsConstants;
    padding[4];
    InternalRef vsConstantsRef;
    if (vsConstantsRef.targetPos >= 0)
        ShaderConstant vsConstants[numVsConstants] @ vsConstantsRef.targetPos;
    padding[8];
    
    InternalRef tesselationShaderRef;
    InternalRef extraRefs[3];
} [[color("800080")]];

struct ShaderSetRef
{
    InternalRef reference;
    if (reference.targetPos != -1)
        ShaderSet shaderSet @ reference.targetPos;
};

struct Material
{
    u16 version;
    padding[0x54-2];
    type::Magic<"DtaM"> magic;
    ShaderSetRef shaderSets[9];
};


RefDefinitions refDefinitions @ 0;
Material material @ gResourceBodyPos;
