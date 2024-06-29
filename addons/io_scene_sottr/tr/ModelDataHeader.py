from ctypes import sizeof
from typing import Literal
from mathutils import Vector
from io_scene_sottr.util.CStruct import CArray, CByte, CFlag, CInt, CLong, CShort, CStruct

class ModelDataHeader(CStruct):
    signature:      CInt
    flags:          CInt
    field_8:        CInt
    num_indexes:    CInt
    field_10:       CInt
    field_14:       CInt
    field_18:       CInt
    field_1C:       CInt
    bound_box_min:  Vector
    bound_box_max:  Vector
    field_40:       CLong
    field_48:       CLong
    field_50:       CInt
    field_54:       CInt
    field_58:       CInt
    field_5C:       CInt
    field_60:       CInt
    field_64:       CInt
    field_68:       CInt
    field_6C:       CInt
    is_skinned:     CInt
    field_74:       CInt
    field_78:       CInt
    field_7C:       CInt
    field_80:       CInt
    field_84:       CInt
    field_88:       CInt
    field_8C:       CArray[CByte, Literal[92]]
    field_E8:       CLong
    field_F0:       CLong

    mesh_parts_offet:           CLong
    mesh_descriptors_offset:    CLong
    bone_mappings_offset:       CLong
    lod_levels_offset:          CLong
    index_data_offset:          CLong
    num_mesh_parts:             CShort
    num_meshes:                 CShort
    num_bone_mappings:          CShort
    num_lod_levels:             CShort
    data2_offset:               CLong
    data1_size:                 CInt
    field_134:                  CInt
    data1_offset:               CLong
    num_blend_shapes:           CInt
    field_144:                  CInt
    data6_offset:               CLong
    field_150:                  CInt
    field_154:                  CInt
    field_158:                  CInt
    field_15C:                  CInt

    has_vertex_weights = CFlag("flags", 1)
    has_blend_shapes = CFlag("flags", 0x4000)

assert(sizeof(ModelDataHeader) == 0x160)