from typing import cast
import bpy
from io_scene_sottr.BlenderHelper import BlenderBoneGroup, BlenderHelper
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.properties.BoneProperties import BoneProperties
from io_scene_sottr.properties.ObjectProperties import ObjectProperties
from io_scene_sottr.util.Enumerable import Enumerable
from io_scene_sottr.util.SlotsBase import SlotsBase

class ModelMerger(SlotsBase):
    bl_local_collection: bpy.types.Collection

    def __init__(self) -> None:
        bl_local_collection = cast(bpy.types.Collection | None, bpy.data.collections.get(BlenderNaming.local_collection_name))
        if bl_local_collection is None:
            bl_local_collection = bpy.data.collections.new(BlenderNaming.local_collection_name)
            bpy.context.scene.collection.children.link(bl_local_collection)
            bpy.context.view_layer.layer_collection.children[bl_local_collection.name].exclude = True
        
        self.bl_local_collection = bl_local_collection

    def add(self, bl_global_armature_obj: bpy.types.Object | None, bl_local_armature_obj: bpy.types.Object) -> bpy.types.Object:
        if bpy.context.object:
            bpy.ops.object.mode_set(mode = "OBJECT")

        bl_global_armature_obj = self.add_local_armature_to_global(bl_global_armature_obj, bl_local_armature_obj)
        BlenderHelper.move_object_to_collection(bl_local_armature_obj, self.bl_local_collection)

        bl_mesh_objs = Enumerable(bl_local_armature_obj.children).where(lambda o: isinstance(o.data, bpy.types.Mesh)).to_list()
        model_id_sets = Enumerable(bl_mesh_objs).select(lambda o: BlenderNaming.parse_model_name(o.name))                   \
                                                .distinct()                                                                 \
                                                .to_list()
        for bl_mesh_obj in bl_mesh_objs:
            self.move_mesh_to_global_armature(bl_local_armature_obj, bl_mesh_obj, bl_global_armature_obj)
        
        for bl_empty in Enumerable(bl_local_armature_obj.children).where(lambda o: not o.data):
            bl_empty.parent = bl_global_armature_obj
            for bl_mesh_obj in Enumerable(bl_empty.children).where(lambda o: isinstance(o.data, bpy.types.Mesh)):
                self.move_mesh_to_global_armature(bl_local_armature_obj, bl_mesh_obj, bl_global_armature_obj)
        
        for model_id_set in model_id_sets:
            bl_local_empty = BlenderHelper.create_object(None, BlenderNaming.make_local_empty_name(model_id_set.model_id, model_id_set.model_data_id))
            bl_local_empty.parent = bl_local_armature_obj
            BlenderHelper.move_object_to_collection(bl_local_empty, self.bl_local_collection)

        return bl_global_armature_obj

    def add_local_armature_to_global(self, bl_global_armature_obj: bpy.types.Object | None, bl_local_armature_obj: bpy.types.Object) -> bpy.types.Object:
        local_skeleton_id = BlenderNaming.parse_local_armature_name(bl_local_armature_obj.name)
        global_bone_parent_ids = self.get_global_bone_parents_from_local_armature(bl_local_armature_obj)
        global_visible_bone_ids = self.get_visible_global_bones_from_local_armature(bl_local_armature_obj)
        global_bone_groups = self.get_bone_groups_from_armature(bl_local_armature_obj, True)

        bl_copied_local_armature = cast(bpy.types.Armature, bl_local_armature_obj.data.copy())
        bl_copied_local_armature_obj = BlenderHelper.create_object(bl_copied_local_armature)
        bl_copied_local_armature_obj.show_in_front = True

        self.convert_local_armature_to_global(bl_copied_local_armature_obj, bl_global_armature_obj)

        global_armature_name: str
        if bl_global_armature_obj is None:
            bl_global_armature_obj = bl_copied_local_armature_obj
            global_armature_name = BlenderNaming.make_global_armature_name([local_skeleton_id])
        else:
            global_armature_name = BlenderNaming.make_global_armature_name(
                Enumerable(BlenderNaming.parse_global_armature_name(bl_global_armature_obj.name)).concat([local_skeleton_id]))
            
            existing_global_bone_groups = self.get_bone_groups_from_armature(bl_global_armature_obj, False)
            BlenderHelper.join_objects(bl_global_armature_obj, [bl_copied_local_armature_obj])
            self.apply_global_bone_parents_to_global_armature(bl_global_armature_obj, global_bone_parent_ids)
            self.apply_visible_global_bones_to_global_armature(bl_global_armature_obj, global_visible_bone_ids)
            self.apply_bone_groups_to_armature(bl_global_armature_obj, existing_global_bone_groups)
        
        bl_global_armature_obj.name = global_armature_name
        bl_global_armature_obj.data.name = global_armature_name
        self.apply_bone_groups_to_armature(bl_global_armature_obj, global_bone_groups)
        return bl_global_armature_obj

    def get_global_bone_parents_from_local_armature(self, bl_local_armature_obj: bpy.types.Object) -> dict[int, int]:
        bl_local_armature = cast(bpy.types.Armature, bl_local_armature_obj.data)
        bone_parents: dict[int, int] = {}
        for bl_bone in bl_local_armature.bones:
            if cast(bpy.types.Bone | None, bl_bone.parent) is None:
                continue

            child_bone_ids  = BlenderNaming.parse_bone_name(bl_bone.name)
            parent_bone_ids = BlenderNaming.parse_bone_name(bl_bone.parent.name)
            if child_bone_ids.global_id is not None and parent_bone_ids.global_id is not None:
                bone_parents[child_bone_ids.global_id] = parent_bone_ids.global_id

        return bone_parents
    
    def apply_global_bone_parents_to_global_armature(self, bl_global_armature_obj: bpy.types.Object, bone_parents: dict[int, int]) -> None:
        bl_global_armature = cast(bpy.types.Armature, bl_global_armature_obj.data)
        with BlenderHelper.enter_edit_mode():
            for child_bone_id, parent_bone_id in bone_parents.items():
                bl_child_bone  = bl_global_armature.edit_bones[BlenderNaming.make_bone_name(None, child_bone_id, None)]
                bl_parent_bone = bl_global_armature.edit_bones[BlenderNaming.make_bone_name(None, parent_bone_id, None)]
                bl_child_bone.parent = bl_parent_bone
    
    def get_visible_global_bones_from_local_armature(self, bl_local_armature_obj: bpy.types.Object) -> list[int]:
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
    
    def apply_visible_global_bones_to_global_armature(self, bl_global_armature_obj: bpy.types.Object, visible_bone_ids: list[int]) -> None:
        bl_global_armature = cast(bpy.types.Armature, bl_global_armature_obj.data)
        for bone_id in visible_bone_ids:
            BlenderHelper.set_bone_visible(bl_global_armature, bl_global_armature.bones[BlenderNaming.make_bone_name(None, bone_id, None)], True)
    
    def get_bone_groups_from_armature(self, bl_armature_obj: bpy.types.Object, convert_bone_names_to_global: bool) -> dict[str, BlenderBoneGroup]:
        result: dict[str, BlenderBoneGroup] = {}
        local_skeleton_id = convert_bone_names_to_global and BlenderNaming.parse_local_armature_name(bl_armature_obj.name) or 0
        for bl_bone in cast(bpy.types.Armature, bl_armature_obj.data).bones:
            bone_group = BlenderHelper.get_bone_group(bl_armature_obj, bl_bone)
            if bone_group is not None and bone_group.name != BlenderNaming.hidden_bone_group_name:
                bone_name = convert_bone_names_to_global and self.convert_local_bone_name_to_global(local_skeleton_id, bl_bone.name) or bl_bone.name
                result[bone_name] = bone_group
        
        return result
    
    def apply_bone_groups_to_armature(self, bl_armature_obj: bpy.types.Object, bone_groups: dict[str, BlenderBoneGroup]):
        bl_armature = cast(bpy.types.Armature, bl_armature_obj.data)
        for bone_name, bone_group in bone_groups.items():
            BlenderHelper.move_bone_to_group(bl_armature_obj, bl_armature.bones[bone_name], bone_group.name, bone_group.palette)
    
    def convert_local_armature_to_global(self, bl_local_armature_obj: bpy.types.Object, bl_existing_global_armature_obj: bpy.types.Object | None) -> None:
        bl_existing_global_armature = bl_existing_global_armature_obj is not None and cast(bpy.types.Armature, bl_existing_global_armature_obj.data) or None
        bl_local_armature = cast(bpy.types.Armature, bl_local_armature_obj.data)
        local_skeleton_id = BlenderNaming.parse_local_armature_name(bl_local_armature_obj.name)

        with BlenderHelper.enter_edit_mode():
            for local_bone_name in Enumerable(bl_local_armature.edit_bones).select(lambda b: b.name).to_list():
                bl_bone = bl_local_armature.edit_bones[local_bone_name]
                global_bone_name = self.convert_local_bone_name_to_global(local_skeleton_id, bl_bone.name)
                if bl_existing_global_armature is None or bl_existing_global_armature.bones.get(global_bone_name) is None:
                    bl_bone.name = global_bone_name
                else:
                    bl_local_armature.edit_bones.remove(bl_bone)
        
        for bl_bone in bl_local_armature.bones:
            bone_props = BoneProperties.get_instance(bl_bone)
            if len(bone_props.counterpart_bone_name) > 0:
                bone_props.counterpart_bone_name = self.convert_local_bone_name_to_global(local_skeleton_id, bone_props.counterpart_bone_name)
    
    def move_mesh_to_global_armature(self, bl_local_armature_obj: bpy.types.Object, bl_mesh_obj: bpy.types.Object, bl_global_armature_obj: bpy.types.Object) -> None:
        if bl_mesh_obj.parent == bl_local_armature_obj:
            bl_mesh_obj.parent = bl_global_armature_obj

        bl_armature_modifier = Enumerable(bl_mesh_obj.modifiers).of_type(bpy.types.ArmatureModifier).first_or_none()
        if bl_armature_modifier is not None:
            bl_armature_modifier.object = bl_global_armature_obj
        
        local_skeleton_id = BlenderNaming.parse_local_armature_name(bl_local_armature_obj.name)
        for vertex_group_name in Enumerable(bl_mesh_obj.vertex_groups).select(lambda g: g.name).to_list():
            bl_vertex_group = bl_mesh_obj.vertex_groups[vertex_group_name]
            bl_vertex_group.name = self.convert_local_bone_name_to_global(local_skeleton_id, vertex_group_name)
        
        cloth_strip_properties = ObjectProperties.get_instance(bl_mesh_obj).cloth
        if cloth_strip_properties.parent_bone_name:
            cloth_strip_properties.parent_bone_name = self.convert_local_bone_name_to_global(local_skeleton_id, cloth_strip_properties.parent_bone_name)
    
    def convert_local_bone_name_to_global(self, local_skeleton_id: int, local_bone_name: str) -> str:
        local_bone_ids = BlenderNaming.parse_bone_name(local_bone_name)
        if local_bone_ids.global_id is None:
            return BlenderNaming.make_bone_name(local_skeleton_id, local_bone_ids.global_id, local_bone_ids.local_id)
        else:
            return BlenderNaming.make_bone_name(None, local_bone_ids.global_id, None)
