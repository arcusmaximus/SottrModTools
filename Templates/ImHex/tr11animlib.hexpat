#include "tr11common.hexpat"

struct Animation
{
    u16 id;
    padding[0x10 - 2];
    InternalRef nameRef;
    if (nameRef.targetPos >= 0)
        char name[] @ nameRef.targetPos;
};

struct AnimLib
{
    padding[0x10];
    u32 numAnimations;
    padding[4];
    InternalRef animationsRef;
    if (animationsRef.targetPos >= 0)
        Animation animations[numAnimations] @ animationsRef.targetPos;
};

RefDefinitions refDefinitions @ 0;
AnimLib lib @ gResourceBodyPos;
