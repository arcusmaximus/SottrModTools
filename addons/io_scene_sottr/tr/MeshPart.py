from ctypes import sizeof
from typing import Literal, Sequence

from mathutils import Vector
from io_scene_sottr.util.CStruct import CArray, CFlag, CInt, CLong, CShort, CStruct

class MeshPart(CStruct):
    field_0: Vector
    first_index_idx: CInt
    num_triangles: CInt
    field_18: CInt
    flags: CInt
    field_20: CInt
    field_24: CInt
    field_28: CInt
    lod_level: CShort
    field_2E: CShort
    material_idx: CLong
    texture_indices: CArray[CLong, Literal[5]]

    has_8_weights_per_vertex      = CFlag("flags", 0x8000)
    has_16bit_skin_indices   = CFlag("flags", 0x10000)
    
    indices: Sequence[int]

    _ignored_fields_ = ("indices",)

assert(sizeof(MeshPart) == 0x60)
