from io_scene_tr_reboot.tr.ResourceBuilder import ResourceBuilder
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader
from io_scene_tr_reboot.tr.Skeleton import SkeletonBase
from io_scene_tr_reboot.tr.tr2013.Tr2013Bone import Tr2013Bone
from io_scene_tr_reboot.util.Enumerable import Enumerable

class Tr2013Skeleton(SkeletonBase[Tr2013Bone]):
    def __init__(self, id: int) -> None:
        super().__init__(id)

    def read(self, reader: ResourceReader) -> None:
        self.read_bones(reader)
        self.read_id_mappings(reader)

    def read_bones(self, reader: ResourceReader) -> None:
        num_bones = reader.read_int32()
        bones_ref = reader.read_ref()
        if bones_ref is None:
            return

        reader.seek(bones_ref)
        self.bones = reader.read_struct_list(Tr2013Bone, num_bones)
        for bone in self.bones:
            bone.distance_from_parent = bone.relative_location.length
            bone.global_id = None
            bone.counterpart_local_id = None
            bone.constraints = []

        self.assign_auto_bone_orientations()

    def read_id_mappings(self, reader: ResourceReader) -> None:
        num_mappings = reader.read_int32()
        reader.read_int32()     # capacity
        mappings_ref = reader.read_ref()
        if mappings_ref is None:
            return

        reader.seek(mappings_ref)
        for _ in range(num_mappings):
            global_bone_id = reader.read_uint16()
            local_bone_id = reader.read_uint16()
            self.bones[local_bone_id].global_id = global_bone_id

    def write(self, writer: ResourceBuilder) -> None:
        self.write_bones(writer)
        self.write_id_mappings(writer)

    def write_bones(self, writer: ResourceBuilder) -> None:
        writer.write_int32(len(self.bones))
        bones_ref = writer.write_internal_ref()

        bones_ref.offset = writer.position
        writer.write_struct_list(self.bones)

    def write_id_mappings(self, writer: ResourceBuilder) -> None:
        writer.write_int32(Enumerable(self.bones).count(lambda b: b.global_id is not None))
        writer.write_int32(0)
        mappings_ref = writer.write_internal_ref()

        mappings_ref.offset = writer.position
        for i, bone in enumerate(self.bones):
            if bone.global_id is not None:
                writer.write_uint16(bone.global_id)
                writer.write_uint16(i)
