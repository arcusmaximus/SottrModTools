from ctypes import sizeof
from typing import Sequence
from io_scene_sottr.tr.BlendShape import BlendShape
from io_scene_sottr.tr.MeshPart import MeshPart
from io_scene_sottr.tr.ModelDataHeader import ModelDataHeader
from io_scene_sottr.tr.Vertex import Vertex
from io_scene_sottr.tr.VertexFormat import VertexFormat
from io_scene_sottr.util.BinaryReader import BinaryReader
from io_scene_sottr.util.BinaryWriter import BinaryWriter
from io_scene_sottr.util.CStruct import CInt, CLong, CShort, CStruct
from io_scene_sottr.util.SlotsBase import SlotsBase

class _MeshHeader(CStruct):
    num_parts: CInt
    num_bones: CShort
    field_6: CShort
    bone_indices_ptr: CLong
    vertex_data_1_ptr: CLong
    vertex_buffer_1_ptr: CLong
    vertex_data_2_ptr: CLong
    vertex_buffer_2_ptr: CLong
    vertex_format_size: CInt
    field_34: CInt
    vertex_format_ptr: CLong
    blend_shapes_header_ptr: CLong
    num_vertices: CInt
    field_4C: CInt
    field_50: CInt
    field_54: CInt
    field_58: CInt
    field_5C: CInt

assert(sizeof(_MeshHeader) == 0x60)

class Mesh(SlotsBase):
    model_data_header: ModelDataHeader
    mesh_header: _MeshHeader

    vertex_format: VertexFormat
    vertices: list[Vertex]
    bone_indices: Sequence[int]
    parts: list[MeshPart]
    blend_shapes: list[BlendShape | None]

    def __init__(self, model_data_header: ModelDataHeader) -> None:
        self.model_data_header = model_data_header
        self.mesh_header = _MeshHeader()
        self.vertex_format = VertexFormat()
        self.bone_indices = []
        self.parts = []
        self.vertices = []
        self.blend_shapes = []

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
            self.blend_shapes = BlendShape.read(reader, self.model_data_header, self.mesh_header.num_vertices)

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
        
        if self.model_data_header.flags & 0x4000:
            BlendShape.write(writer, self.blend_shapes, self.mesh_header.num_vertices)
