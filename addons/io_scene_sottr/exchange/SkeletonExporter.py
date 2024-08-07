from typing import cast
import bpy
import os
from mathutils import Matrix, Quaternion, Vector
from io_scene_sottr.BlenderHelper import BlenderHelper
from io_scene_sottr.BlenderNaming import BlenderBoneIdSet, BlenderNaming
from io_scene_sottr.properties.BoneProperties import BoneProperties
from io_scene_sottr.properties.ObjectProperties import ObjectProperties
from io_scene_sottr.tr.Bone import Bone
from io_scene_sottr.tr.BoneConstraint import BoneConstraint
from io_scene_sottr.tr.Collection import Collection
from io_scene_sottr.tr.Enumerations import ResourceType
from io_scene_sottr.tr.ResourceBuilder import ResourceBuilder
from io_scene_sottr.tr.ResourceKey import ResourceKey
from io_scene_sottr.tr.Skeleton import Skeleton
from io_scene_sottr.util.Enumerable import Enumerable
from io_scene_sottr.util.Serializer import Serializer
from io_scene_sottr.util.SlotsBase import SlotsBase

class SkeletonExporter(SlotsBase):
    scale_factor: float
    
    def __init__(self, scale_factor: float) -> None:
        self.scale_factor = scale_factor
    
    def export(self, folder_path: str, bl_armature_obj: bpy.types.Object) -> None:
        if bpy.context.object:
            bpy.ops.object.mode_set(mode = "OBJECT")

        skeleton_id = BlenderNaming.parse_local_armature_name(bl_armature_obj.name)
        tr_skeleton = Skeleton(skeleton_id)

        with BlenderHelper.enter_edit_mode(bl_armature_obj):
            self.add_blend_shape_id_mappings(tr_skeleton, bl_armature_obj)
            self.add_bones(tr_skeleton, bl_armature_obj)

        writer = ResourceBuilder(ResourceKey(ResourceType.DTP, skeleton_id))
        tr_skeleton.write(writer)

        file_path = os.path.join(folder_path, Collection.make_resource_file_name(writer.resource))
        with open(file_path, "wb") as file:
            file.write(writer.build())
    
    def add_blend_shape_id_mappings(self, tr_skeleton: Skeleton, bl_armature_obj: bpy.types.Object) -> None:
        serialized_mappings = ObjectProperties.get_instance(bl_armature_obj).skeleton.global_blend_shape_ids
        for local_id, global_id in Serializer.deserialize_dict(serialized_mappings).items():
            tr_skeleton.global_blend_shape_ids[int(local_id)] = int(global_id)
        
        for bl_mesh_obj in Enumerable(bl_armature_obj.children).where(lambda o: isinstance(o.data, bpy.types.Mesh)):
            bl_mesh = cast(bpy.types.Mesh, bl_mesh_obj.data)
            if not bl_mesh.shape_keys:
                continue

            for bl_shape_key in Enumerable(bl_mesh.shape_keys.key_blocks).skip(1):
                shape_key_ids = BlenderNaming.parse_shape_key_name(bl_shape_key.name)
                if shape_key_ids.global_id is not None:
                    tr_skeleton.global_blend_shape_ids[shape_key_ids.local_id] = shape_key_ids.global_id
    
    def add_bones(self, tr_skeleton: Skeleton, bl_armature_obj: bpy.types.Object) -> None:
        bl_armature = cast(bpy.types.Armature, bl_armature_obj.data)
        bone_ids: dict[bpy.types.EditBone, BlenderBoneIdSet] = Enumerable(bl_armature.edit_bones).to_dict(lambda b: b, lambda b: BlenderNaming.parse_bone_name(b.name))
        
        bone_with_missing_id = Enumerable(bone_ids.items()).first_or_none(lambda p: p[1].local_id is None)
        if bone_with_missing_id is not None:
            raise Exception(f"Bone {bone_with_missing_id[0].name} in armature {bl_armature_obj.name} doesn't have a local ID. " +
                             "Exporting merged skeletons isn't supported - please export an outfit piece skeleton instead.")

        adding_global_bones = True
        prev_local_id = -1
        for bl_edit_bone, bone_id_set in Enumerable(bone_ids.items()).order_by(lambda p: p[1].local_id):
            if bone_id_set.local_id is None:
                raise Exception()

            if bone_id_set.local_id != prev_local_id + 1:
                raise Exception(f"Gap in bone numbering: no bone found with local ID {prev_local_id + 1} in armature {bl_armature_obj.name}. " +
                                 "Please ensure that the local IDs start at 0 and are contiguous.")
            
            if bone_id_set.global_id is None:
                adding_global_bones = False
            elif not adding_global_bones:
                raise Exception(f"Bone {bl_edit_bone.name} in armature {bl_armature_obj.name} has a global ID even though the one before it doesn't. " +
                                 "The local bone IDs should be numbered so that all the bones with global IDs come first.")
            
            tr_bone = Bone()
            bl_bone = bl_armature.bones[bl_edit_bone.name]
            self.set_bone_common_fields(tr_bone, bl_edit_bone, bone_id_set, bone_ids)
            self.add_bone_counterpart(tr_bone, bl_bone)
            self.add_bone_constraints(tr_bone, bl_bone)

            tr_skeleton.bones.append(tr_bone)
            prev_local_id = bone_id_set.local_id
    
    def set_bone_common_fields(self, tr_bone: Bone, bl_edit_bone: bpy.types.EditBone, bone_id_set: BlenderBoneIdSet, bone_ids: dict[bpy.types.EditBone, BlenderBoneIdSet]) -> None:
        if bone_id_set.local_id is None:
            raise Exception()
        
        tr_bone.global_id = bone_id_set.global_id
        
        if bl_edit_bone.parent:
            parent_id_set = bone_ids[bl_edit_bone.parent]
            if parent_id_set.local_id is None:
                raise Exception()
            
            if parent_id_set.local_id >= bone_id_set.local_id:
                raise Exception(f"Parent {bl_edit_bone.parent.name} has a local ID that's higher than that of its child {bl_edit_bone.name}. It should be lower instead.")

            tr_bone.parent_id = parent_id_set.local_id
            tr_bone.relative_location = (Vector(bl_edit_bone.head) - Vector(bl_edit_bone.parent.head)) / self.scale_factor

            z_axis = (Vector(bl_edit_bone.tail) - Vector(bl_edit_bone.head)).normalized()
            y_axis = z_axis.cross((z_axis.y, z_axis.z, z_axis.x))
            x_axis = z_axis.cross(y_axis)
            tr_bone.absolute_orientation = Matrix(((x_axis.x, y_axis.x, z_axis.x),
                                                    (x_axis.y, y_axis.y, z_axis.y),
                                                    (x_axis.z, y_axis.z, z_axis.z))).to_quaternion()
        else:
            tr_bone.parent_id = -1
            tr_bone.relative_location = Vector(bl_edit_bone.head) / self.scale_factor
            tr_bone.absolute_orientation = Quaternion()

        tr_bone.distance_from_parent = tr_bone.relative_location.length
    
    def add_bone_counterpart(self, tr_bone: Bone, bl_bone: bpy.types.Bone) -> None:
        counterpart_bone_name = BoneProperties.get_instance(bl_bone).counterpart_bone_name
        if len(counterpart_bone_name) > 0:
            counterpart_bone_id_set = BlenderNaming.try_parse_bone_name(counterpart_bone_name)
            if counterpart_bone_id_set is None or counterpart_bone_id_set.local_id is None:
                raise Exception(f"Invalid counterpart bone name {counterpart_bone_name} in bone {bl_bone.name}")
            
            tr_bone.counterpart_local_id = counterpart_bone_id_set.local_id
        else:
            tr_bone.counterpart_local_id = None
    
    def add_bone_constraints(self, tr_bone: Bone, bl_bone: bpy.types.Bone) -> None:
        tr_bone.constraints = []
        for prop_constraint in BoneProperties.get_instance(bl_bone).constraints:
            tr_constraint = BoneConstraint.deserialize(prop_constraint.data)
            tr_bone.constraints.append(tr_constraint)
