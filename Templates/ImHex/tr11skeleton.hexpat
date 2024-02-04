#include "tr11common.hexpat"

struct Bone
{
    Vector4 position;
    Quaternion orientation;
    float distanceFromParent;
    u32 flags;
    s32 parentBoneId;
    u32 field_2C;
    u32 field_30;
    u32 field_34;
    u32 field_38;
    u32 field_3C;
} [[single_color]];

struct BoneArray
{
    u64 numBones;
    InternalRef bonesRef;
    if (bonesRef.targetPos >= 0)
        Bone bones[numBones] @ bonesRef.targetPos;
};

struct IdMapping
{
    u16 globalId;
    u16 localId;
} [[format("formatIdMapping")]];

fn formatIdMapping(IdMapping mapping)
{
    return std::format("{} -> {}", mapping.globalId, mapping.localId);
};

struct CounterpartRange
{
    u16 localIdRange1Start;
    u16 localIdRange2Start;
    u16 count;
    if (count == 0)
        break;
};

struct ExtraBoneInfo
{
    u8 type;
    padding[1];
    u16 localBoneId;
    u16 numAssociatedLocalBoneIds;
    padding[2];
    
    InternalRef associatedLocalBoneIdsRef;
    if (associatedLocalBoneIdsRef.targetPos >= 0)
        u16 associatedLocalBoneIds[numAssociatedLocalBoneIds] @ associatedLocalBoneIdsRef.targetPos;
    
    InternalRef floatsRef;
    if (floatsRef.targetPos >= 0)
        float floats[numAssociatedLocalBoneIds] @ floatsRef.targetPos;
    
    InternalRef quaternionRef;
    if (quaternionRef.targetPos >= 0)
        Quaternion quaternion @ quaternionRef.targetPos;
};

struct ExtraBoneInfoRef
{
    InternalRef extraBoneInfoRef;
    if (extraBoneInfoRef.targetPos >= 0)
        ExtraBoneInfo extraBoneInfo @ extraBoneInfoRef.targetPos;
};

struct Skeleton
{
    InternalRef boneArrayRef;
    BoneArray boneArray @ boneArrayRef.targetPos;
    
    u16 numAnimIdMappings;
    padding[6];
    InternalRef counterpartRangesRef;
    if (counterpartRangesRef.targetPos >= 0)
        CounterpartRange counterpartRanges[while(true)] @ counterpartRangesRef.targetPos;
    
    u64 numWords1;
    InternalRef words1Ref;
    if (words1Ref.targetPos >= 0)
        u16 words1[numWords1] @ words1Ref.targetPos;
    
    u16 numBoneIdMappings;
    padding[6];
    InternalRef boneIdMappingsRef;
    if (boneIdMappingsRef.targetPos >= 0)
        IdMapping boneIdMappings[numBoneIdMappings] @ boneIdMappingsRef.targetPos [[single_color]];
    
    u8 numBlendShapeIdMappings;
    padding[7];
    InternalRef blendShapeIdMappingsRef;
    if (blendShapeIdMappingsRef.targetPos >= 0)
        IdMapping blendShapeIdMappings[numBlendShapeIdMappings] @ blendShapeIdMappingsRef.targetPos [[single_color]];
    
    u8 numExtraBoneInfos;
    padding[7];
    InternalRef extraBoneInfoRefsRef;
    if (extraBoneInfoRefsRef.targetPos >= 0)
        ExtraBoneInfoRef extraBoneInfoRefs[numExtraBoneInfos] @ extraBoneInfoRefsRef.targetPos;
    
    u8 numWords2;
    padding[7];
    InternalRef words2Ref;
    if (words2Ref.targetPos >= 0)
        u16 words2[numWords2] @ words2Ref.targetPos;
    
    InternalRef boneBytesRef;
    if (boneBytesRef.targetPos >= 0)
        u8 boneBytes[boneArray.numBones] @ boneBytesRef.targetPos;
    
    InternalRef localBoneIdsByAnimIdRef;
    if (localBoneIdsByAnimIdRef.targetPos >= 0)
        u16 localBoneIdsByAnimId[numAnimIdMappings] @ localBoneIdsByAnimIdRef.targetPos;
    
    InternalRef animBoneIdsByLocalIdRef;
    if (animBoneIdsByLocalIdRef.targetPos >= 0)
        u16 animBoneIdsByLocalId[numAnimIdMappings] @ animBoneIdsByLocalIdRef.targetPos;
    
    u16 unknownCounts[4];
};

RefDefinitions refDefinitions @ 0;
Skeleton skeleton @ gResourceBodyPos;
