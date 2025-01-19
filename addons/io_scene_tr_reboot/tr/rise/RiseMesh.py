from ctypes import sizeof
from typing import TYPE_CHECKING, Literal
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader
from io_scene_tr_reboot.tr.VertexAttributeTypes import VertexAttributeTypes
from io_scene_tr_reboot.tr.rise.RiseMeshPart import RiseMeshPart
from io_scene_tr_reboot.tr.rise.RiseModelDataHeader import RiseModelDataHeader
from io_scene_tr_reboot.tr.rise.RiseVertexAttributeTypes import RiseVertexAttributeTypes
from io_scene_tr_reboot.tr.tr2013.Tr2013Mesh import ITr2013MeshHeader, Tr2013MeshBase
from io_scene_tr_reboot.util.CStruct import CArray, CInt, CLong, CShort, CStruct64

class _VertexBuffer(CStruct64):
    offset:     CLong
    pointer:    CLong

class _MeshHeader(CStruct64, ITr2013MeshHeader if TYPE_CHECKING else object):
    num_parts:                      CInt
    num_bones:                      CShort
    field_6:                        CShort
    bone_indices_offset:            CLong
    vertex_buffers:                 CArray[_VertexBuffer, Literal[2]]       # type: ignore
    vertex_format_offset:           CLong
    blend_shapes_header_offset:     CLong
    num_vertices:                   CInt
    non_pretesselation_vertices:    CInt
    first_index_idx:                CInt
    num_triangles:                  CInt

assert(sizeof(_MeshHeader) == 0x50)

class RiseMesh(Tr2013MeshBase[RiseModelDataHeader, RiseMeshPart]):
    def __init__(self, model_data_header: RiseModelDataHeader) -> None:
        super().__init__(model_data_header)

    @property
    def vertex_attribute_types(self) -> VertexAttributeTypes:
        return RiseVertexAttributeTypes.instance

    def create_mesh_header(self) -> ITr2013MeshHeader:
        return _MeshHeader()

    def read_mesh_header(self, reader: ResourceReader) -> ITr2013MeshHeader:
        return reader.read_struct(_MeshHeader)
