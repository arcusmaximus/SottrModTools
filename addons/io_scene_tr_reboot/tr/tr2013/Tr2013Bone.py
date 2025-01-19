from ctypes import sizeof
from typing import TYPE_CHECKING
from mathutils import Quaternion, Vector
from io_scene_tr_reboot.tr.Bone import IBone
from io_scene_tr_reboot.tr.BoneConstraint import IBoneConstraint
from io_scene_tr_reboot.tr.ResourceReference import ResourceReference
from io_scene_tr_reboot.util.CStruct import CInt, CStruct32, CUShort

class Tr2013Bone(CStruct32, IBone if TYPE_CHECKING else object):
    min: Vector
    max: Vector
    relative_location: Vector
    flags: CInt
    first_vertex: CUShort
    last_vertex: CUShort
    parent_id: CInt
    info_ref: ResourceReference | None

    absolute_orientation: Quaternion
    distance_from_parent: float
    global_id: int | None
    counterpart_local_id: int | None
    constraints: list[IBoneConstraint]
    _ignored_fields_ = ("absolute_orientation", "distance_from_parent", "global_id", "counterpart_local_id", "constraints")

assert(sizeof(Tr2013Bone) == 0x40)
