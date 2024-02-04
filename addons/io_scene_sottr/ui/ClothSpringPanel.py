import bpy
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.properties.ToolSettingProperties import ToolSettingProperties

class ClothSpringPanel(bpy.types.Panel):
    bl_idname = "SOTTR_PT_ClothSpringPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SOTTR Cloth"
    bl_label = "Springs"
    
    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.edit_object and BlenderNaming.try_parse_cloth_strip_name(context.edit_object.name) is not None

    def draw(self, context: bpy.types.Context) -> None:
        properties = ToolSettingProperties.get_instance(context.scene)
        self.layout.prop(properties, "cloth_spring_stretchiness")
