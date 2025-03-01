from io_scene_tr_reboot.tr.Enumerations import ResourceType
from io_scene_tr_reboot.util.SlotsBase import SlotsBase

class ResourceKey(SlotsBase):
    type: ResourceType
    id: int

    def __init__(self, type: ResourceType, id: int) -> None:
        self.type = type
        self.id = id

    def __str__(self) -> str:
        return f"{self.type}:{self.id}"

    def __hash__(self) -> int:
        return hash((self.type, self.id))

    def __eq__(self, value: object) -> bool:
        return isinstance(value, ResourceKey) and self.type == value.type and self.id == value.id
