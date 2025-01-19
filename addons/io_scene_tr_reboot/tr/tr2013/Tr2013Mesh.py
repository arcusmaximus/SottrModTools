from ctypes import sizeof
from typing import TYPE_CHECKING, Literal, Protocol, Sequence, TypeVar, cast
from io_scene_tr_reboot.tr.BlendShape import BlendShape
from io_scene_tr_reboot.tr.Mesh import IMesh, MeshBase
from io_scene_tr_reboot.tr.MeshPart import IMeshPart
from io_scene_tr_reboot.tr.IModelDataHeader import IModelDataHeader
from io_scene_tr_reboot.tr.ResourceBuilder import ResourceBuilder
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader
from io_scene_tr_reboot.tr.Vertex import Vertex
from io_scene_tr_reboot.tr.VertexAttributeTypes import VertexAttributeTypes
from io_scene_tr_reboot.tr.tr2013.Tr2013MeshPart import Tr2013MeshPart
from io_scene_tr_reboot.tr.tr2013.Tr2013ModelDataHeader import Tr2013ModelDataHeader
from io_scene_tr_reboot.tr.tr2013.Tr2013VertexAttributeTypes import Tr2013VertexAttributeTypes
from io_scene_tr_reboot.util.CStruct import CArray, CInt, CShort, CStruct, CStruct32

class ITr2013VertexBuffer(Protocol):
    offset:     int
    pointer:    int

class ITr2013MeshHeader(Protocol):
    num_parts: int
    num_bones: int
    bone_indices_offset: int
    vertex_buffers: Sequence[ITr2013VertexBuffer]
    vertex_format_offset: int
    num_vertices: int
    blend_shapes_header_offset: int

class ITr2013Mesh(IMesh, Protocol):
    mesh_header: ITr2013MeshHeader

    def read(self, reader: ResourceReader, model_data_header_pos: int, blend_shape_names: list[str] | None) -> None: ...

    def write_header(self, writer: ResourceBuilder) -> None: ...
    def write_bone_indices(self, writer: ResourceBuilder, model_data_header_pos: int) -> None: ...
    def write_content(self, writer: ResourceBuilder, model_data_header_pos: int) -> None: ...

class Tr2013VertexBuffer(CStruct32, ITr2013VertexBuffer if TYPE_CHECKING else object):
    offset:     CInt
    pointer:    CInt

class Tr2013MeshHeader(CStruct32, ITr2013MeshHeader if TYPE_CHECKING else object):
    num_parts:                      CInt
    lod_level:                      CShort
    num_bones:                      CShort
    bone_indices_offset:            CInt
    vertex_buffers:                 CArray[Tr2013VertexBuffer, Literal[2]]  # pyright: ignore[reportIncompatibleVariableOverride]
    vertex_format_offset:           CInt
    num_vertices:                   CInt
    non_pretesselation_vertices:    CInt
    first_index_idx:                CInt
    num_triangles:                  CInt

    blend_shapes_header_offset: int
    _ignored_fields_ = ("blend_shapes_header_offset",)

assert(sizeof(Tr2013MeshHeader) == 0x30)

TModelDataHeader = TypeVar("TModelDataHeader", bound = IModelDataHeader)
TMeshPart = TypeVar("TMeshPart", bound = IMeshPart)
class Tr2013MeshBase(ITr2013Mesh, MeshBase[TModelDataHeader, TMeshPart]):
    mesh_header: ITr2013MeshHeader

    def __init__(self, model_data_header: TModelDataHeader) -> None:
        super().__init__(model_data_header)
        self.model_data_header = model_data_header
        self.mesh_header = self.create_mesh_header()

    def assign(self, other: IMesh) -> None:
        super().assign(other)

        other = cast(Tr2013MeshBase[TModelDataHeader, TMeshPart], other)
        self.model_data_header = other.model_data_header
        self.mesh_header = other.mesh_header

    def read(self, reader: ResourceReader, model_data_header_pos: int, blend_shape_names: list[str] | None) -> None:
        self.mesh_header = self.read_mesh_header(reader)

        return_pos = reader.position

        reader.position = model_data_header_pos + self.mesh_header.bone_indices_offset
        self.bone_indices = reader.read_int32_list(self.mesh_header.num_bones)

        reader.position = model_data_header_pos + self.mesh_header.vertex_format_offset
        self.vertex_format.read(reader)

        vertex_buffers: list[memoryview] = []
        for i, vertex_buffer in enumerate(self.mesh_header.vertex_buffers):
            reader.position = model_data_header_pos + vertex_buffer.offset
            vertex_buffers.append(reader.read_bytes(self.mesh_header.num_vertices * self.vertex_format.vertex_sizes[i]))

        for i in range(self.mesh_header.num_vertices):
            vertex = Vertex()
            vertex.read(vertex_buffers, i, self.vertex_format)
            self.vertices.append(vertex)

        if self.model_data_header.has_blend_shapes:
            reader.position = model_data_header_pos + self.mesh_header.blend_shapes_header_offset
            self.blend_shapes = BlendShape.read(reader, model_data_header_pos, self.model_data_header.num_blend_shapes, blend_shape_names, self.mesh_header.num_vertices)

        reader.position = return_pos

    def write_header(self, writer: ResourceBuilder) -> None:
        self.mesh_header.num_parts = len(self.parts)
        self.mesh_header.num_bones = len(self.bone_indices)
        self.mesh_header.num_vertices = len(self.vertices)
        writer.write_struct(cast(CStruct, self.mesh_header))

    def write_bone_indices(self, writer: ResourceBuilder, model_data_header_pos: int) -> None:
        self.mesh_header.bone_indices_offset = writer.position - model_data_header_pos
        writer.write_int32_list(self.bone_indices)
        writer.align(0x20)

    def write_content(self, writer: ResourceBuilder, model_data_header_pos: int) -> None:
        self.mesh_header.vertex_format_offset = writer.position - model_data_header_pos
        self.vertex_format.write(writer)
        writer.align(0x20)

        vertex_buffers: list[bytearray] = [bytearray(vertex_size * len(self.vertices)) for vertex_size in self.vertex_format.vertex_sizes]
        for i in range(len(self.vertices)):
            self.vertices[i].write(vertex_buffers, i, self.vertex_format)

        for i, vertex_buffer in enumerate(vertex_buffers):
            self.mesh_header.vertex_buffers[i].offset = writer.position - model_data_header_pos
            writer.write_bytes(vertex_buffer)
            writer.align(0x20)

        if self.model_data_header.has_blend_shapes:
            self.mesh_header.blend_shapes_header_offset = writer.position - model_data_header_pos
            BlendShape.write(writer, model_data_header_pos, self.blend_shapes, self.mesh_header.num_vertices)

    def create_mesh_header(self) -> ITr2013MeshHeader: ...

    def read_mesh_header(self, reader: ResourceReader) -> ITr2013MeshHeader: ...

class Tr2013Mesh(Tr2013MeshBase[Tr2013ModelDataHeader, Tr2013MeshPart]):
    def __init__(self, model_data_header: Tr2013ModelDataHeader) -> None:
        super().__init__(model_data_header)

    @property
    def vertex_attribute_types(self) -> VertexAttributeTypes:
        return Tr2013VertexAttributeTypes.instance

    def create_mesh_header(self) -> ITr2013MeshHeader:
        return Tr2013MeshHeader()

    def read_mesh_header(self, reader: ResourceReader) -> ITr2013MeshHeader:
        return reader.read_struct(Tr2013MeshHeader)
