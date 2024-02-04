#include "tr11common.hexpat"

struct StripGroupIndexSet
{
    u32 count;
    padding[4];
    InternalRef stripGroupIndicesRef;
    if (stripGroupIndicesRef.targetPos >= 0)
        u32 stripGroupIndices[count] @ stripGroupIndicesRef.targetPos;
};

struct StripGroup
{
    float gravityFactor;
    float undergroundGravityReduction;
    float dampening;
    u32 springStrengthUpdateIterations;
    u32 collisionIterations;
    u32 updateIterations;
    u32 timeDeltaDivider;
    float windFactor;
    u32 flags;
    float maxMassBounceBackStrength;
    float stiffness;
    u32 transformType;
    u32 springStretchinessDefaultPercentage;
    u32 springStretchinessLowerPercentage;
    u32 springStretchinessUpperPercentage;
    u32 springLengthMultiplierPercentage;
    float accelerationDivider;
    float timeDeltaMultiplier1;
    float timeDeltaMultiplier2;
    padding[0x58 - 0x4C];
    
    u32 numStripIds;
    padding[4];
    InternalRef stripIdsRef;
    if (stripIdsRef.targetPos >= 0)
        u16 stripIds[numStripIds] @ stripIdsRef.targetPos;
    
    u32 numCollisionSetIndices;
    padding[4];
    InternalRef collisionSetIndicesRef;
    if (collisionSetIndicesRef.targetPos >= 0)
        u32 collisionSetIndices[numCollisionSetIndices] @ collisionSetIndicesRef.targetPos;
        
    padding[0x90 - 0x78];
};

enum CollisionType : u8
{
    SPHERE,
    CAPSULE,
    TYPE2,
    TYPE3,
    BOX,
    DOUBLERADIICAPSULE = 6
};

struct Collision
{
    CollisionType type;
    padding[0x14 - 1];
    u32 state;
    u64 hashData1;
    u64 hashData2;
    InternalRef hashData3Ref;
};

struct CollisionSet
{
    u32 count;
    padding[4];
    InternalRef collisionsRef;
    if (collisionsRef.targetPos >= 0)
        Collision collisions[count] @ collisionsRef.targetPos;
};

struct ClothComponent
{
    u8 valid;
    padding[7];
    u32 defaultStripGroupIndexSetIdx;
    padding[0xC];
    float sortLowerBound;
    float sortUpperBound;
    
    InternalRef stripGroupIndexSetsRef;
    u32 numStripGroupIndexSets;
    padding[4];
    if (stripGroupIndexSetsRef.targetPos >= 0)
        StripGroupIndexSet stripGroupIndexSets[numStripGroupIndexSets] @ stripGroupIndexSetsRef.targetPos;
    
    InternalRef stripGroupsRef;
    u32 numStripGroups;
    padding[4];
    if (stripGroupsRef.targetPos >= 0)
        StripGroup stripGroups[numStripGroups] @ stripGroupsRef.targetPos;
    
    InternalRef collisionSetsRef;
    u32 numCollisionSets;
    padding[4];
    if (collisionSetsRef.targetPos >= 0)
        CollisionSet collisionSets[numCollisionSets] @ collisionSetsRef.targetPos;
    
    padding[8];
    InternalRef unknownItemsRef;
};

RefDefinitions refDefinitions @ 0;
ClothComponent clothComponent @ gResourceBodyPos;
