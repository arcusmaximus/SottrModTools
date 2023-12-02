#include "tr11common.hexpat"

struct Model
{
    ExternalRef modelDataRef;
    InternalRef textureRefsRef;
    InternalRef materialRefsRef;
    
    ExternalRef textureRefs[while($ < materialRefsRef.targetPos)] @ textureRefsRef.targetPos;
    ExternalRef materialRefs[while($ < std::mem::size())] @ materialRefsRef.targetPos;
};

RefDefinitions refDefinitions @ 0;
Model model @ gResourceBodyPos;
