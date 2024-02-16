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

struct BoneConstraint0
{
    Quaternion quat1;
    Quaternion quat2;
    Vector3 vec1;
    padding[4];
    Vector3 vec2;
    padding[4];
    Vector3 referencePos;
    padding[4];
    Quaternion referenceRot;
    u16 referenceLocalBoneId;
    u8 referenceType;
};

struct BoneConstraint1
{
    Vector4 offset;
};

struct BoneConstraint2
{
    Quaternion offset;
};

struct BoneConstraint3
{
    InternalRef sourceVectors1Ref;
    if (sourceVectors1Ref.targetPos >= 0)
        Vector4 sourceVectors1[parent.numSourceBones] @ sourceVectors1Ref.targetPos;
    
    InternalRef sourceVectors2Ref;
    if (sourceVectors2Ref.targetPos >= 0)
        Vector4 sourceVectors2[parent.numSourceBones] @ sourceVectors2Ref.targetPos;
    
    InternalRef sourceBlendShapeIdsRef;
    if (sourceBlendShapeIdsRef.targetPos >= 0)
        u16 sourceBlendShapeIds[parent.numSourceBones] @ sourceBlendShapeIdsRef.targetPos;
    
    u8 useSourceVectors1;
    u8 useSourceVectors2;
};

struct BoneConstraint
{
    u8 type;
    padding[1];
    u16 targetLocalBoneId;
    u16 numSourceBones;
    padding[2];
    
    InternalRef sourceLocalBoneIdsRef;
    if (sourceLocalBoneIdsRef.targetPos >= 0)
        u16 sourceLocalBoneIds[numSourceBones] @ sourceLocalBoneIdsRef.targetPos;
    
    InternalRef sourceBoneWeightsRef;
    if (sourceBoneWeightsRef.targetPos >= 0)
        float sourceBoneWeights[numSourceBones] @ sourceBoneWeightsRef.targetPos;
    
    InternalRef extraDataRef;
    if (extraDataRef.targetPos > 0)
    {
        match (type)
        {
            (0):
            {
                BoneConstraint0 extraData @ extraDataRef.targetPos;
            }
            (1):
            {
                BoneConstraint1 extraData @ extraDataRef.targetPos;
            }
            (2):
            {
                BoneConstraint2 extraData @ extraDataRef.targetPos;
            }
            (3):
            {
                BoneConstraint3 extraData @ extraDataRef.targetPos;
            }
        }
    }
};

struct BoneConstraintRef
{
    InternalRef boneConstraintRef;
    if (boneConstraintRef.targetPos >= 0)
        BoneConstraint boneConstraint @ boneConstraintRef.targetPos;
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
    
    u8 numBoneConstraints;
    padding[7];
    InternalRef boneConstraintRefsRef;
    if (boneConstraintRefsRef.targetPos >= 0)
        BoneConstraintRef boneConstraintRefs[numBoneConstraints] @ boneConstraintRefsRef.targetPos;
    
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
