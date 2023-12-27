from ctypes import sizeof
from typing import NamedTuple
from io_scene_sottr.tr.ResourceReader import ResourceReader
from io_scene_sottr.tr.Bone import Bone
from io_scene_sottr.tr.ResourceReference import ResourceReference
from io_scene_sottr.util.CStruct import CByte, CInt, CLong, CShort, CStruct
from io_scene_sottr.util.SlotsBase import SlotsBase

class _SkeletonHeader(CStruct):
    bone_array_ref: ResourceReference | None
    num_words_3: CShort
    field_A: CShort
    field_C: CInt
    field_10: ResourceReference | None
    num_words_1: CLong
    words_1_ref: ResourceReference | None

    num_bone_id_mappings: CShort
    field_2A: CShort
    field_2C: CInt
    bone_id_mappings_ref: ResourceReference | None

    num_blend_shape_id_mappings: CByte
    field_39: CByte
    field_3A: CShort
    field_3C: CInt
    blend_shape_id_mappings_ref: ResourceReference | None

    field_48: CLong
    field_50: ResourceReference | None

    num_words_2: CByte
    field_59: CByte
    field_5A: CShort
    field_5C: CInt
    words_2_ref: ResourceReference | None

    bone_bytes_ref: ResourceReference | None
    words_3a_ref: ResourceReference | None
    words_3b_ref: ResourceReference | None

    field_80: CShort
    field_82: CShort
    field_84: CInt

assert(sizeof(_SkeletonHeader) == 0x88)

class Skeleton(SlotsBase):
    class IdMapping(NamedTuple):
        global_id: int
        local_id: int

    id: int
    bones: list[Bone]
    blend_shape_id_mappings: list[IdMapping]

    def __init__(self, id: int) -> None:
        self.id = id
        self.bones = []
        self.blend_shape_id_mappings = []

    def read(self, reader: ResourceReader) -> None:
        header = reader.read_struct(_SkeletonHeader)
        if header.bone_array_ref is None:
            return
        
        reader.seek(header.bone_array_ref)
        num_bones = reader.read_int64()
        bones_ref = reader.read_ref()
        if bones_ref is None:
            return
        
        reader.seek(bones_ref)
        for _ in range(num_bones):
            tr_bone = reader.read_struct(Bone)
            tr_bone.global_id = None
            self.bones.append(tr_bone)

        if header.bone_id_mappings_ref is not None:
            reader.seek(header.bone_id_mappings_ref)
            for _ in range(header.num_bone_id_mappings):
                global_bone_id = reader.read_uint16()
                local_bone_id = reader.read_uint16()
                self.bones[local_bone_id].global_id = global_bone_id

        if header.blend_shape_id_mappings_ref is not None:
            reader.seek(header.blend_shape_id_mappings_ref)
            for _ in range(header.num_blend_shape_id_mappings):
                global_blend_shape_id = reader.read_uint16()
                local_blend_shape_id = reader.read_uint16()
                self.blend_shape_id_mappings.append(Skeleton.IdMapping(global_blend_shape_id, local_blend_shape_id))
