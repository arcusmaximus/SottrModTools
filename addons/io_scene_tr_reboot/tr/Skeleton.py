from abc import abstractmethod
from mathutils import Quaternion, Vector
from typing import Generic, Protocol, TypeVar
from io_scene_tr_reboot.tr.Bone import IBone
from io_scene_tr_reboot.tr.ResourceBuilder import ResourceBuilder
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader
from io_scene_tr_reboot.util.Enumerable import Enumerable

class ISkeleton(Protocol):
    id: int
    bones: list[IBone]
    global_blend_shape_ids: dict[int, int]

    def read(self, reader: ResourceReader) -> None: ...
    def write(self, writer: ResourceBuilder) -> None: ...

TBone = TypeVar("TBone", bound = IBone)
class SkeletonBase(ISkeleton, Generic[TBone]):
    id: int
    bones: list[TBone]
    global_blend_shape_ids: dict[int, int]

    def __init__(self, id: int) -> None:
        self.id = id
        self.bones = []     # type: ignore
        self.global_blend_shape_ids = {}

    @abstractmethod
    def read(self, reader: ResourceReader) -> None: ...

    @abstractmethod
    def write(self, writer: ResourceBuilder) -> None: ...

    def assign_auto_bone_orientations(self):
        bones_by_parent_id = Enumerable(self.bones).group_by(lambda b: b.parent_id)
        z_axis = Vector((0, 0, 1))
        for bone_id, bone in enumerate(self.bones):
            child_bones = bones_by_parent_id.get(bone_id)
            if child_bones is None:
                if bone.parent_id >= 0:
                    bone.absolute_orientation = self.bones[bone.parent_id].absolute_orientation
                else:
                    bone.absolute_orientation = Quaternion()

                continue

            average_child_pos = Vector()
            for child_bone in child_bones:
                average_child_pos += child_bone.relative_location

            average_child_pos /= len(child_bones)
            if average_child_pos.length < 0.0001:
                bone.absolute_orientation = Quaternion()
                continue

            bone.absolute_orientation = z_axis.rotation_difference(average_child_pos)
