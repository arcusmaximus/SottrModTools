from typing import Generic, Protocol, Sequence, TypeVar
from io_scene_tr_reboot.tr.BlendShape import BlendShape
from io_scene_tr_reboot.tr.IModelDataHeader import IModelDataHeader
from io_scene_tr_reboot.tr.MeshPart import IMeshPart
from io_scene_tr_reboot.tr.Vertex import Vertex
from io_scene_tr_reboot.tr.VertexAttributeTypes import VertexAttributeTypes
from io_scene_tr_reboot.tr.VertexFormat import VertexFormat

class IMesh(Protocol):
    model_data_header: IModelDataHeader
    vertex_format: VertexFormat
    vertices: list[Vertex]
    bone_indices: Sequence[int]
    parts: list[IMeshPart]
    blend_shapes: list[BlendShape | None]

    def clone(self) -> "IMesh": ...

TModelDataHeader = TypeVar("TModelDataHeader", bound = IModelDataHeader)
TMeshPart = TypeVar("TMeshPart", bound = IMeshPart)
class MeshBase(IMesh, Generic[TModelDataHeader, TMeshPart]):
    model_data_header: TModelDataHeader
    vertex_format: VertexFormat
    vertices: list[Vertex]
    bone_indices: Sequence[int]
    parts: list[TMeshPart]
    blend_shapes: list[BlendShape | None]

    def __init__(self, model_data_header: TModelDataHeader) -> None:
        self.model_data_header = model_data_header  # type: ignore
        self.vertex_format = VertexFormat(self.vertex_attribute_types)
        self.vertices = []
        self.bone_indices = []
        self.parts = []
        self.blend_shapes = []

    @property
    def vertex_attribute_types(self) -> VertexAttributeTypes: ...

    def clone(self) -> IMesh:
        new_mesh = self.__class__(self.model_data_header)
        new_mesh.assign(self)
        return new_mesh

    def assign(self, other: IMesh) -> None:
        self.vertex_format = other.vertex_format
        self.vertices = other.vertices
        self.bone_indices = other.bone_indices
        self.parts = other.parts                    # type: ignore
        self.blend_shapes = other.blend_shapes
