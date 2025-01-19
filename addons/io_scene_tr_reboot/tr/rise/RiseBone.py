from ctypes import sizeof
from typing import TYPE_CHECKING
from mathutils import Vector, Quaternion
from io_scene_tr_reboot.tr.Bone import IBone
from io_scene_tr_reboot.tr.BoneConstraint import IBoneConstraint
from io_scene_tr_reboot.tr.ResourceReference import ResourceReference
from io_scene_tr_reboot.util.CStruct import CInt, CStruct64, CUShort

class RiseBone(CStruct64, IBone if TYPE_CHECKING else object):
    min: Vector
    max: Vector
    relative_location: Vector
    flags: CInt
    first_vertex: CUShort
    last_vertex: CUShort
    parent_id: CInt
    info_ref: ResourceReference | None
    field_44: CInt
    field_48: CInt
    field_4C: CInt

    global_id: int | None
    absolute_orientation: Quaternion
    distance_from_parent: float
    counterpart_local_id: int | None
    constraints: list[IBoneConstraint]
    _ignored_fields_ = ("global_id", "absolute_orientation", "distance_from_parent", "counterpart_local_id", "constraints")

assert(sizeof(RiseBone) == 0x50)
