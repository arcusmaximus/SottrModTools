#include "tr11common.hexpat"

bitfield ModelDataFlags
{
    unknown1 : 14;
    hasBlendShapes : 1;
    unknown2 : 17;
};

struct ModelDataHeader
{
    type::Magic<"Mesh"> magic;
    ModelDataFlags flags;
    u32;
    u32 numIndices;
    u32;
    u32;
    u32;
    u32;
    Vector boundingBoxMin;
    Vector boundingBoxMax;
    padding[0xF8 - $];
    u64 meshPartsPos;
    u64 meshDescriptorsPos;
    u64 boneMappingsPos;
    u64 lodLevelsPos;
    u64 indexesPos;
    u16 numMeshParts;
    u16 numMeshes;
    u16 numBoneMappings;
    u16 numLodLevels;
    u64 data2Pos;
    u32 data1Size;
    u32;
    u64 data1Pos;
    u32 numBlendShapes;
    u32;
    u64 data6Pos;
    u32;
    u32;
    u32;
    u32;
};

struct ModelLodLevel
{
    std::mem::Bytes<0x40> data;
};

struct MeshHeader
{
    u32 numParts;
    u16 numBones;
    u16;
    u64 boneIndicesPos;
    u64 vertexData1Pos;
    u64 vertexBuffer1Ptr;
    u64 vertexData2Pos;
    u64 vertexBuffer2Ptr;
    u32 vertexFormatSize;
    u32;
    u64 vertexFormatPos;
    u64 blendShapesHeaderPos;
    u32 numVertices;
    u32;
    u32;
    u32;
    u32;
    u32;
};

u32 gCurrentMeshIndex = 0;

struct MeshBoneIndices
{
    u32 boneIndices[parent.meshHeaders[gCurrentMeshIndex].numBones];
    std::mem::AlignTo<0x20>;
    gCurrentMeshIndex += 1;
};

enum VertexAttributeName : u32
{
    POSITION            = 0xD2F7D823,
    NORMAL              = 0x36F5E414,
    TESSELATION_NORMAL  = 0x3E7F6149,
    TANGENT             = 0xF1ED11C3,
    BINORMAL            = 0x64A86F01,
    SKIN_WEIGHTS        = 0x48E691C0,
    SKIN_INDICES        = 0x5156D8D3,
    COLOR1              = 0x7E7DD623,
    COLOR2              = 0x733EF0FA,
    TEXCOORD1           = 0x8317902A,
    TEXCOORD2           = 0x8E54B6F3,
    TEXCOORD3           = 0x8A95AB44,
    TEXCOORD4           = 0x94D2FB41
};

enum VertexAttributeType : u8
{
    FLOAT = 0,
    FLOAT2 = 1,
    FLOAT3 = 2,
    FLOAT4 = 3,
    R8G8B8A8_UNORM_0 = 4,
    R8G8B8A8_UNORM_1 = 5,
    R8G8B8A8_UNORM_2 = 6,
    R8G8B8A8_UNORM_3 = 7,
    R8G8B8A8_UNORM_4 = 13,
    R8G8B8A8_UNORM_5 = 22,
    R8G8B8A8_UINT_0 = 8,
    R8G8B8A8_UINT_1 = 23,
    R16G16_SINT = 9,
    R16G16B16A16_SINT = 10,
    R16G16B16A16_UINT_0 = 11,
    R16G16B16A16_UINT_1 = 24,
    R32G32B32A32_UINT = 12,
    R16G16_SNORM_0 = 14,
    R16G16_SNORM_1 = 25,
    R16G16B16A16_SNORM_0 = 15,
    R16G16B16A16_SNORM_1 = 26,
    R16G16_UNORM = 16,
    R16G16B16A16_UNORM = 17,
    R10G10B10A2_UINT = 18,
    R10G10B10A2_UNORM_0 = 19,
    R10G10B10A2_UNORM_1 = 20
};

struct VertexAttribute
{
    VertexAttributeName name;
    u16 offset;
    VertexAttributeType type;
    u8 vertexBufferIdx;
} [[format("formatVertexAttribute")]];

fn formatVertexAttribute(VertexAttribute attr)
{
    return std::string::substr(std::string::to_string(attr.name), std::string::length("VertexAttributeName::"), 50);
};

struct VertexFormat
{
    u64 hash;
    u16 numAttributes;
    u8 vertexSizes[2];
    padding[4];
    VertexAttribute attributes[numAttributes];
};

struct VertexBuffer
{
    std::mem::Bytes<
        parent.parent.meshHeaders[gCurrentMeshIndex].numVertices *
        parent.vertexFormat.vertexSizes[gCurrentVertexBufferIndex]
    > buffer;
    std::mem::AlignTo<0x20>;
    gCurrentVertexBufferIndex += 1;
} [[inline]];

u32 gCurrentVertexBufferIndex = 0;

struct BlendShapes
{
    u32 numBlendShapes;
    u32 numVertexOffsets;
    u32 field_8;
    u32 positionsOffset;
    u32 normalsOffset;
    u32 colorsOffset;
    u32 segmentsOffset;
    u32 vertexIndicesOffset;
    u64 blendShapeBitmaskPtr;
    u64 blendShapeDataPtr;
    u64 blendShapeSrvsPtr;
    std::mem::AlignTo<0x20>;
    
    u32 supportedBlendShapeBitmasks[(parent.parent.header.numBlendShapes + 0x1F) >> 5];
    std::mem::AlignTo<0x20>;
    
    std::mem::Bytes<((parent.parent.meshHeaders[gCurrentMeshIndex].numVertices + 0x3F) >> 6) * numBlendShapes * 4> segments;
    std::mem::AlignTo<0x20>;
    
    std::mem::Bytes<numVertexOffsets * 4> positionOffsets;
    std::mem::AlignTo<0x20>;
    
    std::mem::Bytes<numVertexOffsets * 4> normalOffsets;
    std::mem::AlignTo<0x20>;
    
    std::mem::Bytes<numVertexOffsets * 4> colorOffsets;
    std::mem::AlignTo<0x20>;
    
    std::mem::Bytes<numVertexOffsets> vertexIndices;
    std::mem::AlignTo<0x20>;
};

struct MeshContent
{
    VertexFormat vertexFormat;
    std::mem::AlignTo<0x20>;
    
    gCurrentVertexBufferIndex = 0;
    VertexBuffer vertexBuffers[2];
    
    if (parent.header.flags.hasBlendShapes == 1)
        BlendShapes blendShapes;
    
    gCurrentMeshIndex += 1;
};

struct MeshPart
{
    Vector field_0;
    u32 firstIndexIdx;
    u32 numTriangles;
    u32 field_18;
    u32 flags;
    u32 field_20;
    u32 field_24;
    u32 field_28;
    u16 lodLevelPlus1;
    u16 field_2E;
    u64 materialIdx;
    u64 textureIndices[5];
};

struct ModelData
{
    ModelDataHeader header;
    std::mem::Bytes<header.data1Size> data1;
    std::assert(header.data2Pos == 0xFFFFFFFF, "data2Pos is expected to be empty");
    ModelLodLevel lodLevels[header.numLodLevels];
    
    u32 boneMappings[header.numBoneMappings];
    std::mem::AlignTo<0x20>;
    
    MeshHeader meshHeaders[header.numMeshes];
    
    gCurrentMeshIndex = 0;
    MeshBoneIndices meshBoneIndices[header.numMeshes];
    
    gCurrentMeshIndex = 0;
    MeshContent meshContents[header.numMeshes];
    
    if (header.data6Pos != 0)
        std::mem::Bytes<header.numBlendShapes * 0x40>;
    
    std::mem::Bytes<header.numIndices * 2> indices;
    std::mem::AlignTo<0x20>;
    
    MeshPart meshParts[header.numMeshParts];
};

ModelData modelData @ 0;
