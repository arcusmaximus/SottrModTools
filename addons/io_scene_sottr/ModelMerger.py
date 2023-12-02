from typing import Iterable, cast
import bpy
from io_scene_sottr.BlenderHelper import BlenderHelper
from io_scene_sottr.BlenderNaming import BlenderNaming
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
            bpy.ops.object.mode_set(mode = "OBJECT")                # type: ignore

        bl_global_armature_obj = self.add_local_armature_to_global(bl_global_armature_obj, bl_local_armature_obj)
        BlenderHelper.move_object_to_collection(bl_local_armature_obj, self.bl_local_collection)

        bl_mesh_objs = Enumerable(cast(Iterable[bpy.types.Object], bl_local_armature_obj.children)).where(lambda o: isinstance(o.data, bpy.types.Mesh)).to_list()
        model_id_sets = Enumerable(bl_mesh_objs).select(lambda o: BlenderNaming.parse_model_name(o))                        \
                                                .distinct()                                                                 \
                                                .to_list()
        for bl_mesh_obj in bl_mesh_objs:
            self.move_mesh_to_global_armature(bl_mesh_obj, bl_global_armature_obj)
        
        for model_id_set in model_id_sets:
            bl_local_empty = BlenderHelper.create_object(None, BlenderNaming.make_local_empty_name(model_id_set.model_id, model_id_set.model_data_id))
            bl_local_empty.parent = bl_local_armature_obj
            BlenderHelper.move_object_to_collection(bl_local_empty, self.bl_local_collection)

        return bl_global_armature_obj

    def add_local_armature_to_global(self, bl_global_armature_obj: bpy.types.Object | None, bl_local_armature_obj: bpy.types.Object) -> bpy.types.Object:
        local_skeleton_id = BlenderNaming.parse_local_armature_name(bl_local_armature_obj.data.name)
        global_bone_parent_ids = self.get_global_bone_parents_from_local_armature(bl_local_armature_obj)
        global_visible_bone_ids = self.get_visible_global_bones_from_local_armature(bl_local_armature_obj)

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
                Enumerable(BlenderNaming.parse_global_armature_name(bl_global_armature_obj.data.name)).concat([local_skeleton_id]))
            
            BlenderHelper.join_objects(bl_global_armature_obj, [bl_copied_local_armature_obj])
            self.apply_global_bone_parents_to_global_armature(bl_global_armature_obj, global_bone_parent_ids)
            self.apply_visible_global_bones_to_global_armature(bl_global_armature_obj, global_visible_bone_ids)
        
        bl_global_armature_obj.name = global_armature_name
        bl_global_armature_obj.data.name = global_armature_name
        return bl_global_armature_obj

    def get_global_bone_parents_from_local_armature(self, bl_local_armature_obj: bpy.types.Object) -> dict[int, int]:
        bl_local_armature = cast(bpy.types.Armature, bl_local_armature_obj.data)
        bone_parents: dict[int, int] = {}
        for bl_bone in bl_local_armature.bones:
            if cast(bpy.types.Bone | None, bl_bone.parent) is None:
                continue

            child_bone_ids  = BlenderNaming.parse_local_bone_name(bl_bone.name)
            parent_bone_ids = BlenderNaming.parse_local_bone_name(bl_bone.parent.name)
            if child_bone_ids.global_id is not None and parent_bone_ids.global_id is not None:
                bone_parents[child_bone_ids.global_id] = parent_bone_ids.global_id

        return bone_parents
    
    def apply_global_bone_parents_to_global_armature(self, bl_global_armature_obj: bpy.types.Object, bone_parents: dict[int, int]) -> None:
        bl_global_armature = cast(bpy.types.Armature, bl_global_armature_obj.data)
        with BlenderHelper.enter_edit_mode():
            for child_bone_id, parent_bone_id in bone_parents.items():
                bl_child_bone = bl_global_armature.edit_bones[BlenderNaming.make_global_bone_name(child_bone_id)]
                bl_parent_bone = bl_global_armature.edit_bones[BlenderNaming.make_global_bone_name(parent_bone_id)]
                bl_child_bone.parent = bl_parent_bone
    
    def get_visible_global_bones_from_local_armature(self, bl_local_armature_obj: bpy.types.Object) -> list[int]:
        visible_bone_ids: list[int] = []
        bl_local_armature = cast(bpy.types.Armature, bl_local_armature_obj.data)
        for bl_bone in bl_local_armature.bones:
            if not bl_bone.layers[0]:
                continue

            bone_ids = BlenderNaming.parse_local_bone_name(bl_bone.name)
            if bone_ids.global_id is None:
                continue

            visible_bone_ids.append(bone_ids.global_id)
        
        return visible_bone_ids
    
    def apply_visible_global_bones_to_global_armature(self, bl_global_armature_obj: bpy.types.Object, visible_bone_ids: list[int]) -> None:
        bl_global_armature = cast(bpy.types.Armature, bl_global_armature_obj.data)
        for bone_id in visible_bone_ids:
            bl_global_armature.bones[BlenderNaming.make_global_bone_name(bone_id)].layers[0] = True
    
    def convert_local_armature_to_global(self, bl_local_armature_obj: bpy.types.Object, bl_existing_global_armature_obj: bpy.types.Object | None) -> None:
        bl_existing_global_armature = bl_existing_global_armature_obj is not None and cast(bpy.types.Armature, bl_existing_global_armature_obj.data) or None
        bl_local_armature = cast(bpy.types.Armature, bl_local_armature_obj.data)

        with BlenderHelper.enter_edit_mode():
            for local_bone_name in Enumerable(bl_local_armature.edit_bones).select(lambda b: b.name).to_list():
                bl_bone = bl_local_armature.edit_bones[local_bone_name]
                global_bone_id = BlenderNaming.parse_local_bone_name(local_bone_name).global_id
                if global_bone_id is None:
                    bl_local_armature.edit_bones.remove(bl_bone)
                else:
                    global_bone_name = BlenderNaming.make_global_bone_name(global_bone_id)
                    if bl_existing_global_armature is None or bl_existing_global_armature.bones.get(global_bone_name) is None:
                        bl_bone.name = global_bone_name
                    else:
                        bl_local_armature.edit_bones.remove(bl_bone)
    
    def move_mesh_to_global_armature(self, bl_mesh_obj: bpy.types.Object, bl_global_armature_obj: bpy.types.Object) -> None:
        bl_mesh_obj.parent = bl_global_armature_obj
                
        bl_armature_modifier = Enumerable(bl_mesh_obj.modifiers).of_type(bpy.types.ArmatureModifier).first_or_none()
        if bl_armature_modifier is not None:
            bl_armature_modifier.object = bl_global_armature_obj
        
        for vertex_group_name in Enumerable(bl_mesh_obj.vertex_groups).select(lambda g: g.name).to_list():
            local_bone_ids = BlenderNaming.parse_local_bone_name(vertex_group_name)
            bl_vertex_group = bl_mesh_obj.vertex_groups[vertex_group_name]
            if local_bone_ids.global_id is None:
                bl_mesh_obj.vertex_groups.remove(bl_vertex_group)
            else:
                bl_vertex_group.name = BlenderNaming.make_global_bone_name(local_bone_ids.global_id)
