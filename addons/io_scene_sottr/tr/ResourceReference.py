from io_scene_sottr.tr.Enumerations import ResourceType
from io_scene_sottr.tr.ResourceKey import ResourceKey

class ResourceReference(ResourceKey):
    offset: int

    def __init__(self, type: ResourceType, id: int, offset: int) -> None:
        super().__init__(type, id)
        self.offset = offset
    
    def __eq__(self, value: object) -> bool:
        return isinstance(value, ResourceReference) and super().__eq__(value) and self.offset == value.offset
