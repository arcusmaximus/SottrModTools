from abc import abstractmethod
import os
from typing import TYPE_CHECKING, Annotated, Iterable, Protocol
import bpy
from bpy.types import Context, Event
from io_scene_tr_reboot.BlenderNaming import BlenderNaming
from io_scene_tr_reboot.exchange.ClothExporter import ClothExporter
from io_scene_tr_reboot.exchange.ModelExporter import ModelExporter
from io_scene_tr_reboot.ModelSplitter import ModelSplitter
from io_scene_tr_reboot.exchange.SkeletonExporter import SkeletonExporter
from io_scene_tr_reboot.exchange.shadow.ShadowModelExporter import ShadowModelExporter
from io_scene_tr_reboot.exchange.tr2013.Tr2013ClothExporter import Tr2013ClothExporter
from io_scene_tr_reboot.exchange.tr2013.Tr2013SkeletonExporter import Tr2013SkeletonExporter
from io_scene_tr_reboot.operator.BlenderOperatorBase import ExportOperatorBase, ExportOperatorProperties
from io_scene_tr_reboot.operator.OperatorCommon import OperatorCommon
from io_scene_tr_reboot.operator.OperatorContext import OperatorContext
from io_scene_tr_reboot.properties.BlenderPropertyGroup import Prop
from io_scene_tr_reboot.tr.Enumerations import CdcGame
from io_scene_tr_reboot.util.DictionaryExtensions import DictionaryExtensions
from io_scene_tr_reboot.util.Enumerable import Enumerable

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems
else:
    OperatorReturnItems = str

class _Properties(ExportOperatorProperties, Protocol):
    export_skeleton: Annotated[bool, Prop("Export skeleton")]
    export_cloth: Annotated[bool, Prop("Export cloth")]

class ExportModelOperatorBase(ExportOperatorBase[_Properties]):
    bl_idname = ""
    bl_menu_item_name = ""
    filename_ext = ""

    @property
    @abstractmethod
    def game(self) -> CdcGame: ...

    def invoke(self, context: Context | None, event: Event) -> set[OperatorReturnItems]:
        if context is None:
            return { "CANCELLED" }

        with OperatorContext.begin(self):
            bl_mesh_objs = self.get_mesh_objects_to_export(context, False)
            if len(bl_mesh_objs) == 0:
                OperatorContext.log_error("No meshes found in scene.")
                return { "CANCELLED" }

            folder_path: str
            if self.properties.filepath:
                folder_path = os.path.split(self.properties.filepath)[0]
            elif context.blend_data.filepath:
                folder_path = os.path.split(context.blend_data.filepath)[0]
            else:
                folder_path = ""

            model_id = BlenderNaming.parse_mesh_name(Enumerable(bl_mesh_objs).first().name).model_id
            self.properties.filepath = os.path.join(folder_path, str(model_id) + self.filename_ext)
            context.window_manager.fileselect_add(self)
            return { "RUNNING_MODAL" }

    def execute(self, context: Context | None) -> set[OperatorReturnItems]:
        if context is None:
            return { "CANCELLED" }

        with OperatorContext.begin(self):
            bl_local_collection = context.view_layer.layer_collection.children.get(BlenderNaming.local_collection_name)
            was_local_collection_excluded = False
            if bl_local_collection is not None:
                was_local_collection_excluded = bl_local_collection.exclude
                bl_local_collection.exclude = False

            bl_mesh_objs = self.get_mesh_objects_to_export(context, True)

            model_exporter = self.create_model_exporter(OperatorCommon.scale_factor)
            folder_path = os.path.split(self.properties.filepath)[0]
            for model_id_set, bl_mesh_objs_of_model in Enumerable(bl_mesh_objs).group_by(lambda o: BlenderNaming.parse_model_name(o.name)).items():
                model_exporter.export_model(folder_path, model_id_set, bl_mesh_objs_of_model)

            if self.properties.export_skeleton or self.requires_skeleton_export:
                skeleton_exporter = self.create_skeleton_exporter(OperatorCommon.scale_factor)
                for bl_armature_obj in Enumerable(bl_mesh_objs).select(lambda o: o.parent) \
                                                               .of_type(bpy.types.Object) \
                                                               .where(lambda o: isinstance(o.data, bpy.types.Armature)) \
                                                               .distinct():
                    skeleton_exporter.export(folder_path, bl_armature_obj)

            if self.properties.export_cloth or self.requires_cloth_export:
                bl_unsplit_mesh_objs = self.get_mesh_objects_to_export(context, False)
                bl_armature_obj = Enumerable(bl_unsplit_mesh_objs).select(lambda o: o.parent).first_or_none(lambda o: o is not None and isinstance(o.data, bpy.types.Armature))
                if bl_armature_obj is not None:
                    cloth_exporter = self.create_cloth_exporter(OperatorCommon.scale_factor)
                    cloth_exporter.export_cloths(folder_path, bl_armature_obj, self.get_local_armatures(context))

            if bl_local_collection is not None:
                bl_local_collection.exclude = was_local_collection_excluded

            if not OperatorContext.warnings_logged and not OperatorContext.errors_logged:
                OperatorContext.log_info("Model successfully exported.")

            return { "FINISHED" }

    def get_mesh_objects_to_export(self, context: bpy.types.Context, split_global_meshes: bool) -> set[bpy.types.Object]:
        bl_mesh_objs_by_model_id: dict[int, list[bpy.types.Object]] = {}
        for bl_obj in Enumerable(context.scene.objects).where(lambda o: isinstance(o.data, bpy.types.Mesh)):
            mesh_id_set = BlenderNaming.try_parse_mesh_name(bl_obj.name)
            if mesh_id_set is not None and not self.is_in_local_collection(bl_obj):
                DictionaryExtensions.get_or_add(bl_mesh_objs_by_model_id, mesh_id_set.model_id, lambda: []).append(bl_obj)

        bl_mesh_objs_to_export = self.get_mesh_object_subset_to_export(context.selected_objects, split_global_meshes, bl_mesh_objs_by_model_id)
        if len(bl_mesh_objs_to_export) == 0:
            bl_mesh_objs_to_export = self.get_mesh_object_subset_to_export(context.scene.objects, split_global_meshes, bl_mesh_objs_by_model_id)

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
        return Enumerable(bl_obj.users_collection).any(lambda c: c.name == BlenderNaming.local_collection_name)

    def get_mesh_children_of_armature(self, bl_armature_obj: bpy.types.Object) -> Iterable[bpy.types.Object]:
        return Enumerable(bl_armature_obj.children).where(
            lambda o: isinstance(o.data, bpy.types.Mesh) and BlenderNaming.try_parse_mesh_name(o.name) is not None)

    def get_local_armatures(self, context: bpy.types.Context) -> dict[int, bpy.types.Object]:
        return Enumerable(context.scene.objects).where(lambda o: isinstance(o.data, bpy.types.Armature) and self.is_in_local_collection(o)) \
                                                .to_dict(lambda o: BlenderNaming.parse_local_armature_name(o.name))

    def create_model_exporter(self, scale_factor: float) -> ModelExporter:
        return ModelExporter(scale_factor, self.game)

    @property
    def requires_skeleton_export(self) -> bool:
        return False

    def create_skeleton_exporter(self, scale_factor: float) -> SkeletonExporter:
        return SkeletonExporter(scale_factor, self.game)

    @property
    def requires_cloth_export(self) -> bool:
        return False

    def create_cloth_exporter(self, scale_factor: float) -> ClothExporter:
        return ClothExporter(scale_factor, self.game)

class ExportTr2013ModelOperator(ExportModelOperatorBase):
    bl_idname = "export_scene.tr9model"
    bl_menu_item_name = "TR2013 model (.tr9model)"
    filename_ext = ".tr9model"

    @property
    def game(self) -> CdcGame:
        return CdcGame.TR2013

    def create_skeleton_exporter(self, scale_factor: float) -> SkeletonExporter:
        return Tr2013SkeletonExporter(scale_factor)

    def create_cloth_exporter(self, scale_factor: float) -> ClothExporter:
        return Tr2013ClothExporter(scale_factor)

    @property
    def requires_skeleton_export(self) -> bool:
        return True

    @property
    def requires_cloth_export(self) -> bool:
        return True

class ExportRiseModelOperator(ExportModelOperatorBase):
    bl_idname = "export_scene.tr10model"
    bl_menu_item_name = "ROTTR model (.tr10model)"
    filename_ext = ".tr10model"

    @property
    def game(self) -> CdcGame:
        return CdcGame.ROTTR

class ExportShadowModelOperator(ExportModelOperatorBase):
    bl_idname = "export_scene.tr11model"
    bl_menu_item_name = "SOTTR model (.tr11model)"
    filename_ext = ".tr11model"

    @property
    def game(self) -> CdcGame:
        return CdcGame.SOTTR

    def create_model_exporter(self, scale_factor: float) -> ModelExporter:
        return ShadowModelExporter(scale_factor)
