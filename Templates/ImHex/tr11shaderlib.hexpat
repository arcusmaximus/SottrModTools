#include <std/io.pat>
#include <std/mem.pat>

enum ShaderType : u32
{
    PIXEL = 1,
    VERTEX,
    HULL,
    DOMAIN,
    COMPUTE,
    GEOMETRY,
    RT
};

struct Shader
{
    padding[4];
    u32 size [[color("0000C0")]];
    u64 nameHash [[color("D0D000")]];
    std::mem::Bytes<size - 0x10> data [[color("606060")]];
};

struct ShaderOffset
{
    u32 positionMinus4 [[color("00C000")]];
    Shader shader @ positionMinus4 + 4;
} [[format("formatShaderOffset")]];

fn formatShaderOffset(ShaderOffset reference)
{
    return std::format("0x{:X}", reference.positionMinus4 + 4);
};

struct ShaderLib
{
    ShaderType type [[color("D0D000")]];
    u32 numShadersTimes4 [[color("0000C0")]];
    padding[4];
    ShaderOffset shaderOffsets[numShadersTimes4 / 4];
};

ShaderLib lib @ 0;
