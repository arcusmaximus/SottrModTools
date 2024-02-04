#include "tr11common.hexpat"

struct ObjectRef
{
    padding[0x20];
    u32 zoneId;
};

RefDefinitions refDefinitions @ 0;
ObjectRef objectRef @ gResourceBodyPos;
