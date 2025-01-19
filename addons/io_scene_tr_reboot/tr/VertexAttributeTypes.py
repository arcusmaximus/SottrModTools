from typing import Protocol, TypeVar
from io_scene_tr_reboot.tr.VertexAttributeType import VertexAttributeType, VertexAttributeType_FLOAT1, VertexAttributeType_FLOAT2, VertexAttributeType_FLOAT3, VertexAttributeType_FLOAT4, VertexAttributeType_R10G10B10A2_UINT, VertexAttributeType_R10G10B10A2_UNORM, VertexAttributeType_R16G16_SINT, VertexAttributeType_R16G16_SNORM, VertexAttributeType_R16G16_UNORM, VertexAttributeType_R16G16B16A16_SINT, VertexAttributeType_R16G16B16A16_SNORM, VertexAttributeType_R16G16B16A16_UINT, VertexAttributeType_R16G16B16A16_UNORM, VertexAttributeType_R32G32B32A32_UINT, VertexAttributeType_R8G8B8A8_UINT, VertexAttributeType_R8G8B8A8_UNORM
from io_scene_tr_reboot.util.Enumerable import Enumerable

T = TypeVar("T")
class IVertexAttributeTypes(Protocol[T]):
    float1: T
    float2: T
    float3: T
    float4: T
    color32: T
    vectorc32: T
    weightsc32: T
    indicesc32: T
    ubyte4: T
    short2: T
    short4: T
    ushort4: T | None
    uint4: T | None
    ubyte4n: T
    short2n: T
    short4n: T
    ushort2n: T
    ushort4n: T
    udec3: T
    udec3n: T | None
    dec3n: T
    weightsub4n: T
    weightsub4: T | None
    weightsuhalf4: T | None
    texcoords2: T
    texcoords4: T

class IVertexAttributeTypeIds(IVertexAttributeTypes[int], Protocol):
    pass

class VertexAttributeTypes(IVertexAttributeTypes[VertexAttributeType]):
    __lookup: dict[int, VertexAttributeType]

    def __init__(self, ids: IVertexAttributeTypeIds) -> None:
        self.float1         = VertexAttributeType_FLOAT1(ids.float1)
        self.float2         = VertexAttributeType_FLOAT2(ids.float2)
        self.float3         = VertexAttributeType_FLOAT3(ids.float3)
        self.float4         = VertexAttributeType_FLOAT4(ids.float4)

        self.color32        = VertexAttributeType_R8G8B8A8_UNORM(ids.color32)
        self.vectorc32      = VertexAttributeType_R8G8B8A8_UNORM(ids.vectorc32)
        self.ubyte4n        = VertexAttributeType_R8G8B8A8_UNORM(ids.ubyte4n)
        self.weightsub4n    = VertexAttributeType_R8G8B8A8_UNORM(ids.weightsub4n)

        self.weightsc32     = VertexAttributeType_R8G8B8A8_UINT(ids.weightsc32)
        self.indicesc32     = VertexAttributeType_R8G8B8A8_UINT(ids.indicesc32)
        self.ubyte4         = VertexAttributeType_R8G8B8A8_UINT(ids.ubyte4)
        self.weightsub4     = ids.weightsub4 is not None and VertexAttributeType_R8G8B8A8_UINT(ids.weightsub4) or None

        self.short2         = VertexAttributeType_R16G16_SINT(ids.short2)

        self.short4         = VertexAttributeType_R16G16B16A16_SINT(ids.short4)

        self.ushort4        = ids.ushort4 is not None and VertexAttributeType_R16G16B16A16_UINT(ids.ushort4) or None
        self.weightsuhalf4  = ids.weightsuhalf4 is not None and VertexAttributeType_R16G16B16A16_UINT(ids.weightsuhalf4) or None

        self.uint4          = ids.uint4 is not None and VertexAttributeType_R32G32B32A32_UINT(ids.uint4) or None

        self.short2n        = VertexAttributeType_R16G16_SNORM(ids.short2n)
        self.texcoords2     = VertexAttributeType_R16G16_SNORM(ids.texcoords2)

        self.short4n        = VertexAttributeType_R16G16B16A16_SNORM(ids.short4n)
        self.texcoords4     = VertexAttributeType_R16G16B16A16_SNORM(ids.texcoords4)

        self.ushort2n       = VertexAttributeType_R16G16_UNORM(ids.ushort2n)

        self.ushort4n       = VertexAttributeType_R16G16B16A16_UNORM(ids.ushort4n)

        self.udec3          = VertexAttributeType_R10G10B10A2_UINT(ids.udec3)

        self.udec3n         = ids.udec3n is not None and VertexAttributeType_R10G10B10A2_UNORM(ids.udec3n) or None
        self.dec3n          = VertexAttributeType_R10G10B10A2_UNORM(ids.dec3n)

        self.__lookup = Enumerable(self.__dict__.values()).of_type(VertexAttributeType).to_dict(lambda t: t.id)

    def get(self, id: int) -> VertexAttributeType | None:
        return self.__lookup.get(id)
