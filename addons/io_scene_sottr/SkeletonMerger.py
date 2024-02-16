from typing import cast
import bpy
from io_scene_sottr.BlenderHelper import BlenderBoneGroup, BlenderHelper
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.properties.BoneProperties import BoneProperties
from io_scene_sottr.properties.ObjectProperties import ObjectProperties
from io_scene_sottr.tr.BoneConstraint import BoneConstraint
from io_scene_sottr.util.Enumerable import Enumerable
from io_scene_sottr.util.SlotsBase import SlotsBase

class SkeletonMerger(SlotsBase):
    def add(self, bl_target_armature_obj: bpy.types.Object | None, bl_source_armature_obj: bpy.types.Object, /) -> bpy.types.Object:
        ...
    
    def get_global_bone_parents(self, bl_armature_obj: bpy.types.Object) -> dict[int, int]:
        bl_armature = cast(bpy.types.Armature, bl_armature_obj.data)
        bone_parents: dict[int, int] = {}
        for bl_bone in bl_armature.bones:
            if not bl_bone.parent:
                continue

            child_bone_id_set  = BlenderNaming.parse_bone_name(bl_bone.name)
            parent_bone_id_set = BlenderNaming.parse_bone_name(bl_bone.parent.name)
            if child_bone_id_set.global_id is not None and parent_bone_id_set.global_id is not None:
                bone_parents[child_bone_id_set.global_id] = parent_bone_id_set.global_id

        return bone_parents
    
    def apply_global_bone_parents(self, bl_armature_obj: bpy.types.Object, bone_parents: dict[int, int]) -> None:
        bl_armature = cast(bpy.types.Armature, bl_armature_obj.data)
        bone_names_by_global_id = self.get_bone_names_by_global_id(bl_armature_obj)
        with BlenderHelper.enter_edit_mode():
            for child_bone_id, parent_bone_id in bone_parents.items():
                bl_child_bone  = bl_armature.edit_bones[bone_names_by_global_id[child_bone_id]]
                bl_parent_bone = bl_armature.edit_bones[bone_names_by_global_id[parent_bone_id]]
                bl_child_bone.parent = bl_parent_bone
    
    def get_visible_global_bones(self, bl_local_armature_obj: bpy.types.Object) -> list[int]:
        visible_bone_ids: list[int] = []
        bl_local_armature = cast(bpy.types.Armature, bl_local_armature_obj.data)
        for bl_bone in bl_local_armature.bones:
            if not BlenderHelper.is_bone_visible(bl_local_armature, bl_bone):
                continue

            bone_ids = BlenderNaming.parse_bone_name(bl_bone.name)
            if bone_ids.global_id is None:
                continue

            visible_bone_ids.append(bone_ids.global_id)
        
        return visible_bone_ids
    
    def apply_visible_global_bones(self, bl_armature_obj: bpy.types.Object, visible_global_bone_ids: list[int]) -> None:
        bl_armature = cast(bpy.types.Armature, bl_armature_obj.data)
        bone_names_by_global_id = self.get_bone_names_by_global_id(bl_armature_obj)
        for global_bone_id in visible_global_bone_ids:
            bone_name = bone_names_by_global_id[global_bone_id]
            BlenderHelper.set_bone_visible(bl_armature, bl_armature.bones[bone_name], True)
    
    def get_bone_groups(self, bl_armature_obj: bpy.types.Object) -> dict[str, BlenderBoneGroup]:
        result: dict[str, BlenderBoneGroup] = {}
        for bl_bone in cast(bpy.types.Armature, bl_armature_obj.data).bones:
            bone_group = BlenderHelper.get_bone_group(bl_armature_obj, bl_bone)
            if bone_group is not None and bone_group.name != BlenderNaming.hidden_bone_group_name:
                result[bl_bone.name] = bone_group
        
        return result
    
    def apply_bone_groups(self, bl_armature_obj: bpy.types.Object, bone_groups: dict[str, BlenderBoneGroup]):
        bl_armature = cast(bpy.types.Armature, bl_armature_obj.data)
        for bone_name, bone_group in bone_groups.items():
            BlenderHelper.move_bone_to_group(bl_armature_obj, bl_armature.bones[bone_name], bone_group.name, bone_group.palette)

    def get_bone_names_by_global_id(self, bl_armature_obj: bpy.types.Object) -> dict[int, str]:
        bl_armature = cast(bpy.types.Armature, bl_armature_obj.data)
        bone_names_by_global_id: dict[int, str] = {}
        for bl_bone in bl_armature.bones:
            bone_id_set = BlenderNaming.parse_bone_name(bl_bone.name)
            if bone_id_set.global_id is not None:
                bone_names_by_global_id[bone_id_set.global_id] = bl_bone.name
        
        return bone_names_by_global_id

    def apply_bone_renames_to_armature_and_children(self, bl_armature_obj: bpy.types.Object, renames: dict[str, str]) -> None:
        self.apply_bone_renames_to_armature(bl_armature_obj, renames)
        self.apply_bone_renames_to_cloth_strips(bl_armature_obj, renames)
        
    def apply_bone_renames_to_armature(self, bl_armature_obj: bpy.types.Object, renames: dict[str, str]) -> None:
        bl_armature = cast(bpy.types.Armature, bl_armature_obj.data)

        with BlenderHelper.enter_edit_mode(bl_armature_obj):
            for from_bone_name, to_bone_name in renames.items():
                bl_armature.edit_bones[from_bone_name].name = to_bone_name
        
        local_id_changes: dict[int, int] = {}
        for old_name, new_name in renames.items():
            old_id_set = BlenderNaming.parse_bone_name(old_name)
            new_id_set = BlenderNaming.parse_bone_name(new_name)
            if old_id_set.local_id is not None and new_id_set.local_id is not None and old_id_set.local_id != new_id_set.local_id:
                local_id_changes[old_id_set.local_id] = new_id_set.local_id

        for bl_bone in bl_armature.bones:
            tr_bone_properties = BoneProperties.get_instance(bl_bone)
            new_counterpart_bone_name = renames.get(tr_bone_properties.counterpart_bone_name)
            if new_counterpart_bone_name is not None:
                tr_bone_properties.counterpart_bone_name = new_counterpart_bone_name

            if len(local_id_changes) == 0:
                continue

            for tr_constraint_data in tr_bone_properties.constraints:
                tr_constraint = BoneConstraint.deserialize(tr_constraint_data.data)
                tr_constraint.apply_bone_local_id_changes(local_id_changes)
                tr_constraint_data.data = tr_constraint.serialize()
    
    def apply_bone_renames_to_vertex_groups(self, bl_armature_obj: bpy.types.Object, mappings: dict[str, str]) -> None:
        for bl_mesh_obj in Enumerable(bl_armature_obj.children_recursive).where(lambda o: isinstance(o.data, bpy.types.Mesh)):
            for from_bone_name, to_bone_name in mappings.items():
                bl_vertex_group = cast(bpy.types.VertexGroup | None, bl_mesh_obj.vertex_groups.get(from_bone_name))
                if bl_vertex_group is None:
                    continue

                bl_vertex_group.name = to_bone_name

    def apply_bone_renames_to_cloth_strips(self, bl_armature_obj: bpy.types.Object, renames: dict[str, str]) -> None:
        bl_cloth_empty = Enumerable(bl_armature_obj.children).first_or_none(lambda o: not o.data and BlenderNaming.is_cloth_empty_name(o.name))
        if bl_cloth_empty is None:
            return
        
        for bl_cloth_strip_obj in Enumerable(bl_cloth_empty.children).where(lambda o: isinstance(o.data, bpy.types.Mesh)):
            cloth_properties = ObjectProperties.get_instance(bl_cloth_strip_obj).cloth
            if not cloth_properties.parent_bone_name:
                continue

            new_parent_bone_name = renames.get(cloth_properties.parent_bone_name)
            if not new_parent_bone_name:
                continue

            cloth_properties.parent_bone_name = new_parent_bone_name
    
    def move_armature_children(self, bl_source_armature_obj: bpy.types.Object, bl_target_armature_obj: bpy.types.Object) -> None:
        for bl_mesh_obj in Enumerable(bl_source_armature_obj.children_recursive).where(lambda o: isinstance(o.data, bpy.types.Mesh)):
            bl_armature_modifier = Enumerable(bl_mesh_obj.modifiers).of_type(bpy.types.ArmatureModifier).first_or_none()
            if bl_armature_modifier is not None and bl_armature_modifier.object == bl_source_armature_obj:
                bl_armature_modifier.object = bl_target_armature_obj
        
        for bl_obj in Enumerable(bl_source_armature_obj.children):
            bl_obj.parent = bl_target_armature_obj
