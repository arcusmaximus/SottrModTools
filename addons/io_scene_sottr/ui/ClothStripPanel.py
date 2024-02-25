import bpy
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.properties.ObjectProperties import ObjectProperties

class ClothStripPanel(bpy.types.Panel):
    bl_idname = "SOTTR_PT_ClothStripPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SOTTR Cloth"
    bl_label = "Strip"
    
    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        bl_obj = context.active_object
        return bl_obj and BlenderNaming.try_parse_cloth_strip_name(bl_obj.name) is not None

    def draw(self, context: bpy.types.Context) -> None:
        props = ObjectProperties.get_instance(context.active_object)
        self.layout.prop(props.cloth, "parent_bone_name", icon = "BONE_DATA")
        self.layout.prop(props.cloth, "gravity_factor")
        self.layout.prop(props.cloth, "wind_factor")
        self.layout.prop(props.cloth, "stiffness")
        self.layout.prop(props.cloth, "rigidity")
        self.layout.prop(props.cloth, "dampening")
