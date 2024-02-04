#include "tr11common.hexpat"

struct AnchorBone
{
    Vector4 offset;
    float weight;
    u16 localBoneId;
    padding[0x20 - 0x16];
} [[format("formatAnchorBone")]];

fn formatAnchorBone(AnchorBone anchorBone)
{
    return std::format("Bone {}", anchorBone.localBoneId);
};

struct SpringVector
{
    Vector3 vector;
    float springIdx;
};

struct SpringVectorArray
{
    u32 count;
    padding[0xC];
    SpringVector vectors[count];
};

struct Mass
{
    Vector4 position;
    InternalRef anchorBonesRef;
    InternalRef springVectorArrayRef;
    u16 localBoneId;
    u8 numAnchorBones;
    u8 massGroupIdx;
    u8 mass;
    u8 bounceBackStrengthFactor;
    padding[0x30 - 0x26];
    
    if (anchorBonesRef.targetPos >= 0)
        AnchorBone anchorBones[numAnchorBones] @ anchorBonesRef.targetPos;
    
    if (springVectorArrayRef.targetPos >= 0)
        SpringVectorArray springVectorArray @ springVectorArrayRef.targetPos;
};

fn formatMass(Mass mass)
{
    return std::format("Bone {}", mass.localBoneId);
};

struct Spring
{
    float restLength;
    float i32erpolationValue;
    u16 massIdx1;
    u16 massIdx2;
};

struct Strip
{
    InternalRef massesRef;
    InternalRef springsRef;
    u32 parentBoneLocalId;
    u16 stripId;
    u16 numMasses;
    u16 numSprings;
    u16 numMassGroups;
    padding[0x20 - 0x1C];
    
    if (massesRef.targetPos >= 0)
        Mass masses[numMasses] @ massesRef.targetPos;
    
    if (springsRef.targetPos >= 0)
        Spring springs[numSprings] @ springsRef.targetPos;
};

struct Cloth
{
    InternalRef stripsRef;
    u16 numStrips;
    if (stripsRef.targetPos >= 0)
        Strip strips[numStrips] @ stripsRef.targetPos;
};

RefDefinitions refDefinitions @ 0;
Cloth cloth @ gResourceBodyPos;
