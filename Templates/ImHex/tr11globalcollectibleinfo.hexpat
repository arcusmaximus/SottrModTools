#include "tr11common.hexpat"

#pragma pattern_limit 200000

struct CollectibleItem1
{
    u32 hash;
    padding[4];
    
    InternalRef nameRef;
    if (nameRef.targetPos >= 0)
        char name[] @ nameRef.targetPos;
    
    padding[0x1F0 - 0x10];
};

struct CollectibleSet1
{
    u32 type;
    padding[0x10 - 4];
    
    InternalRef nameRef;
    if (nameRef.targetPos >= 0)
        char name[] @ nameRef.targetPos;
    
    padding[0x38 - 0x18];
    InternalRef filePath1Ref;
    if (filePath1Ref.targetPos >= 0)
        char filePath1[] @ filePath1Ref.targetPos;
    
    padding[0x60 - 0x40];
    InternalRef filePath2Ref;
    if (filePath2Ref.targetPos >= 0)
        char filePath2[] @ filePath2Ref.targetPos;
    
    padding[0x98 - 0x68];
    InternalRef itemsRef;
    u32 numItems;
    padding[4];
    if (itemsRef.targetPos >= 0)
        CollectibleItem1 items[numItems] @ itemsRef.targetPos;
};

struct CollectibleItem2
{
    u32 hash;
    padding[4];
    
    InternalRef nameRef;
    if (nameRef.targetPos >= 0)
        char name[] @ nameRef.targetPos;
    
    padding[0xF0 - 0x10];
};

struct CollectibleSet2
{
    u32 type;
    padding[0x10 - 4];
    
    InternalRef itemsRef;
    u32 numItems;
    padding[4];
    if (itemsRef.targetPos >= 0)
        CollectibleItem2 items[numItems] @ itemsRef.targetPos;
};

enum OutfitPieceSlot : u32
{
    HEAD,
    HAIR,
    TORSO,
    LEGS
};

struct OutfitInfo
{
    InternalRef childHashesRef;
    u32 numChildHashes;
    if (childHashesRef.targetPos >= 0)
        u32 childHashes[numChildHashes] @ childHashesRef.targetPos;
    
    OutfitPieceSlot slot;
    u16 zoneId;
    padding[2];
};

struct Outfit
{
    u32 hash;
    padding[4];
    
    InternalRef nameRef;
    if (nameRef.targetPos >= 0)
        char name[] @ nameRef.targetPos;
    
    padding[0xF0 - 0x10];
    u32 isPiece;
    padding[0x108 - 0xF4];
    
    InternalRef modifiersRef;
    u32 numModifiers;
    padding[4];
    if (modifiersRef.targetPos >= 0)
        u16 modifiers[numModifiers] @ modifiersRef.targetPos;
    
    u64 nameLocaleHash;
    u64 descriptionLocaleHash;
    padding[8];
    
    InternalRef infoRef;
    if (infoRef.targetPos >= 0)
        OutfitInfo info @ infoRef.targetPos;
    
    u32 imageDtpId;
    padding[4];
    InternalRef imageFileNameRef;
    if (imageFileNameRef.targetPos >= 0)
        char imageFileName[] @ imageFileNameRef.targetPos;
    
    padding[0x1D8 - 0x148];
    u8 photoModeFaceChooserDisabled;
    u8 photoModeMuscleSliderDisabled;
    padding[0x1E0 - 0x1DA];
};

struct OutfitSet
{
    u32 type;
    u32 field_4;
    u32 field_8;
    u32 field_C;
    InternalRef outfitsRef;
    u32 numOutfits;
    padding[4];
    
    if (outfitsRef.targetPos >= 0)
        Outfit outfits[numOutfits] @ outfitsRef.targetPos;
};

struct Root
{
    InternalRef set1sRef;
    u32 numSet1s;
    //if (set1sRef.targetPos >= 0)
    //    CollectibleSet1 set1s[numSet1s] @ set1sRef.targetPos;
    
    padding[0x20 - 0xC];
    InternalRef set2sRef;
    u32 numSet2s;
    //if (set2sRef.targetPos >= 0)
    //    CollectibleSet2 set2s[numSet2s] @ set2sRef.targetPos;
    
    padding[0x58 - 0x2C];
    InternalRef outfitSetsRef;
    u32 numOutfitSets;
    if (outfitSetsRef.targetPos >= 0)
        OutfitSet outfitSets[numOutfitSets] @ outfitSetsRef.targetPos;
};

struct RootRef
{
    InternalRef rootRef;
    if (rootRef.targetPos >= 0)
        Root root @ rootRef.targetPos;
};

RefDefinitions refDefinitions @ 0;
RootRef rootRef @ gResourceBodyPos;
