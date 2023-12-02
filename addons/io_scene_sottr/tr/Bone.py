from ctypes import sizeof
from mathutils import Quaternion, Vector
from io_scene_sottr.util.CStruct import CFloat, CInt, CStruct

class Bone(CStruct):
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
    _ignored_fields_ = ("global_id",)

assert(sizeof(Bone) == 0x40)
