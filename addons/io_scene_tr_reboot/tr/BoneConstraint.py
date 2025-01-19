from typing import Protocol
from io_scene_tr_reboot.tr.ResourceBuilder import ResourceBuilder

class IBoneConstraint(Protocol):
    target_bone_local_id: int
    
    def write(self, writer: ResourceBuilder) -> None:
        ...
    
    def serialize(self) -> str:
        ...
