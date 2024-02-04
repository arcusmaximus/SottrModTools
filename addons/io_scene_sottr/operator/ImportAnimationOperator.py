import bpy
from io_scene_sottr.exchange.AnimationImporter import AnimationImporter
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.operator.BlenderOperatorBase import ImportOperatorBase, ImportOperatorProperties
from io_scene_sottr.operator.OperatorCommon import OperatorCommon
from io_scene_sottr.operator.OperatorContext import OperatorContext
from io_scene_sottr.util.Enumerable import Enumerable

class ImportAnimationOperator(ImportOperatorBase[ImportOperatorProperties]):
    bl_idname = "import_scene.tr11anim"
    bl_menu_item_name = "SOTTR animation (.tr11anim)"
    filename_ext = ".tr11anim"

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        with OperatorContext.begin(self):
            bl_armature_obj = self.get_target_armature()
            if bl_armature_obj is None:
                return { "CANCELLED" }

            context.window_manager.fileselect_add(self)
            return { "RUNNING_MODAL" }
    
    def execute(self, context: bpy.types.Context) -> set[str]:
        with OperatorContext.begin(self):
            bl_armature_obj = self.get_target_armature()
            if bl_armature_obj is None:
                return { "CANCELLED" }
            
            importer = AnimationImporter(OperatorCommon.scale_factor)
            importer.import_animation(getattr(self.properties, "filepath"), bl_armature_obj)
            return { "FINISHED" }

    def get_target_armature(self) -> bpy.types.Object | None:
        bl_selected_obj = bpy.context.object
        if bl_selected_obj and isinstance(bl_selected_obj.data, bpy.types.Armature):
            return bl_selected_obj
        
        if bl_selected_obj and bl_selected_obj.parent and isinstance(bl_selected_obj.parent.data, bpy.types.Armature):
            return bl_selected_obj.parent
    
        bl_armature_objs = Enumerable(bpy.context.scene.objects).where(lambda o: isinstance(o.data, bpy.types.Armature) and not self.is_in_local_collection(o)).to_list()
        if len(bl_armature_objs) == 0:
            OperatorContext.log_error("No armature found in scene. Please import a model first.")
            return None
        
        if len(bl_armature_objs) > 1:
            OperatorContext.log_error("Please select the target armature.")
            return None
        
        return bl_armature_objs[0]
    
    def is_in_local_collection(self, bl_obj: bpy.types.Object) -> bool:
        return Enumerable(bl_obj.users_collection).any(lambda c: c.name == BlenderNaming.local_collection_name)
