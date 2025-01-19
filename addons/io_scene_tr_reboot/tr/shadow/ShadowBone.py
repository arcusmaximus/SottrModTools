from ctypes import sizeof
from typing import TYPE_CHECKING
from mathutils import Quaternion, Vector
from io_scene_tr_reboot.tr.Bone import IBone
from io_scene_tr_reboot.tr.BoneConstraint import IBoneConstraint
from io_scene_tr_reboot.util.CStruct import CFloat, CInt, CStruct64

class ShadowBone(CStruct64, IBone if TYPE_CHECKING else object):
    relative_location: Vector
    absolute_orientation: Quaternion
    distance_from_parent: CFloat
    flags: CInt
    parent_id: CInt
    field_2C: CInt
    field_30: CInt
    field_34: CInt
    field_38: CInt
    field_3C: CInt

    global_id: int | None
    counterpart_local_id: int | None
    constraints: list[IBoneConstraint]
    _ignored_fields_ = ("global_id", "counterpart_local_id", "constraints")

assert(sizeof(ShadowBone) == 0x40)
