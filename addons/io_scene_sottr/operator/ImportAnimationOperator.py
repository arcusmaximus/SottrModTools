from typing import Iterable, cast
import bpy
from bpy.types import Context, Menu, Operator, Event
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty                            # type: ignore
from io_scene_sottr.AnimationImporter import AnimationImporter
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.operator.OperatorCommon import OperatorCommon
from io_scene_sottr.operator.OperatorContext import OperatorContext
from io_scene_sottr.util.Enumerable import Enumerable

class ImportAnimationOperator(Operator, ImportHelper):          # type: ignore
    bl_idname = "import_scene.tr11anim"
    
    bl_menu = cast(Menu, bpy.types.TOPBAR_MT_file_import)
    bl_menu_item_name = "SOTTR animation (.tr11anim)"

    filename_ext = ".tr11anim"
    filter_glob: StringProperty(                                # type: ignore
        default = "*" + filename_ext,
        options = { "HIDDEN" }
    )
    bl_label = "Import"

    def invoke(self, context: Context, event: Event) -> set[str]:       # type: ignore
        with OperatorContext.begin(self):
            bl_armature_obj = self.get_target_armature()
            if bl_armature_obj is None:
                return { "CANCELLED" }

            context.window_manager.fileselect_add(self)
            return { "RUNNING_MODAL" }
    
    def execute(self, context: Context) -> set[str]:
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
        bl_collections = Enumerable(cast(Iterable[bpy.types.Collection], bl_obj.users_collection))
        return bl_collections.any(lambda c: c.name == BlenderNaming.local_collection_name)
