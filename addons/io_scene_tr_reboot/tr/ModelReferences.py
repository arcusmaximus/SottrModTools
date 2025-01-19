from abc import abstractmethod
from io_scene_tr_reboot.tr.Enumerations import ResourceType
from io_scene_tr_reboot.tr.ResourceBuilder import ResourceBuilder
from io_scene_tr_reboot.tr.ResourceKey import ResourceKey
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader
from io_scene_tr_reboot.tr.ResourceReference import ResourceReference
from io_scene_tr_reboot.util.SlotsBase import SlotsBase

class ModelReferences(SlotsBase):
    model_data_resource: ResourceReference | None
    texture_resources: list[ResourceKey | None]
    material_resources: list[ResourceKey | None]

    def __init__(self, model_data_id: int | None = None) -> None:
        if model_data_id is not None:
            self.model_data_resource = ResourceReference(ResourceType.MODEL, model_data_id, 0)
        else:
            self.model_data_resource = None

        self.texture_resources = []
        self.material_resources = []

    @abstractmethod
    def read(self, reader: ResourceReader) -> None: ...

    @abstractmethod
    def write(self, writer: ResourceBuilder) -> None: ...
