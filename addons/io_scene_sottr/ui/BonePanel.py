import bpy
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.properties.BoneProperties import BoneProperties

class BonePanel(bpy.types.Panel):
    bl_idname = "SOTTR_PT_BonePanel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "bone"
    bl_label = "SOTTR Bone Properties"
    
    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        bl_bone = context.bone
        if not bl_bone:
            return False
        
        bone_id_set = BlenderNaming.try_parse_bone_name(bl_bone.name)
        return bone_id_set is not None and bone_id_set.global_id is not None

    def draw(self, context: bpy.types.Context) -> None:
        props = BoneProperties.get_instance(context.bone)
        self.layout.prop(props, "counterpart_bone_name", icon = "BONE_DATA")
