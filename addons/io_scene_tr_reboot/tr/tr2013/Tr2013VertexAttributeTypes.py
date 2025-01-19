from typing import ClassVar
from io_scene_tr_reboot.tr.VertexAttributeTypes import IVertexAttributeTypeIds, VertexAttributeTypes

class Tr2013VertexAttributeTypeIds(IVertexAttributeTypeIds):
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
    ubyte4n = 11
    short2n = 12
    short4n = 13
    ushort2n = 14
    ushort4n = 15
    udec3 = 16
    dec3n = 17
    weightsub4n = 18
    texcoords2 = 19
    texcoords4 = 20

    ushort4 = None
    uint4 = None
    udec3n = None
    weightsub4 = None
    weightsuhalf4 = None

class Tr2013VertexAttributeTypes(VertexAttributeTypes):
    instance: ClassVar["Tr2013VertexAttributeTypes"]

    def __init__(self) -> None:
        super().__init__(Tr2013VertexAttributeTypeIds())

Tr2013VertexAttributeTypes.instance = Tr2013VertexAttributeTypes()
