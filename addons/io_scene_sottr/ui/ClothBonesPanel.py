import bpy
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.operator.PinClothBonesOperator import PinClothBonesOperator
from io_scene_sottr.operator.UnpinClothBonesOperator import UnpinClothBonesOperator
from io_scene_sottr.operator.RegenerateClothBonesOperator import RegenerateClothBonesOperator
from io_scene_sottr.properties.ToolSettingProperties import ToolSettingProperties
from io_scene_sottr.util.Enumerable import Enumerable

class ClothBonesPanel(bpy.types.Panel):
    bl_idname = "SOTTR_PT_ClothBonesPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SOTTR Cloth"
    bl_label = "Bones"

    def draw(self, context: bpy.types.Context) -> None:
        bl_row = self.layout.row()
        bl_row.operator(RegenerateClothBonesOperator.bl_idname)

        bl_row = self.layout.row(align = True)
        if context.mode == "POSE":
            bl_row.operator(PinClothBonesOperator.bl_idname)
            bl_row.operator(UnpinClothBonesOperator.bl_idname)

        if bpy.context.mode == "POSE" and Enumerable(bpy.context.selected_pose_bones).any(self.is_cloth_bone):
            properties = ToolSettingProperties.get_instance(context.scene)
            self.layout.prop(properties, "cloth_bone_bounceback_factor")

    def is_cloth_bone(self, bl_pose_bone: bpy.types.PoseBone) -> bool:
        bone_id_set = BlenderNaming.try_parse_bone_name(bl_pose_bone.name)
        return bone_id_set is not None and bone_id_set.global_id is None
    