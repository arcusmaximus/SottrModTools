from typing import ClassVar
from io_scene_tr_reboot.tr.VertexAttributeTypes import IVertexAttributeTypeIds, VertexAttributeTypes

class ShadowVertexAttributeTypeIds(IVertexAttributeTypeIds):
    float1 = 0
    float2 = 1
    float3 = 2
    float4 = 3
    color32 = 4
    vectorc32 = 5
    weightsc32 = 6
    indicesc32 = 7
    ubyte4 = 8
    short2 = 9
    short4 = 10
    ushort4 = 11
    uint4 = 12
    ubyte4n = 13
    short2n = 14
    short4n = 15
    ushort2n = 16
    ushort4n = 17
    udec3 = 18
    udec3n = 19
    dec3n = 20
    dec4n = 21
    weightsub4n = 22
    weightsub4 = 23
    weightsuhalf4 = 24
    texcoords2 = 25
    texcoords4 = 26

class ShadowVertexAttributeTypes(VertexAttributeTypes):
    instance: ClassVar["ShadowVertexAttributeTypes"]

    def __init__(self) -> None:
        super().__init__(ShadowVertexAttributeTypeIds())

ShadowVertexAttributeTypes.instance = ShadowVertexAttributeTypes()
