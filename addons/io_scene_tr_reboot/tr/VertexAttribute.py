from ctypes import sizeof
from io_scene_tr_reboot.tr.VertexAttributeType import VertexAttributeType
from io_scene_tr_reboot.util.CStruct import CByte, CStruct, CUInt, CUShort

class VertexAttribute(CStruct):
    name_hash: CUInt
    offset: CUShort
    type_id: CByte
    vertex_buffer_idx: CByte

    type: VertexAttributeType
    _ignored_fields_ = ("type",)

assert(sizeof(VertexAttribute) == 8)
