import bpy
from io_scene_tr_reboot.BlenderNaming import BlenderNaming
from io_scene_tr_reboot.properties.ToolSettingProperties import ToolSettingProperties

class ClothSpringPanel(bpy.types.Panel):
    bl_idname = "TR_PT_ClothSpringPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "TR Cloth"
    bl_label = "Springs"

    @classmethod
    def poll(cls, context: bpy.types.Context | None) -> bool:
        return context is not None and context.edit_object is not None and BlenderNaming.try_parse_cloth_strip_name(context.edit_object.name) is not None

    def draw(self, context: bpy.types.Context | None) -> None:
        if context is None:
            return

        properties = ToolSettingProperties.get_instance(context.scene)
        self.layout.prop(properties, "cloth_spring_stretchiness")
