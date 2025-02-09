from ctypes import sizeof
from typing import Protocol, cast
from io_scene_tr_reboot.tr.Collision import Collision, CollisionCapsule, CollisionSphere, CollisionType
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader
from io_scene_tr_reboot.util.CStruct import CFloat, CInt, CShort, CStruct, CStruct32
from io_scene_tr_reboot.util.Conditional import coalesce

class _CollisionBone(CStruct32):
    type: CShort
    local_bone_idx: CShort

assert(sizeof(_CollisionBone) == 4)

class _Collision(CStruct32):
    type: CInt
    constraint_type: CInt
    bone1: _CollisionBone
    bone2: _CollisionBone
    radius: CFloat

assert(sizeof(_Collision) == 0x14)

class _ITr2013Collision(Protocol):
    def assign_from_struct(self, struct: _Collision, global_bone_ids: list[int | None]) -> None: ...
    def assign_to_struct(self, struct: _Collision, global_bone_ids: list[int | None]) -> None: ...

class Tr2013Collision(Collision):
    @classmethod
    def read(cls, reader: ResourceReader, index: int, global_bone_ids: list[int | None]) -> Collision:
        struct = reader.read_struct(_Collision)
        collision = cls.create(CollisionType(struct.type), index)
        collision.global_bone_id = cls._convert_dtp_bone_id_to_global(struct.bone1.local_bone_idx, global_bone_ids)
        cast(_ITr2013Collision, collision).assign_from_struct(struct, global_bone_ids)
        return collision

    @classmethod
    def to_struct(cls, collision: Collision, global_bone_ids: list[int | None]) -> CStruct:
        struct = _Collision()
        struct.bone1 = _CollisionBone()
        struct.bone2 = _CollisionBone()

        struct.type = collision.type
        struct.constraint_type = collision.type
        struct.bone1.type = 1
        struct.bone1.local_bone_idx = cls._convert_global_bone_id_to_dtp(collision.global_bone_id, global_bone_ids)
        cast(_ITr2013Collision, collision).assign_to_struct(struct, global_bone_ids)
        return struct


class Tr2013CollisionCapsule(CollisionCapsule, Tr2013Collision, _ITr2013Collision):
    def assign_from_struct(self, struct: _Collision, global_bone_ids: list[int | None]) -> None:
        self.target_global_bone_id = self._convert_dtp_bone_id_to_global(struct.bone2.local_bone_idx, global_bone_ids)
        self.radius = struct.radius

    def assign_to_struct(self, struct: _Collision, global_bone_ids: list[int | None]) -> None:
        struct.bone2.type = 1
        struct.bone2.local_bone_idx = self._convert_global_bone_id_to_dtp(coalesce(self.target_global_bone_id, -1), global_bone_ids)
        struct.radius = self.radius

class Tr2013CollisionSphere(CollisionSphere, Tr2013Collision, _ITr2013Collision):
    def assign_from_struct(self, struct: _Collision, global_bone_ids: list[int | None]) -> None:
        self.radius = struct.radius

    def assign_to_struct(self, struct: _Collision, global_bone_ids: list[int | None]) -> None:
        struct.radius = self.radius

Tr2013Collision.type_mapping = {
    CollisionType.CAPSULE:  Tr2013CollisionCapsule,
    CollisionType.SPHERE:   Tr2013CollisionSphere
}
