#include "tr11common.hexpat"

struct Bone
{
    Vector position;
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

struct BoneIdMapping
{
    u16 animBoneId;
    u16 skeletonBoneId;
};

struct Skeleton
{
    InternalRef boneArrayRef;
    BoneArray boneArray @ boneArrayRef.targetPos;
    
    u16 numWords3;
    u16;
    u32;
    InternalRef;
    
    u64 numWords1;
    InternalRef words1Ref;
    if (words1Ref.targetPos >= 0)
        u16 words1[numWords1] @ words1Ref.targetPos;
    
    u16 numMappings1;
    padding[6];
    InternalRef mappings1Ref;
    if (mappings1Ref.targetPos >= 0)
        BoneIdMapping mappings1[numMappings1] @ mappings1Ref.targetPos [[single_color]];
    
    u8 numMappings2;
    padding[7];
    InternalRef mappings2Ref;
    if (mappings2Ref.targetPos >= 0)
        BoneIdMapping mappings2[numMappings2] @ mappings2Ref.targetPos [[single_color]];
    
    u64;
    InternalRef;
    
    u8 numWords2;
    padding[7];
    InternalRef words2Ref;
    if (words2Ref.targetPos >= 0)
        u16 words2[numWords2] @ words2Ref.targetPos;
    
    InternalRef boneBytesRef;
    if (boneBytesRef.targetPos >= 0)
        u8 boneBytes[boneArray.numBones] @ boneBytesRef.targetPos;
    
    InternalRef words3ARef;
    if (words3ARef.targetPos >= 0)
        u16 words3A[numWords3] @ words3ARef.targetPos;
    
    InternalRef words3BRef;
    if (words3BRef.targetPos >= 0)
        u16 words3B[numWords3] @ words3BRef.targetPos;
    
    u16;
    u16;
    u32;
};

RefDefinitions refDefinitions @ 0;
Skeleton skeleton @ gResourceBodyPos;
