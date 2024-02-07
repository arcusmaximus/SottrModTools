from ctypes import sizeof
from typing import NamedTuple, cast
from mathutils import Vector
from io_scene_sottr.tr.Collision import Collision, CollisionKey, CollisionType
from io_scene_sottr.tr.ResourceBuilder import ResourceBuilder
from io_scene_sottr.tr.ResourceReader import ResourceReader
from io_scene_sottr.tr.ResourceReference import ResourceReference
from io_scene_sottr.util.CStruct import CByte, CFloat, CInt, CLong, CShort, CStruct, CULong
from io_scene_sottr.util.Enumerable import Enumerable
from io_scene_sottr.util.SlotsBase import SlotsBase

class _ClothDtp(CStruct):
    strips_ref: ResourceReference | None
    num_strips: CShort

assert(sizeof(_ClothDtp) == 0xA)

class _ClothDtpStrip(CStruct):
    masses_ref: ResourceReference | None
    springs_ref: ResourceReference | None
    parent_bone_local_id: CInt
    id: CShort
    num_masses: CShort
    num_springs: CShort
    num_mass_groups: CShort
    field_1C: CInt

assert(sizeof(_ClothDtpStrip) == 0x20)

class _ClothDtpMass(CStruct):
    position: Vector
    anchor_bones_ref: ResourceReference | None
    vector_array_ref: ResourceReference | None
    local_bone_id: CShort
    num_anchor_bones: CByte
    group_idx: CByte
    mass: CByte
    bounce_back_factor: CByte
    field_26: CByte
    field_27: CByte
    field_28: CLong

assert(sizeof(_ClothDtpMass) == 0x30)

class _ClothDtpAnchorBone(CStruct):
    offset: Vector
    weight: CFloat
    local_bone_id: CShort
    field_16: CShort
    field_18: CLong

assert(sizeof(_ClothDtpAnchorBone) == 0x20)

class _ClothDtpSpring(CStruct):
    rest_length: CFloat
    stretchiness_interpolation_value: CFloat
    mass_1_idx: CShort
    mass_2_idx: CShort

assert(sizeof(_ClothDtpSpring) == 0xC)

class _ClothComponentDtp(CStruct):
    valid: CByte
    field_1: CByte
    field_2: CShort
    field_4: CInt
    default_strip_group_index_set_idx: CInt
    field_C: CInt
    field_10: CInt
    field_14: CInt
    sort_lower_bound: CFloat
    sort_upper_bound: CFloat
    strip_group_index_sets_ref: ResourceReference | None
    num_strip_group_index_sets: CInt
    field_2C: CInt
    strip_groups_ref: ResourceReference | None
    num_strip_groups: CInt
    field_3C: CInt
    collision_sets_ref: ResourceReference | None
    num_collision_sets: CInt
    field_4C: CInt
    field_50: CLong
    unknown_ref: ResourceReference | None

assert(sizeof(_ClothComponentDtp) == 0x60)

class _ClothComponentStripGroupIndexSet(CStruct):
    count: CInt
    field_4: CInt
    items_ref: ResourceReference | None

assert(sizeof(_ClothComponentStripGroupIndexSet) == 0x10)

class _ClothComponentStripGroup(CStruct):
    gravity_factor: CFloat
    underground_gravity_reduction: CFloat
    dampening: CFloat
    spring_strength_update_iterations: CInt
    collision_iterations: CInt
    update_iterations: CInt
    time_delta_divider: CInt
    wind_factor: CFloat
    flags: CInt
    max_mass_bounce_back_strength: CFloat
    stiffness: CFloat
    transform_type: CInt
    spring_stretchiness_default_percentage: CInt
    spring_stretchiness_lower_percentage: CInt
    spring_stretchiness_upper_percentage: CInt
    spring_length_multiplier_percentage: CInt
    acceleration_divider: CFloat
    time_delta_multiplier: CFloat
    reference_time_delta_multiplier: CFloat
    field_4C: CInt
    field_50: CFloat
    field_54: CInt
    num_strip_ids: CInt
    field_5C: CInt
    strip_ids_ref: ResourceReference | None
    num_collision_set_indices: CInt
    field_6C: CInt
    collision_set_indices_ref: ResourceReference | None
    field_78: CLong
    field_80: CLong
    field_88: CLong

assert(sizeof(_ClothComponentStripGroup) == 0x90)

class _ClothComponentCollisionSet(CStruct):
    count: CInt
    field_4: CInt
    items_ref: ResourceReference | None

assert(sizeof(_ClothComponentCollisionSet) == 0x10)

class _ClothComponentCollision(CStruct):
    type: CByte
    field_1: CByte
    field_2: CShort
    field_4: CInt
    field_8: CLong
    field_10: CLong
    hash_data_1: CULong
    hash_data_2: CULong
    remaining_hash_data_ref: ResourceReference | None

assert(sizeof(_ClothComponentCollision) == 0x30)

class ClothMassAnchorBone(NamedTuple):
    local_bone_id: int
    offset: Vector

class ClothMass(SlotsBase):
    local_bone_id: int
    position: Vector
    mass: float
    anchor_local_bones: list[ClothMassAnchorBone]
    bounceback_factor: float

    def __init__(self, local_bone_id: int, position: Vector) -> None:
        self.local_bone_id = local_bone_id
        self.position = position
        self.mass = 1.0
        self.anchor_local_bones = []
        self.bounceback_factor = 0

class ClothSpring(SlotsBase):
    mass_1_idx: int
    mass_2_idx: int
    stretchiness: float

    def __init__(self, mass_1_idx: int, mass_2_idx: int, stretchiness: float) -> None:
        self.mass_1_idx = mass_1_idx
        self.mass_2_idx = mass_2_idx
        self.stretchiness = stretchiness

class ClothStrip(SlotsBase):
    id: int
    parent_bone_local_id: int
    masses: list[ClothMass]
    springs: list[ClothSpring]
    collision_keys: list[CollisionKey]
    
    gravity_factor: float
    wind_factor: float
    stiffness: float
    dampening: float

    def __init__(self, id: int, parent_bone_local_id: int) -> None:
        self.id = id
        self.parent_bone_local_id = parent_bone_local_id
        self.masses = []
        self.springs = []
        self.collision_keys = []

        self.gravity_factor = 1
        self.wind_factor = 1
        self.stiffness = 0
        self.dampening = 0

class Cloth(SlotsBase):
    definition_id: int
    component_id: int
    strips: list[ClothStrip]

    def __init__(self, definition_id: int, component_id: int) -> None:
        self.definition_id = definition_id
        self.component_id = component_id
        self.strips = []
    
    def read(self, cloth_definition_reader: ResourceReader, cloth_component_reader: ResourceReader, collisions: list[Collision]) -> None:
        colision_lookup = Enumerable(collisions).to_dict(lambda c: CollisionKey(c.type, self.get_collision_hash([c.hash])))

        self.read_cloth_definition(cloth_definition_reader)
        self.read_cloth_component(cloth_component_reader, colision_lookup)
    
    def read_cloth_definition(self, reader: ResourceReader) -> None:
        dtp_cloth = reader.read_struct(_ClothDtp)
        if dtp_cloth.strips_ref is None:
            raise Exception()
        
        reader.seek(dtp_cloth.strips_ref)
        for dtp_strip in reader.read_struct_list(_ClothDtpStrip, dtp_cloth.num_strips):
            if dtp_strip.masses_ref is None or dtp_strip.springs_ref is None:
                raise Exception()

            strip = ClothStrip(dtp_strip.id, dtp_strip.parent_bone_local_id)

            reader.seek(dtp_strip.masses_ref)
            for dtp_mass in reader.read_struct_list(_ClothDtpMass, dtp_strip.num_masses):
                mass = ClothMass(dtp_mass.local_bone_id, dtp_mass.position)
                mass.mass = dtp_mass.mass / 255.0
                mass.bounceback_factor = dtp_mass.bounce_back_factor / 255.0
                
                if dtp_mass.anchor_bones_ref is not None:
                    reader.seek(dtp_mass.anchor_bones_ref)
                    for dtp_anchor_bone in reader.read_struct_list(_ClothDtpAnchorBone, dtp_mass.num_anchor_bones):
                        mass.anchor_local_bones.append(ClothMassAnchorBone(dtp_anchor_bone.local_bone_id, dtp_anchor_bone.offset))
                
                strip.masses.append(mass)
            
            reader.seek(dtp_strip.springs_ref)
            for dtp_spring in reader.read_struct_list(_ClothDtpSpring, dtp_strip.num_springs):
                strip.springs.append(ClothSpring(dtp_spring.mass_1_idx, dtp_spring.mass_2_idx, dtp_spring.stretchiness_interpolation_value))
            
            self.strips.append(strip)
    
    def read_cloth_component(self, reader: ResourceReader, collisions: dict[CollisionKey, Collision]) -> None:
        dtp_component = reader.read_struct(_ClothComponentDtp)
        if dtp_component.strip_groups_ref is None or \
           dtp_component.collision_sets_ref is None:
            raise Exception()
        
        collision_sets: list[list[CollisionKey]] = []
        reader.seek(dtp_component.collision_sets_ref)
        for dtp_collision_set in reader.read_struct_list(_ClothComponentCollisionSet, dtp_component.num_collision_sets):
            if dtp_collision_set.items_ref is None:
                raise Exception()
            
            collision_set: list[CollisionKey] = []
            reader.seek(dtp_collision_set.items_ref)
            for dtp_collision in reader.read_struct_list(_ClothComponentCollision, dtp_collision_set.count):
                collision_key = self.read_cloth_component_collision(dtp_collision, reader)
                collision = collisions.get(collision_key)
                if collision is not None:
                    collision_set.append(CollisionKey(collision.type, collision.hash))
            
            collision_sets.append(collision_set)
        
        reader.seek(dtp_component.strip_groups_ref)
        for dtp_strip_group in reader.read_struct_list(_ClothComponentStripGroup, dtp_component.num_strip_groups):
            if dtp_strip_group.collision_set_indices_ref is None or dtp_strip_group.strip_ids_ref is None:
                raise Exception()
            
            strip_group_collisions: list[CollisionKey] = []
            reader.seek(dtp_strip_group.collision_set_indices_ref)
            for collision_set_idx in reader.read_uint32_list(dtp_strip_group.num_collision_set_indices):
                strip_group_collisions.extend(collision_sets[collision_set_idx])
            
            reader.seek(dtp_strip_group.strip_ids_ref)
            for strip_id in reader.read_uint16_list(dtp_strip_group.num_strip_ids):
                strip = Enumerable(self.strips).first_or_none(lambda s: s.id == strip_id)
                if strip is None:
                    continue
                
                strip.gravity_factor = dtp_strip_group.gravity_factor
                strip.wind_factor = dtp_strip_group.wind_factor
                strip.stiffness = dtp_strip_group.stiffness
                strip.dampening = dtp_strip_group.dampening

                for mass in strip.masses:
                    mass.bounceback_factor *= dtp_strip_group.max_mass_bounce_back_strength
                
                for spring in strip.springs:
                    spring.stretchiness = dtp_strip_group.spring_stretchiness_lower_percentage / 100 + spring.stretchiness * \
                                          (dtp_strip_group.spring_stretchiness_upper_percentage - dtp_strip_group.spring_stretchiness_lower_percentage) / 100
                
                strip.collision_keys = strip_group_collisions
    
    def read_cloth_component_collision(self, dtp_collision: _ClothComponentCollision, reader: ResourceReader) -> CollisionKey:
        inputs: list[int] = [dtp_collision.hash_data_1]
        if dtp_collision.hash_data_2 != 0:
            inputs.append(dtp_collision.hash_data_2)
            if dtp_collision.remaining_hash_data_ref is not None:
                reader.seek(dtp_collision.remaining_hash_data_ref)
                while True:
                    value = reader.read_uint64()
                    if value == 0:
                        break

                    inputs.append(value)
        
        return CollisionKey(CollisionType(dtp_collision.type), self.get_collision_hash(inputs))

    def write(self, cloth_definition_writer: ResourceBuilder, cloth_component_writer: ResourceBuilder) -> None:
        self.write_cloth_definition(cloth_definition_writer)
        self.write_cloth_component(cloth_component_writer)

    def write_cloth_definition(self, writer: ResourceBuilder) -> None:
        dtp = _ClothDtp()
        dtp.strips_ref = writer.make_internal_ref()
        dtp.num_strips = len(self.strips)
        writer.write_struct(dtp)
        writer.align(0x10)

        dtp.strips_ref.offset = writer.position
        dtp_strips: list[_ClothDtpStrip] = []
        for strip in self.strips:
            dtp_strip = _ClothDtpStrip()
            dtp_strip.id = strip.id
            dtp_strip.masses_ref = writer.make_internal_ref()
            dtp_strip.num_masses = len(strip.masses)
            dtp_strip.num_mass_groups = len(strip.masses)
            dtp_strip.springs_ref = writer.make_internal_ref()
            dtp_strip.num_springs = len(strip.springs)
            dtp_strip.parent_bone_local_id = strip.parent_bone_local_id
            writer.write_struct(dtp_strip)
            writer.align(0x10)

            dtp_strips.append(dtp_strip)
        
        dtp_masses: list[_ClothDtpMass] = []
        for strip, dtp_strip in Enumerable(self.strips).zip(dtp_strips):
            cast(ResourceReference, dtp_strip.masses_ref).offset = writer.position
            for mass_idx, mass in enumerate(strip.masses):
                dtp_mass = _ClothDtpMass()
                dtp_mass.local_bone_id = mass.local_bone_id
                dtp_mass.position = mass.position
                dtp_mass.anchor_bones_ref = writer.make_internal_ref()
                dtp_mass.num_anchor_bones = len(mass.anchor_local_bones)
                dtp_mass.vector_array_ref = writer.make_internal_ref()
                dtp_mass.group_idx = mass_idx
                dtp_mass.mass = int(mass.mass * 255)
                dtp_mass.bounce_back_factor = int(mass.bounceback_factor * 255)
                writer.write_struct(dtp_mass)

                dtp_masses.append(dtp_mass)

        for mass, dtp_mass in Enumerable(self.strips).select_many(lambda s: s.masses).zip(dtp_masses):
            cast(ResourceReference, dtp_mass.anchor_bones_ref).offset = writer.position
            for anchor_bone in mass.anchor_local_bones:
                dtp_anchor_bone = _ClothDtpAnchorBone()
                dtp_anchor_bone.offset = anchor_bone.offset
                dtp_anchor_bone.weight = 1.0 / len(mass.anchor_local_bones)
                dtp_anchor_bone.local_bone_id = anchor_bone.local_bone_id
                writer.write_struct(dtp_anchor_bone)
        
            cast(ResourceReference, dtp_mass.vector_array_ref).offset = writer.position
            writer.write_uint32(0)
            writer.align(0x10)
        
        for strip, dtp_strip in Enumerable(self.strips).zip(dtp_strips):
            cast(ResourceReference, dtp_strip.springs_ref).offset = writer.position
            for spring in strip.springs:
                dtp_spring = _ClothDtpSpring()
                dtp_spring.rest_length = (strip.masses[spring.mass_1_idx].position - strip.masses[spring.mass_2_idx].position).length
                dtp_spring.stretchiness_interpolation_value = spring.stretchiness
                dtp_spring.mass_1_idx = spring.mass_1_idx
                dtp_spring.mass_2_idx = spring.mass_2_idx
                writer.write_struct(dtp_spring)

    def write_cloth_component(self, writer: ResourceBuilder) -> None:
        dtp = _ClothComponentDtp()
        dtp.valid = 1
        dtp.sort_lower_bound = 5000
        dtp.sort_upper_bound = 20000
        dtp.strip_group_index_sets_ref = writer.make_internal_ref()
        dtp.num_strip_group_index_sets = 1
        dtp.strip_groups_ref = writer.make_internal_ref()
        dtp.num_strip_groups = len(self.strips)
        dtp.collision_sets_ref = writer.make_internal_ref()
        dtp.num_collision_sets = len(self.strips)
        dtp.unknown_ref = None
        writer.write_struct(dtp)
        writer.align(0x10)

        dtp.strip_group_index_sets_ref.offset = writer.position
        dtp_strip_group_index_set = _ClothComponentStripGroupIndexSet()
        dtp_strip_group_index_set.count = len(self.strips)
        dtp_strip_group_index_set.items_ref = writer.make_internal_ref()
        writer.write_struct(dtp_strip_group_index_set)
        writer.align(0x10)

        dtp_strip_group_index_set.items_ref.offset = writer.position
        for i in range(len(self.strips)):
            writer.write_uint32(i)
        
        writer.align(0x10)

        dtp.strip_groups_ref.offset = writer.position
        dtp_strip_groups: list[_ClothComponentStripGroup] = []
        for strip in self.strips:
            dtp_strip_group = _ClothComponentStripGroup()
            dtp_strip_group.gravity_factor = strip.gravity_factor
            dtp_strip_group.underground_gravity_reduction = 0.5
            dtp_strip_group.dampening = strip.dampening
            dtp_strip_group.spring_strength_update_iterations = 3
            dtp_strip_group.collision_iterations = 2
            dtp_strip_group.update_iterations = 5
            dtp_strip_group.time_delta_divider = 2
            dtp_strip_group.wind_factor = strip.wind_factor
            dtp_strip_group.max_mass_bounce_back_strength = 1.0
            dtp_strip_group.stiffness = strip.stiffness
            dtp_strip_group.transform_type = 0
            dtp_strip_group.spring_stretchiness_default_percentage = 0
            dtp_strip_group.spring_stretchiness_lower_percentage = 0
            dtp_strip_group.spring_stretchiness_upper_percentage = 100
            dtp_strip_group.spring_length_multiplier_percentage = 60
            dtp_strip_group.acceleration_divider = 20
            dtp_strip_group.time_delta_multiplier = 1.0
            dtp_strip_group.reference_time_delta_multiplier = 8.0
            dtp_strip_group.strip_ids_ref = writer.make_internal_ref()
            dtp_strip_group.num_strip_ids = 1
            dtp_strip_group.collision_set_indices_ref = writer.make_internal_ref()
            dtp_strip_group.num_collision_set_indices = 1
            writer.write_struct(dtp_strip_group)
        
            dtp_strip_groups.append(dtp_strip_group)

        for i, (strip, dtp_strip_group) in enumerate(Enumerable(self.strips).zip(dtp_strip_groups)):
            cast(ResourceReference, dtp_strip_group.strip_ids_ref).offset = writer.position
            writer.write_uint16(strip.id)
            writer.align(0x10)

            cast(ResourceReference, dtp_strip_group.collision_set_indices_ref).offset = writer.position
            writer.write_uint32(i)
            writer.align(0x10)
        
        dtp.collision_sets_ref.offset = writer.position
        dtp_collision_sets: list[_ClothComponentCollisionSet] = []
        for strip in self.strips:
            dtp_collision_set = _ClothComponentCollisionSet()
            dtp_collision_set.count = len(strip.collision_keys)
            dtp_collision_set.items_ref = writer.make_internal_ref()
            writer.write_struct(dtp_collision_set)
            writer.align(0x10)

            dtp_collision_sets.append(dtp_collision_set)

        for strip, dtp_collision_set in Enumerable(self.strips).zip(dtp_collision_sets):
            cast(ResourceReference, dtp_collision_set.items_ref).offset = writer.position
            for collision_key in strip.collision_keys:
                dtp_collision = _ClothComponentCollision()
                dtp_collision.type = collision_key.type
                dtp_collision.hash_data_1 = collision_key.hash
                dtp_collision.remaining_hash_data_ref = None
                writer.write_struct(dtp_collision)
    
    def get_collision_hash(self, input: list[int]) -> int:
        hash = 0
        for value in input:
            for i, byte in enumerate(value.to_bytes(8, "little")):
                if (i % 4) == 0 and hash == 0:
                    hash = 0xCBF29CE484222325

                hash = ((hash * 0x100000001B3) ^ byte) & 0xFFFFFFFFFFFFFFFF
        
        return hash
