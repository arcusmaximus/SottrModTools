import bpy
from io_scene_tr_reboot.BlenderNaming import BlenderNaming
from io_scene_tr_reboot.properties.ObjectProperties import ObjectProperties
from io_scene_tr_reboot.properties.SceneProperties import SceneProperties
from io_scene_tr_reboot.tr.Factories import Factories

class ClothStripPanel(bpy.types.Panel):
    bl_idname = "TR_PT_ClothStripPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tomb Raider Cloth"
    bl_label = "Strip"

    @classmethod
    def poll(cls, context: bpy.types.Context | None) -> bool:
        if context is None:
            return False

        bl_obj = context.active_object
        return bl_obj is not None and BlenderNaming.try_parse_cloth_strip_name(bl_obj.name) is not None

    def draw(self, context: bpy.types.Context | None) -> None:
        if context is None:
            return

        bl_obj = context.active_object
        if bl_obj is None:
            return

        props = ObjectProperties.get_instance(bl_obj).cloth
        cloth_class = Factories.get(SceneProperties.get_game()).cloth_class
        self.layout.prop(props, "parent_bone_name", icon = "BONE_DATA")
        self.layout.prop(props, "gravity_factor")
        self.layout.prop(props, "wind_factor")

        if cloth_class.supports.strip_pose_follow_factor:
            self.layout.prop(props, "stiffness")

        self.layout.prop(props, "rigidity")

        if not cloth_class.supports.mass_specific_bounceback_factor:
            self.layout.prop(props, "bounceback_factor")

        self.layout.prop(props, "dampening")
