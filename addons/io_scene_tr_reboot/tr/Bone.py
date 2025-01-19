from typing import Protocol
from mathutils import Quaternion, Vector
from io_scene_tr_reboot.tr.BoneConstraint import IBoneConstraint

class IBone(Protocol):
    global_id: int | None
    counterpart_local_id: int | None
    constraints: list[IBoneConstraint]
    relative_location: Vector
    absolute_orientation: Quaternion
    distance_from_parent: float
    parent_id: int
