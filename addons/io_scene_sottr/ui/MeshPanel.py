import bpy
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.operator.BrowseBlendShapeNormalsSourceFileOperator import BrowseBlendShapeNormalsSourceFileOperator
from io_scene_sottr.operator.FixVertexGroupNamesOperator import FixVertexGroupNamesOperator
from io_scene_sottr.properties.ObjectProperties import ObjectProperties

class MeshPanel(bpy.types.Panel):
    bl_idname = "SOTTR_PT_MeshObjectPanel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "SOTTR Mesh Properties"
    
    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        bl_obj = context.object
        return bl_obj and isinstance(bl_obj.data, bpy.types.Mesh) and BlenderNaming.try_parse_mesh_name(bl_obj.name) is not None

    def draw(self, context: bpy.types.Context) -> None:
        props = ObjectProperties.get_instance(context.object)

        self.layout.operator(FixVertexGroupNamesOperator.bl_idname)
        
        self.layout.label(text = "Shape Key Normals Source")
        row = self.layout.row(align = True)
        row.prop(props, "blend_shape_normals_source_file_path", text = "")
        row.operator(BrowseBlendShapeNormalsSourceFileOperator.bl_idname, icon = "FILE_FOLDER", text = "")
