#include <std/core.pat>
#include <std/io.pat>
#include <std/mem.pat>
#include <std/string.pat>
#include <std/sys.pat>
#include <type/magic.pat>

bool revealRefs in;

enum ResourceType : u8
{
    NONE                = 0,
    ANIMATION           = 2,
    PSDRES              = 4,
    TEXTURE             = 5,
    SOUND               = 6,
    DTP                 = 7,
    SCRIPT              = 8,
    SHADERLIB           = 9,
    MATERIAL            = 10,
    GLOBALCONTENTREF    = 11,
    MODEL               = 12,
    COLLISIONMESH       = 13,
    OBJECTREF           = 14,
    TRIGGER             = 15
};

u32 gResourceBodyPos;
s16 gRefIndexByFilePos[std::mem::size() / 4];

fn getRefIndex(u32 filePos)
{
    return gRefIndexByFilePos[filePos / 4] - 1;
};

fn setRefIndex(u32 filePos, s16 refIdx)
{
    gRefIndexByFilePos[filePos / 4] = refIdx + 1;
};

struct InternalRefValue<auto targetPos>
{
    s32 targetPos = targetPos;
    u64;
} [[sealed, format("formatInternalRef"), color(this.targetPos >= 0 ? "00C000" : "404040")]];

struct PlacedInternalRef<auto targetPos>
{
    InternalRefValue<targetPos> pointer;
    if (targetPos != -1)
        u8 target @ targetPos [[color("00FF80")]];
};

struct InternalRef
{
    s32 targetPos = getInternalRefTargetPos($);
    InternalRefValue<targetPos> pointer;
    if (targetPos != -1)
        u8 target @ targetPos [[highlight_hidden]];
} [[format("formatInternalRef")]];

fn getInternalRefTargetPos(u32 refPos)
{
    s32 refIdx = getRefIndex(refPos);
    if (refIdx < 0)
        return -1;
       
    return gResourceBodyPos + refDefinitions.internalRefs[refIdx].targetOffset;
};

fn formatInternalRef(auto reference)
{
    if (reference.targetPos == -1)
        return "null";
    
    return std::format("0x{:X}", reference.targetPos);
};

struct InternalRefDefinition
{
    u32 refOffset;
    u32 targetOffset;
    setRefIndex(gResourceBodyPos + refOffset, std::core::array_index());
    if (revealRefs)
        PlacedInternalRef<gResourceBodyPos + targetOffset> reference @ gResourceBodyPos + refOffset;
};

struct WideExternalRefDefinition
{
    u32 referenceOffset;
    ResourceType targetType;
    padding[3];
    u32 targetId;
    u32 targetOffset;
    u64 pointer @ bodyOffset + referenceOffset;
};

struct ExternalRef
{
    ResourceType resourceType = getExternalRefResourceType($);
    u64 resourceId;
} [[sealed, format_read("formatExternalRef"), format_write("parseExternalRef"), color(this.resourceType != ResourceType::NONE ? "C00000" : "404040")]];

fn getExternalRefResourceType(u32 refPos)
{
    s32 refIdx = getRefIndex(refPos);
    if (refIdx < 0)
        return ResourceType::NONE;
       
    return refDefinitions.packedExternalRefs[refIdx].value.resourceType;
};

struct PlacedExternalRef<auto resourceType>
{
    ResourceType resourceType = resourceType;
    u64 resourceId;
} [[sealed, format_read("formatExternalRef"), format_write("parseExternalRef"), color(this.resourceType != ResourceType::NONE ? "C00000" : "404040")]];

fn formatExternalRef(auto reference)
{
    if (reference.resourceType == ResourceType::NONE)
        return "null";
    
    ResourceType resourceType = reference.resourceType;
    return std::format("{}:{}", enumToString(resourceType), reference.resourceId & 0x7FFFFFFF);
};

fn parseExternalRef(str string)
{
    s32 colonPos = std::string::index_of_char(string, ':');
    if (colonPos >= 0)
        string = std::string::substr(string, colonPos + 1, std::string::length(string) - colonPos - 1);
    
    u64 resourceId = std::string::parse_int(string, 10);
    return resourceId;
};

bitfield PackedExternalRefDefinitionValue
{
    refOffset : 25;
    ResourceType resourceType : 7;
};

struct PackedExternalRefDefinition
{
    PackedExternalRefDefinitionValue value [[inline]];
    setRefIndex(gResourceBodyPos + value.refOffset * 4, std::core::array_index());
    if (revealRefs)
        PlacedExternalRef<value.resourceType> reference @ gResourceBodyPos + value.refOffset * 4;
};

struct RefDefinitions
{
    u32 numInternalRefs;
    u32 numWideExternalRefs;
    u32 numIntPatches;
    u32 numShortPatches;
    u32 numPackedExternalRefs;
    
    gResourceBodyPos = $ + numInternalRefs*8 +
                           numWideExternalRefs*16 +
                           numIntPatches*4 +
                           numShortPatches*8 +
                           numPackedExternalRefs*4;
    
    InternalRefDefinition internalRefs[numInternalRefs];
    WideExternalRefDefinition wideExternalRefs[numWideExternalRefs];
    u32 intPatches[numIntPatches];
    u64 shortPatches[numShortPatches];
    PackedExternalRefDefinition packedExternalRefs[numPackedExternalRefs];
} [[color("0000C0")]];

struct Vector3
{
    float x, y, z;
} [[format("formatVector3"), color("00D0D0")]];

fn formatVector3(Vector3 vector)
{
    return std::format("({}, {}, {})", vector.x, vector.y, vector.z);
};

struct Vector4
{
    float x, y, z, w;
} [[format("formatVector4"), color("00D0D0")]];

fn formatVector4(Vector4 vector)
{
    return std::format("({}, {}, {}, {})", vector.x, vector.y, vector.z, vector.w);
};

struct Quaternion
{
    float x, y, z, w;
} [[format("formatQuaternion"), color("00D0D0")]];

fn formatQuaternion(Quaternion quaternion)
{
    return std::format("({}, {}, {}, {})", quaternion.w, quaternion.x, quaternion.y, quaternion.z);
};

struct Matrix
{
    Vector4 a, b, c, d;
};

namespace std
{
    namespace string
    {
        fn index_of_char(str string, char c)
        {
            u32 len = std::string::length(string);
            for (s32 i = 0, i < len, i += 1)
            {
                if (std::string::at(string, i) == c)
                    return i;
            }
            return -1;
        };
    }
}

fn enumToString(auto enumItem)
{
    str result = std::string::to_string(enumItem);
    s32 colonPos = std::string::index_of_char(result, ':');
    return std::string::substr(result, colonPos + 2, std::string::length(result) - colonPos - 2);
};
