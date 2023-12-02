#include "tr11common.hexpat"

struct GlobalContentReference
{
    ExternalRef reference;
    padding[0x10];
    u32 globalContentId;
};

RefDefinitions refDefinitions @ 0;
GlobalContentReference reference @ gResourceBodyPos;
