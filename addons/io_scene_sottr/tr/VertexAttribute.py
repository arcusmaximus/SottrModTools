from io_scene_sottr.util.CStruct import CByte, CStruct, CUInt, CUShort

class VertexAttribute(CStruct):
    name_hash: CUInt
    offset: CUShort
    format: CByte
    vertex_buffer_idx: CByte
