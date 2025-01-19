from ctypes import sizeof
from typing import Literal, cast
from io_scene_tr_reboot.tr.BlendShape import BlendShape
from io_scene_tr_reboot.tr.Mesh import IMesh, MeshBase
from io_scene_tr_reboot.tr.Vertex import Vertex
from io_scene_tr_reboot.tr.VertexAttributeTypes import VertexAttributeTypes
from io_scene_tr_reboot.tr.shadow.ShadowMeshPart import ShadowMeshPart
from io_scene_tr_reboot.tr.shadow.ShadowModelDataHeader import ShadowModelDataHeader
from io_scene_tr_reboot.tr.shadow.ShadowVertexAttributeTypes import ShadowVertexAttributeTypes
from io_scene_tr_reboot.util.BinaryReader import BinaryReader
from io_scene_tr_reboot.util.BinaryWriter import BinaryWriter
from io_scene_tr_reboot.util.CStruct import CArray, CInt, CLong, CShort, CStruct64

class _VertexBuffer(CStruct64):
    offset:     CLong
    pointer:    CLong

class _MeshHeader(CStruct64):
    num_parts:                  CInt
    num_bones:                  CShort
    field_6:                    CShort
    bone_indices_ptr:           CLong
    vertex_buffers:             CArray[_VertexBuffer, Literal[2]]
    vertex_format_size:         CInt
    field_34:                   CInt
    vertex_format_ptr:          CLong
    blend_shapes_header_ptr:    CLong
    num_vertices:               CInt
    field_4C:                   CInt
    field_50:                   CInt
    field_54:                   CInt
    field_58:                   CInt
    field_5C:                   CInt

assert(sizeof(_MeshHeader) == 0x60)

class ShadowMesh(MeshBase[ShadowModelDataHeader, ShadowMeshPart]):
    mesh_header: _MeshHeader

    def __init__(self, model_data_header: ShadowModelDataHeader) -> None:
        super().__init__(model_data_header)
        self.mesh_header = _MeshHeader()

    @property
    def vertex_attribute_types(self) -> VertexAttributeTypes:
        return ShadowVertexAttributeTypes.instance

    def assign(self, other: IMesh) -> None:
        super().assign(other)

        other = cast(ShadowMesh, other)
        self.model_data_header = other.model_data_header
        self.mesh_header = other.mesh_header

    def read_header(self, reader: BinaryReader) -> None:
        self.mesh_header = reader.read_struct(_MeshHeader)

    def read_bone_indices(self, reader: BinaryReader) -> None:
        self.bone_indices = reader.read_int32_list(self.mesh_header.num_bones)
        reader.align(0x20)

    def read_content(self, reader: BinaryReader) -> None:
        vertex_format_start_pos = reader.position
        self.vertex_format.read(reader)
        if reader.position != vertex_format_start_pos + self.mesh_header.vertex_format_size:
            raise Exception("Vertex format doesn't match size")

        reader.align(0x20)

        vertex_buffers: list[memoryview] = []
        for vertex_size in self.vertex_format.vertex_sizes:
            vertex_buffers.append(reader.read_bytes(self.mesh_header.num_vertices * vertex_size))
            reader.align(0x20)

        for i in range(self.mesh_header.num_vertices):
            vertex: Vertex = Vertex()
            vertex.read(vertex_buffers, i, self.vertex_format)
            self.vertices.append(vertex)

        if self.model_data_header.has_blend_shapes:
            self.blend_shapes = BlendShape.read(reader, 0, self.model_data_header.num_blend_shapes, None, self.mesh_header.num_vertices)

    def write_header(self, writer: BinaryWriter) -> None:
        self.mesh_header.num_parts = len(self.parts)
        self.mesh_header.num_bones = len(self.bone_indices)
        self.mesh_header.vertex_format_size = self.vertex_format.size
        self.mesh_header.num_vertices = len(self.vertices)
        writer.write_struct(self.mesh_header)

    def write_bone_indices(self, writer: BinaryWriter) -> None:
        writer.write_int32_list(self.bone_indices)
        writer.align(0x20)

    def write_content(self, writer: BinaryWriter) -> None:
        self.vertex_format.write(writer)
        writer.align(0x20)

        vertex_buffers: list[bytearray] = [bytearray(vertex_size * len(self.vertices)) for vertex_size in self.vertex_format.vertex_sizes]
        for i in range(len(self.vertices)):
            self.vertices[i].write(vertex_buffers, i, self.vertex_format)

        for vertex_buffer in vertex_buffers:
            writer.write_bytes(vertex_buffer)
            writer.align(0x20)

        if self.model_data_header.has_blend_shapes:
            BlendShape.write(writer, 0, self.blend_shapes, self.mesh_header.num_vertices)
