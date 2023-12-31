import os
from typing import Iterable, cast
import bpy
from bpy.types import Context, Menu, Operator, Event
from bpy.props import StringProperty                                    # type: ignore
from bpy_extras.io_utils import ExportHelper
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.ModelExporter import ModelExporter
from io_scene_sottr.ModelSplitter import ModelSplitter
from io_scene_sottr.operator.OperatorCommon import OperatorCommon
from io_scene_sottr.operator.OperatorContext import OperatorContext
from io_scene_sottr.util.DictionaryExtensions import DictionaryExtensions
from io_scene_sottr.util.Enumerable import Enumerable

class ExportModelOperator(Operator, ExportHelper):                      # type: ignore
    bl_idname = "export_scene.tr11model"
    
    bl_menu = cast(Menu, bpy.types.TOPBAR_MT_file_export)
    bl_menu_item_name = "SOTTR model (.tr11model)"
    
    filename_ext = ".tr11model"
    filter_glob: StringProperty(                                        # type: ignore
        default = "*" + filename_ext,
        options = { "HIDDEN" }
    )
    bl_label = "Export"

    def invoke(self, context: Context, event: Event) -> set[str]:       # type: ignore
        with OperatorContext.begin(self):
            bl_mesh_objs_to_export = self.get_mesh_objects_to_export(False)
            if len(bl_mesh_objs_to_export) == 0:
                OperatorContext.log_error("No SOTTR meshes found in scene.")
                return { "CANCELLED" }

            folder_path: str
            if getattr(self.properties, "filepath"):
                folder_path = os.path.split(getattr(self.properties, "filepath"))[0]
            elif context.blend_data.filepath:
                folder_path = os.path.split(context.blend_data.filepath)[0]
            else:
                folder_path = ""

            model_id = BlenderNaming.parse_mesh_name(Enumerable(bl_mesh_objs_to_export).first().name).model_id
            setattr(self.properties, "filepath", os.path.join(folder_path, str(model_id) + self.filename_ext))
            context.window_manager.fileselect_add(self)
            return { "RUNNING_MODAL" }

    def execute(self, context: Context) -> set[str]:
        with OperatorContext.begin(self):
            bl_local_collection = cast(bpy.types.LayerCollection | None, bpy.context.view_layer.layer_collection.children.get(BlenderNaming.local_collection_name))
            was_local_collection_excluded = False
            if bl_local_collection is not None:
                was_local_collection_excluded = bl_local_collection.exclude
                bl_local_collection.exclude = False
            
            bl_mesh_objs = self.get_mesh_objects_to_export(True)
            
            exporter = ModelExporter(OperatorCommon.scale_factor)
            folder_path = os.path.split(getattr(self.properties, "filepath"))[0]
            for model_id_set, bl_mesh_objs_of_model in Enumerable(bl_mesh_objs).group_by(lambda o: BlenderNaming.parse_model_name(o.name)).items():
                exporter.export_model(folder_path, model_id_set.model_id, model_id_set.model_data_id, bl_mesh_objs_of_model)
            
            if bl_local_collection is not None:
                bl_local_collection.exclude = was_local_collection_excluded
            
            if not OperatorContext.warnings_logged and not OperatorContext.errors_logged:
                OperatorContext.log_info("Model successfully exported.")
            
            return { "FINISHED" }

    def get_mesh_objects_to_export(self, split_global_meshes: bool) -> set[bpy.types.Object]:
        bl_mesh_objs_by_model_id: dict[int, list[bpy.types.Object]] = {}
        for bl_obj in Enumerable(bpy.context.scene.objects).where(lambda o: isinstance(o.data, bpy.types.Mesh)):
            mesh_id_set = BlenderNaming.try_parse_mesh_name(bl_obj.name)
            if mesh_id_set is not None and not self.is_in_local_collection(bl_obj):
                DictionaryExtensions.get_or_add(bl_mesh_objs_by_model_id, mesh_id_set.model_id, lambda: []).append(bl_obj)

        bl_mesh_objs_to_export = self.get_mesh_object_subset_to_export(bpy.context.selected_objects, split_global_meshes, bl_mesh_objs_by_model_id)
        if len(bl_mesh_objs_to_export) == 0:
            bl_mesh_objs_to_export = self.get_mesh_object_subset_to_export(bpy.context.scene.objects, split_global_meshes, bl_mesh_objs_by_model_id)
        
        return bl_mesh_objs_to_export

    def get_mesh_object_subset_to_export(self, bl_objs: Iterable[bpy.types.Object], split_global_meshes: bool, bl_mesh_objs_by_model_id: dict[int, list[bpy.types.Object]]) -> set[bpy.types.Object]:
        bl_mesh_objs_to_export: set[bpy.types.Object] = set()
        bl_visited_armature_objs: set[bpy.types.Object] = set()

        for object_name in Enumerable(bl_objs).where(lambda o: not self.is_in_local_collection(o)).select(lambda o: o.name).to_list():
            bl_obj = bpy.data.objects[object_name]

            if isinstance(bl_obj.data, bpy.types.Mesh):
                mesh_id_set = BlenderNaming.try_parse_mesh_name(bl_obj.name)
                if mesh_id_set is None:
                    continue

                if bl_obj.parent and isinstance(bl_obj.parent.data, bpy.types.Armature):
                    bl_obj = bl_obj.parent
                else:
                    bl_mesh_objs_to_export.update(bl_mesh_objs_by_model_id[mesh_id_set.model_id])
            
            if isinstance(bl_obj.data, bpy.types.Armature) and bl_obj not in bl_visited_armature_objs:
                bl_visited_armature_objs.add(bl_obj)
                bl_armature_objs: list[bpy.types.Object] = [bl_obj]
                if BlenderNaming.is_global_armature_name(bl_obj.data.name) and split_global_meshes:
                    bl_armature_objs = ModelSplitter().split(bl_obj)
                
                bl_mesh_objs_to_export.update(Enumerable(bl_armature_objs).select_many(self.get_mesh_children_of_armature))
        
        return bl_mesh_objs_to_export
    
    def is_in_local_collection(self, bl_obj: bpy.types.Object) -> bool:
        bl_collections = Enumerable(cast(Iterable[bpy.types.Collection], bl_obj.users_collection))
        return bl_collections.any(lambda c: c.name == BlenderNaming.local_collection_name)
    
    def get_mesh_children_of_armature(self, bl_armature_obj: bpy.types.Object) -> Iterable[bpy.types.Object]:
        return Enumerable(cast(Iterable[bpy.types.Object], bl_armature_obj.children)).where(
            lambda o: isinstance(o.data, bpy.types.Mesh) and BlenderNaming.try_parse_mesh_name(o.name) is not None)
