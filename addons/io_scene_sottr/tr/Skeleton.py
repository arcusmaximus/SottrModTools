from ctypes import sizeof
from io_scene_sottr.tr.ResourceBuilder import ResourceBuilder
from io_scene_sottr.tr.ResourceReader import ResourceReader
from io_scene_sottr.tr.Bone import Bone
from io_scene_sottr.tr.ResourceReference import ResourceReference
from io_scene_sottr.util.CStruct import CByte, CInt, CLong, CShort, CStruct
from io_scene_sottr.util.Enumerable import Enumerable
from io_scene_sottr.util.SlotsBase import SlotsBase

class _SkeletonHeader(CStruct):
    bone_array_ref: ResourceReference | None
    num_anim_id_mappings: CShort
    field_A: CShort
    field_C: CInt
    counterpart_ranges_ref: ResourceReference | None
    num_unused_words_1: CLong
    unused_words_1_ref: ResourceReference | None

    num_bone_id_mappings: CShort
    field_2A: CShort
    field_2C: CInt
    bone_id_mappings_ref: ResourceReference | None

    num_blend_shape_id_mappings: CByte
    field_39: CByte
    field_3A: CShort
    field_3C: CInt
    blend_shape_id_mappings_ref: ResourceReference | None

    num_extra_bone_infos: CByte
    field_49: CByte
    field_4A: CShort
    field_4C: CInt
    extra_bone_infos_ref: ResourceReference | None

    num_unused_words_2_ref: CByte
    field_59: CByte
    field_5A: CShort
    field_5C: CInt
    unused_words_2_ref: ResourceReference | None

    unused_bytes_ref: ResourceReference | None
    local_bone_ids_by_anim_id_ref: ResourceReference | None
    anim_bone_ids_by_local_id_ref: ResourceReference | None

    unknown_count_1: CShort
    unknown_count_2: CShort
    unknown_count_3: CShort
    unknown_count_4: CShort

assert(sizeof(_SkeletonHeader) == 0x88)

class _CounterpartRange(CStruct):
    local_id_range_1_start: CShort
    local_id_range_2_start: CShort
    count: CShort

assert(sizeof(_CounterpartRange) == 6)

class Skeleton(SlotsBase):
    id: int
    bones: list[Bone]
    global_blend_shape_ids: dict[int, int]

    def __init__(self, id: int) -> None:
        self.id = id
        self.bones = []
        self.global_blend_shape_ids = {}

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
            tr_bone.counterpart_local_id = None
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
                self.global_blend_shape_ids[local_blend_shape_id] = global_blend_shape_id
        
        if header.counterpart_ranges_ref is None:
            return
        
        reader.seek(header.counterpart_ranges_ref)
        while True:
            counterpart_range = reader.read_struct(_CounterpartRange)
            if counterpart_range.count == 0:
                break

            for i in range(counterpart_range.count):
                self.bones[counterpart_range.local_id_range_1_start + i].counterpart_local_id = counterpart_range.local_id_range_2_start + i

    def write(self, writer: ResourceBuilder) -> None:
        header = _SkeletonHeader()
        header.bone_array_ref = writer.make_internal_ref()
        header.num_anim_id_mappings = Enumerable(self.bones).count(lambda b: b.global_id is not None)
        header.counterpart_ranges_ref = writer.make_internal_ref()
        header.unused_words_1_ref = None
        header.num_bone_id_mappings = header.num_anim_id_mappings
        header.bone_id_mappings_ref = writer.make_internal_ref()
        header.num_blend_shape_id_mappings = len(self.global_blend_shape_ids)
        header.blend_shape_id_mappings_ref = writer.make_internal_ref()
        header.extra_bone_infos_ref = None
        header.unused_words_2_ref = None
        header.unused_bytes_ref = None
        header.local_bone_ids_by_anim_id_ref = writer.make_internal_ref()
        header.anim_bone_ids_by_local_id_ref = writer.make_internal_ref()
        header.unknown_count_1 = header.num_anim_id_mappings
        header.unknown_count_2 = header.num_anim_id_mappings
        header.unknown_count_3 = header.num_anim_id_mappings
        writer.write_struct(header)

        header.bone_array_ref.offset = writer.position
        writer.write_int64(len(self.bones))
        bones_ref = writer.write_internal_ref()

        writer.align(0x10)
        bones_ref.offset = writer.position
        for bone in self.bones:
            writer.write_struct(bone)
        
        header.bone_id_mappings_ref.offset = writer.position
        for local_bone_id, bone in enumerate(self.bones):
            if bone.global_id is not None:
                writer.write_uint16(bone.global_id)
                writer.write_uint16(local_bone_id)
        
        header.blend_shape_id_mappings_ref.offset = writer.position
        for local_id, global_id in self.global_blend_shape_ids.items():
            writer.write_uint16(global_id)
            writer.write_uint16(local_id)
        
        header.local_bone_ids_by_anim_id_ref.offset = writer.position
        header.anim_bone_ids_by_local_id_ref.offset = writer.position
        for i in range(header.num_anim_id_mappings):
            writer.write_uint16(i)
        
        header.counterpart_ranges_ref.offset = writer.position
        for local_bone_id, bone in enumerate(self.bones):
            if bone.counterpart_local_id is not None:
                counterpart_range = _CounterpartRange()
                counterpart_range.local_id_range_1_start = local_bone_id
                counterpart_range.local_id_range_2_start = bone.counterpart_local_id
                counterpart_range.count = 1
                writer.write_struct(counterpart_range)
            
        writer.write_struct(_CounterpartRange())
