from ctypes import sizeof
from typing import ClassVar, cast
from mathutils import Quaternion, Vector
from io_scene_tr_reboot.tr.BoneConstraint import IBoneConstraint
from io_scene_tr_reboot.tr.ResourceBuilder import ResourceBuilder
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader
from io_scene_tr_reboot.tr.ResourceReference import ResourceReference
from io_scene_tr_reboot.util.CStruct import CByte, CInt, CShort, CStruct64
from io_scene_tr_reboot.util.CStructTypeMappings import CVec3
from io_scene_tr_reboot.util.Serializer import Serializer

class _BoneConstraintCommonData(CStruct64):
    type: CByte
    field_1: CByte
    target_bone_local_id: CShort
    num_source_bones: CShort
    field_6: CShort
    source_bone_local_ids_ref: ResourceReference | None
    source_bone_weights_ref: ResourceReference | None
    extra_data_ref: ResourceReference | None

assert(sizeof(_BoneConstraintCommonData) == 0x20)

class _BoneConstraintExtraData0(CStruct64):
    quat1: Quaternion
    quat2: Quaternion
    vec1: CVec3
    field_2C: CInt
    vec2: CVec3
    field_3C: CInt
    reference_pos: CVec3
    field_4C: CInt
    reference_rot: Quaternion
    reference_bone_local_id: CShort
    reference_type: CByte

assert(sizeof(_BoneConstraintExtraData0) == 0x63)

class _BoneConstraintExtraData1(CStruct64):
    offset: Vector

assert(sizeof(_BoneConstraintExtraData1) == 0x10)

class _BoneConstraintExtraData2(CStruct64):
    offset: Quaternion

assert(sizeof(_BoneConstraintExtraData2) == 0x10)

class _BoneConstraintExtraData3(CStruct64):
    source_vectors_1_ref: ResourceReference | None
    source_vectors_2_ref: ResourceReference | None
    source_blend_shape_ids_ref: ResourceReference | None
    use_source_vectors_1: CByte
    use_source_vectors_2: CByte

assert(sizeof(_BoneConstraintExtraData3) == 0x1A)

class ShadowBoneConstraint(IBoneConstraint):
    concrete_classes: ClassVar[list[type["ShadowBoneConstraint"]]] = []

    target_bone_local_id: int
    source_bone_local_ids: list[int]
    source_bone_weights: list[float]

    def __init__(self) -> None:
        self.target_bone_local_id = 0
        self.source_bone_local_ids = []
        self.source_bone_weights = []

    @staticmethod
    def read(reader: ResourceReader) -> "ShadowBoneConstraint":
        common_data = reader.read_struct(_BoneConstraintCommonData)

        constraint = ShadowBoneConstraint.concrete_classes[common_data.type]()
        constraint.target_bone_local_id = common_data.target_bone_local_id

        if common_data.source_bone_local_ids_ref is not None:
            reader.seek(common_data.source_bone_local_ids_ref)
            constraint.source_bone_local_ids = list(reader.read_uint16_list(common_data.num_source_bones))

        if common_data.source_bone_weights_ref is not None:
            reader.seek(common_data.source_bone_weights_ref)
            constraint.source_bone_weights = list(reader.read_float_list(common_data.num_source_bones))

        if common_data.extra_data_ref is not None:
            reader.seek(common_data.extra_data_ref)
            constraint.read_extra_data(reader)

        return constraint

    def read_extra_data(self, reader: ResourceReader) -> None:
        ...

    def write(self, writer: ResourceBuilder) -> None:
        common_data = _BoneConstraintCommonData()
        common_data.type = ShadowBoneConstraint.concrete_classes.index(self.__class__)
        common_data.target_bone_local_id = self.target_bone_local_id
        common_data.num_source_bones = len(self.source_bone_local_ids)
        common_data.source_bone_local_ids_ref = writer.make_internal_ref()
        common_data.source_bone_weights_ref = writer.make_internal_ref()
        common_data.extra_data_ref = writer.make_internal_ref()
        writer.write_struct(common_data)

        common_data.source_bone_local_ids_ref.offset = writer.position
        writer.write_uint16_list(self.source_bone_local_ids)
        writer.align(4)

        common_data.source_bone_weights_ref.offset = writer.position
        writer.write_float_list(self.source_bone_weights)
        writer.align(0x10)

        common_data.extra_data_ref.offset = writer.position
        self.write_extra_data(writer)

    def write_extra_data(self, writer: ResourceBuilder) -> None:
        ...

    def apply_bone_local_id_changes(self, mapping: dict[int, int]) -> None:
        new_target_bone_id = mapping.get(self.target_bone_local_id)
        if new_target_bone_id is not None:
            self.target_bone_local_id = new_target_bone_id

        for i, old_source_bone_id in enumerate(self.source_bone_local_ids):
            new_source_bone_id = mapping.get(old_source_bone_id)
            if new_source_bone_id is not None:
                self.source_bone_local_ids[i] = new_source_bone_id

    def serialize(self) -> str:
        values: dict[str, str] = {
            "type": str(ShadowBoneConstraint.concrete_classes.index(self.__class__))
        }
        return Serializer.serialize_object(self, values)

    @staticmethod
    def deserialize(data: str) -> "ShadowBoneConstraint":
        def create_constraint(values: dict[str, str]) -> object:
            type = ShadowBoneConstraint.concrete_classes[int(values["type"])]
            return type()

        return cast(ShadowBoneConstraint, Serializer.deserialize_object(data, create_constraint))

class ShadowBoneConstraint0(ShadowBoneConstraint):
    quat1: Quaternion
    quat2: Quaternion
    vec1: Vector
    vec2: Vector
    reference_pos: Vector
    reference_rot: Quaternion
    reference_bone_local_id: int
    reference_type: int

    def __init__(self) -> None:
        super().__init__()
        self.quat1 = Quaternion()
        self.quat2 = Quaternion()
        self.vec1 = Vector()
        self.vec2 = Vector()
        self.reference_pos = Vector()
        self.reference_rot = Quaternion()
        self.reference_bone_local_id = 0
        self.reference_type = 0

    def read_extra_data(self, reader: ResourceReader) -> None:
        extra_data = reader.read_struct(_BoneConstraintExtraData0)
        self.quat1 = extra_data.quat1
        self.quat2 = extra_data.quat2
        self.vec1 = extra_data.vec1.to_vector()
        self.vec2 = extra_data.vec2.to_vector()
        self.reference_pos = extra_data.reference_pos.to_vector()
        self.reference_rot = extra_data.reference_rot
        self.reference_bone_local_id = extra_data.reference_bone_local_id
        self.reference_type = extra_data.reference_type

    def write_extra_data(self, writer: ResourceBuilder) -> None:
        extra_data = _BoneConstraintExtraData0()
        extra_data.quat1 = self.quat1
        extra_data.quat2 = self.quat2
        extra_data.vec1 = CVec3.from_vector(self.vec1)
        extra_data.vec2 = CVec3.from_vector(self.vec2)
        extra_data.reference_pos = CVec3.from_vector(self.reference_pos)
        extra_data.reference_rot = self.reference_rot
        extra_data.reference_bone_local_id = self.reference_bone_local_id
        extra_data.reference_type = self.reference_type
        writer.write_struct(extra_data)
        writer.align(0x10)

    def apply_bone_local_id_changes(self, mapping: dict[int, int]) -> None:
        super().apply_bone_local_id_changes(mapping)

        new_reference_bone_id = mapping.get(self.reference_bone_local_id)
        if new_reference_bone_id is not None:
            self.reference_bone_local_id = new_reference_bone_id

class ShadowBoneConstraint1(ShadowBoneConstraint):
    offset: Vector

    def __init__(self) -> None:
        super().__init__()
        self.offset = Vector()

    def read_extra_data(self, reader: ResourceReader) -> None:
        extra_data = reader.read_struct(_BoneConstraintExtraData1)
        self.offset = extra_data.offset

    def write_extra_data(self, writer: ResourceBuilder) -> None:
        extra_data = _BoneConstraintExtraData1()
        extra_data.offset = self.offset
        writer.write_struct(extra_data)

class ShadowBoneConstraint2(ShadowBoneConstraint):
    offset: Quaternion

    def __init__(self) -> None:
        super().__init__()
        self.offset = Quaternion()

    def read_extra_data(self, reader: ResourceReader) -> None:
        extra_data = reader.read_struct(_BoneConstraintExtraData2)
        self.offset = extra_data.offset

    def write_extra_data(self, writer: ResourceBuilder) -> None:
        extra_data = _BoneConstraintExtraData2()
        extra_data.offset = self.offset
        writer.write_struct(extra_data)

class ShadowBoneConstraint3(ShadowBoneConstraint):
    source_vectors_1: list[Vector]
    source_vectors_2: list[Vector]
    source_blend_shape_ids: list[int]
    use_source_vectors_1: bool
    use_source_vectors_2: bool

    def __init__(self) -> None:
        super().__init__()
        self.source_vectors_1 = []
        self.source_vectors_2 = []
        self.source_blend_shape_ids = []
        self.use_source_vectors_1 = False
        self.use_source_vectors_2 = False

    def read_extra_data(self, reader: ResourceReader) -> None:
        extra_data = reader.read_struct(_BoneConstraintExtraData3)

        if extra_data.source_vectors_1_ref is not None:
            reader.seek(extra_data.source_vectors_1_ref)
            self.source_vectors_1 = reader.read_vec4d_list(len(self.source_bone_local_ids))

        if extra_data.source_vectors_2_ref is not None:
            reader.seek(extra_data.source_vectors_2_ref)
            self.source_vectors_2 = reader.read_vec4d_list(len(self.source_bone_local_ids))

        if extra_data.source_blend_shape_ids_ref is not None:
            reader.seek(extra_data.source_blend_shape_ids_ref)
            self.source_blend_shape_ids = list(reader.read_uint16_list(len(self.source_bone_local_ids)))

        self.use_source_vectors_1 = extra_data.use_source_vectors_1 != 0
        self.use_source_vectors_2 = extra_data.use_source_vectors_2 != 0

    def write_extra_data(self, writer: ResourceBuilder) -> None:
        extra_data = _BoneConstraintExtraData3()
        extra_data.source_vectors_1_ref = writer.make_internal_ref()
        extra_data.source_vectors_2_ref = writer.make_internal_ref()
        extra_data.source_blend_shape_ids_ref = writer.make_internal_ref()
        extra_data.use_source_vectors_1 = int(self.use_source_vectors_1)
        extra_data.use_source_vectors_2 = int(self.use_source_vectors_2)
        writer.write_struct(extra_data)
        writer.align(0x10)

        extra_data.source_vectors_1_ref.offset = writer.position
        writer.write_vec4d_list(self.source_vectors_1)

        extra_data.source_vectors_2_ref.offset = writer.position
        writer.write_vec4d_list(self.source_vectors_2)

        extra_data.source_blend_shape_ids_ref.offset = writer.position
        writer.write_uint16_list(self.source_blend_shape_ids)

        writer.align(0x10)

ShadowBoneConstraint.concrete_classes = [
    ShadowBoneConstraint0,
    ShadowBoneConstraint1,
    ShadowBoneConstraint2,
    ShadowBoneConstraint3
]
