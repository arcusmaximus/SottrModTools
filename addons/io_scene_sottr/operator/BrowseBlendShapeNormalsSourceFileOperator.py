import bpy
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.operator.BlenderOperatorBase import ImportOperatorBase, ImportOperatorProperties
from io_scene_sottr.properties.ObjectProperties import ObjectProperties

class BrowseBlendShapeNormalsSourceFileOperator(ImportOperatorBase[ImportOperatorProperties]):
    bl_idname = "tr11.browse_blend_shape_normals_source_file"
    bl_label = "Select"
    bl_description = "Browse for .tr11modeldata file"
    bl_menu_item_name = "SOTTR model"
    filename_ext = ".tr11modeldata"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        bl_obj = context.object
        return bl_obj and isinstance(bl_obj.data, bpy.types.Mesh) and BlenderNaming.try_parse_mesh_name(bl_obj.name) is not None
    
    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        properties = ObjectProperties.get_instance(context.object)
        if properties.blend_shape_normals_source_file_path:
            self.properties.filepath = properties.blend_shape_normals_source_file_path
        else:
            mesh_id_set = BlenderNaming.parse_mesh_name(context.object.name)
            self.properties.filepath = f"{mesh_id_set.model_data_id}.tr11modeldata"
        
        return super().invoke(context, event)
    
    def execute(self, context: bpy.types.Context) -> set[str]:
        ObjectProperties.get_instance(context.object).blend_shape_normals_source_file_path = self.properties.filepath
        return { "FINISHED" }
