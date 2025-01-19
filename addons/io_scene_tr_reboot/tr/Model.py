from abc import abstractmethod
from typing import Generic, Protocol, TypeVar
from io_scene_tr_reboot.tr.Mesh import IMesh
from io_scene_tr_reboot.tr.MeshPart import IMeshPart
from io_scene_tr_reboot.tr.IModelDataHeader import IModelDataHeader
from io_scene_tr_reboot.tr.ModelReferences import ModelReferences
from io_scene_tr_reboot.tr.ResourceBuilder import ResourceBuilder
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader

class IModel(Protocol):
    id: int
    refs: ModelReferences
    header: IModelDataHeader
    meshes: list[IMesh]

    def read(self, reader: ResourceReader) -> None: ...
    def write(self, writer: ResourceBuilder) -> None: ...

TModelReferences = TypeVar("TModelReferences", bound = ModelReferences)
TModelDataHeader = TypeVar("TModelDataHeader", bound = IModelDataHeader)
TMesh = TypeVar("TMesh", bound = IMesh)
TMeshPart = TypeVar("TMeshPart", bound = IMeshPart)
class Model(IModel, Generic[TModelReferences, TModelDataHeader, TMesh, TMeshPart]):
    id: int
    refs: TModelReferences
    header: TModelDataHeader            # type: ignore
    meshes: list[TMesh]

    def __init__(self, model_id: int, refs: TModelReferences) -> None:
        self.id = model_id
        self.refs = refs                # type: ignore
        self.meshes = []                # type: ignore
        self.material_resources = []

    @abstractmethod
    def read(self, reader: ResourceReader) -> None: ...

    @abstractmethod
    def write(self, writer: ResourceBuilder) -> None: ...
