from typing import cast
import bpy
from io_scene_sottr.BlenderHelper import BlenderHelper
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.properties.BoneProperties import BoneProperties
from io_scene_sottr.properties.ObjectProperties import ObjectProperties
from io_scene_sottr.tr.Cloth import ClothStrip
from io_scene_sottr.tr.Collection import Collection
from io_scene_sottr.tr.Hashes import Hashes
from io_scene_sottr.util.Enumerable import Enumerable
from io_scene_sottr.util.SlotsBase import SlotsBase

class ClothImporter(SlotsBase):
    scale_factor: float

    def __init__(self, scale_factor: float) -> None:
        self.scale_factor = scale_factor
    
    def import_from_collection(self, tr_collection: Collection, bl_armature_obj: bpy.types.Object) -> list[bpy.types.Object]:
        if bpy.context.object:
            bpy.ops.object.mode_set(mode = "OBJECT")

        skeleton_id = BlenderNaming.parse_local_armature_name(bl_armature_obj.name)

        cloth_empty_name = BlenderNaming.make_cloth_empty_name(tr_collection.name)
        bl_cloth_empty = bpy.data.objects.get(cloth_empty_name) or BlenderHelper.create_object(None, cloth_empty_name)
        bl_cloth_empty.parent = bl_armature_obj
        
        tr_cloth = tr_collection.get_cloth()
        if tr_cloth is None:
            bl_dummy_strip_obj = self.create_dummy_cloth_strip(tr_collection, bl_armature_obj)
            if bl_dummy_strip_obj is None:
                return []
            
            bl_dummy_strip_obj.parent = bl_cloth_empty
            return [bl_dummy_strip_obj]

        bl_strip_objs: list[bpy.types.Object] = []
        for tr_cloth_strip in tr_cloth.strips:
            strip_name = BlenderNaming.make_cloth_strip_name(tr_collection.name, skeleton_id, tr_cloth.definition_id, tr_cloth.component_id, tr_cloth_strip.id)
            bl_strip_obj = self.import_cloth_strip(tr_cloth_strip, strip_name, bl_armature_obj)
            bl_strip_obj.parent = bl_cloth_empty
            bl_strip_objs.append(bl_strip_obj)
        
        return bl_strip_objs

    def import_cloth_strip(self, tr_cloth_strip: ClothStrip, name: str, bl_armature_obj: bpy.types.Object) -> bpy.types.Object:
        vertex_positions = Enumerable(tr_cloth_strip.masses).select(lambda m: m.position * self.scale_factor).to_list()
        edge_vertex_indices = Enumerable(tr_cloth_strip.springs).select(lambda s: (s.mass_1_idx, s.mass_2_idx)).to_list()

        bl_mesh = bpy.data.meshes.new(name)
        bl_mesh.from_pydata(vertex_positions, edge_vertex_indices, [])

        bl_obj = BlenderHelper.create_object(bl_mesh)
        bl_obj.show_in_front = True

        bl_armature = cast(bpy.types.Armature, bl_armature_obj.data)

        cloth_strip_properties = ObjectProperties.get_instance(bl_obj).cloth
        cloth_strip_properties.parent_bone_name = Enumerable(bl_armature.bones).select(lambda b: b.name) \
                                                                               .first(lambda b: BlenderNaming.parse_bone_name(b).local_id == tr_cloth_strip.parent_bone_local_id)
        cloth_strip_properties.gravity_factor = tr_cloth_strip.gravity_factor
        cloth_strip_properties.wind_factor = tr_cloth_strip.wind_factor
        cloth_strip_properties.stiffness = tr_cloth_strip.pose_follow_factor
        cloth_strip_properties.rigidity = tr_cloth_strip.rigidity
        cloth_strip_properties.dampening = tr_cloth_strip.drag

        for i, tr_cloth_mass in enumerate(tr_cloth_strip.masses):
            bl_vertex_group = bl_obj.vertex_groups.new(name = BlenderNaming.make_bone_name(None, None, tr_cloth_mass.local_bone_id))
            bl_vertex_group.add([i], 1.0, "REPLACE")

            bl_bone = bl_armature.bones[bl_vertex_group.name]
            BoneProperties.get_instance(bl_bone).cloth.bounceback_factor = tr_cloth_mass.bounceback_factor
            if tr_cloth_mass.mass == 0:
                BlenderHelper.move_bone_to_group(bl_armature_obj, bl_bone, BlenderNaming.pinned_cloth_bone_group_name, BlenderNaming.pinned_cloth_bone_palette_name)
            else:
                BlenderHelper.move_bone_to_group(bl_armature_obj, bl_bone, BlenderNaming.unpinned_cloth_bone_group_name, BlenderNaming.unpinned_cloth_bone_palette_name)
        
        for i, tr_cloth_spring in enumerate(tr_cloth_strip.springs):
            BlenderHelper.set_edge_bevel_weight(bl_mesh, i, tr_cloth_spring.stretchiness)
        
        bl_armature_modifier = cast(bpy.types.ArmatureModifier, bl_obj.modifiers.new("Armature", "ARMATURE"))
        bl_armature_modifier.object = bl_armature_obj

        return bl_obj

    def create_dummy_cloth_strip(self, tr_collection: Collection, bl_armature_obj: bpy.types.Object) -> bpy.types.Object | None:
        cloth_definition_ref = tr_collection.header.cloth_definition_ref
        cloth_component = tr_collection.simple_components.get(Hashes.cloth)
        if cloth_definition_ref is None or cloth_component is None:
            return None
        
        skeleton_id = BlenderNaming.parse_local_armature_name(bl_armature_obj.name)
        
        name = BlenderNaming.make_cloth_strip_name(tr_collection.name, skeleton_id, cloth_definition_ref.id, cloth_component.id, 1111)
        bl_mesh = bpy.data.meshes.new(name = name)
        bl_obj = BlenderHelper.create_object(bl_mesh)

        bl_armature_modifier = cast(bpy.types.ArmatureModifier, bl_obj.modifiers.new("Armature", "ARMATURE"))
        bl_armature_modifier.object = bl_armature_obj
        
        return bl_obj
