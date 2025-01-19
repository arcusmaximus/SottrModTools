from ctypes import sizeof
from io_scene_tr_reboot.tr.ResourceBuilder import ResourceBuilder
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader
from io_scene_tr_reboot.tr.ResourceReference import ResourceReference
from io_scene_tr_reboot.tr.Skeleton import SkeletonBase
from io_scene_tr_reboot.tr.rise.RiseBone import RiseBone
from io_scene_tr_reboot.util.CStruct import CByte, CInt, CStruct64, CUShort
from io_scene_tr_reboot.util.Conditional import coalesce
from io_scene_tr_reboot.util.Enumerable import Enumerable

class _SkeletonHeader(CStruct64):
    bone_array_ref: ResourceReference | None

    num_anim_id_mappings: CUShort
    num_counterpart_ranges: CUShort
    field_C: CInt
    counterpart_ranges_ref: ResourceReference | None

    num_ignore_counterpart_bones: CInt
    field_1C: CInt
    ignore_counterpart_bones_ref: ResourceReference | None

    num_bone_id_mappings: CInt
    field_2C: CInt
    bone_id_mappings_ref: ResourceReference | None

    num_blend_shape_id_mappings: CInt
    field_3C: CInt
    blend_shape_id_mappings_ref: ResourceReference | None

assert(sizeof(_SkeletonHeader) == 0x48)

class _CounterpartRange(CStruct64):
    local_id_range_1_start: CByte
    local_id_range_2_start: CByte
    count: CByte

assert(sizeof(_CounterpartRange) == 3)

class RiseSkeleton(SkeletonBase[RiseBone]):
    def __init__(self, id: int) -> None:
        super().__init__(id)

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
        self.bones = reader.read_struct_list(RiseBone, num_bones)
        for bone in self.bones:
            bone.distance_from_parent = bone.relative_location.length
            bone.global_id = None
            bone.counterpart_local_id = None
            bone.constraints = []

        self.assign_auto_bone_orientations()
        self.read_id_mappings(header, reader)
        self.read_bone_counterparts(header, reader)

    def read_id_mappings(self, header: _SkeletonHeader, reader: ResourceReader) -> None:
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

    def read_bone_counterparts(self, header: _SkeletonHeader, reader: ResourceReader) -> None:
        if header.counterpart_ranges_ref is None:
            return

        reader.seek(header.counterpart_ranges_ref)
        for counterpart_range in reader.read_struct_list(_CounterpartRange, header.num_counterpart_ranges):
            for i in range(counterpart_range.count):
                self.bones[counterpart_range.local_id_range_1_start + i].counterpart_local_id = counterpart_range.local_id_range_2_start + i

    def write(self, writer: ResourceBuilder) -> None:
        header = _SkeletonHeader()
        header.bone_array_ref = writer.make_internal_ref()
        header.num_anim_id_mappings = Enumerable(self.bones).count(lambda b: b.global_id is not None)
        header.num_counterpart_ranges = Enumerable(self.bones).count(lambda b: b.counterpart_local_id is not None)
        header.counterpart_ranges_ref = writer.make_internal_ref()
        header.ignore_counterpart_bones_ref = None
        header.num_bone_id_mappings = header.num_anim_id_mappings
        header.bone_id_mappings_ref = writer.make_internal_ref()
        header.num_blend_shape_id_mappings = Enumerable(self.global_blend_shape_ids.keys()).max() + 1 if len(self.global_blend_shape_ids) > 0 else 0
        header.blend_shape_id_mappings_ref = writer.make_internal_ref()
        writer.write_struct(header)

        header.bone_array_ref.offset = writer.position
        writer.write_int64(len(self.bones))
        bones_ref = writer.write_internal_ref()

        writer.align(0x10)
        bones_ref.offset = writer.position
        for bone in self.bones:
            writer.write_struct(bone)

        self.write_id_mappings(header, writer)
        self.write_bone_counterparts(header, writer)

        writer.write_struct(_CounterpartRange())

    def write_id_mappings(self, header: _SkeletonHeader, writer: ResourceBuilder) -> None:
        if header.bone_id_mappings_ref is None or \
           header.blend_shape_id_mappings_ref is None:
            raise Exception()

        header.bone_id_mappings_ref.offset = writer.position
        for local_bone_id, bone in enumerate(self.bones):
            if bone.global_id is not None:
                writer.write_uint16(bone.global_id)
                writer.write_uint16(local_bone_id)

        header.blend_shape_id_mappings_ref.offset = writer.position
        if len(self.global_blend_shape_ids) > 0:
            for local_id in range(Enumerable(self.global_blend_shape_ids.keys()).max() + 1):
                global_id = coalesce(self.global_blend_shape_ids.get(local_id), 0xFFFF)
                writer.write_uint16(global_id)
                writer.write_uint16(local_id)

    def write_bone_counterparts(self, header: _SkeletonHeader, writer: ResourceBuilder) -> None:
        if header.counterpart_ranges_ref is None:
            raise Exception()

        header.counterpart_ranges_ref.offset = writer.position
        for local_bone_id, bone in enumerate(self.bones):
            if bone.counterpart_local_id is not None:
                counterpart_range = _CounterpartRange()
                counterpart_range.local_id_range_1_start = local_bone_id
                counterpart_range.local_id_range_2_start = bone.counterpart_local_id
                counterpart_range.count = 1
                writer.write_struct(counterpart_range)
