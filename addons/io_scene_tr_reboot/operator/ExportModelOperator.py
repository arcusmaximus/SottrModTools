import os
import shutil
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
from io_scene_tr_reboot.exchange.tr2013.Tr2013ModelExporter import Tr2013ModelExporter
from io_scene_tr_reboot.exchange.tr2013.Tr2013SkeletonExporter import Tr2013SkeletonExporter
from io_scene_tr_reboot.operator.BlenderOperatorBase import ExportOperatorBase, ExportOperatorProperties
from io_scene_tr_reboot.operator.OperatorCommon import OperatorCommon
from io_scene_tr_reboot.operator.OperatorContext import OperatorContext
from io_scene_tr_reboot.properties.BlenderPropertyGroup import Prop
from io_scene_tr_reboot.properties.SceneProperties import SceneProperties
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

class ExportModelOperator(ExportOperatorBase[_Properties]):
    bl_idname = "export_scene.trmodel"
    bl_menu_item_name = "Tomb Raider Reboot model (.trXmodeldata)"
    filename_ext = ""

    def invoke(self, context: Context | None, event: Event) -> set[OperatorReturnItems]:
        if context is None:
            return { "CANCELLED" }

        game = SceneProperties.get_game()
        ExportModelOperator.filename_ext = f".tr{game}modeldata"
        self.properties.filter_glob = "*" + ExportModelOperator.filename_ext

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

            model_data_id = BlenderNaming.parse_mesh_name(Enumerable(bl_mesh_objs).first().name).model_data_id
            self.properties.filepath = os.path.join(folder_path, str(model_data_id) + self.filename_ext)
            context.window_manager.fileselect_add(self)
            return { "RUNNING_MODAL" }

    def draw(self, context: Context) -> None:
        game = SceneProperties.get_game()
        if not self.requires_skeleton_export(game):
            self.layout.prop(self.properties, "export_skeleton")

        if not self.requires_cloth_export(game):
            self.layout.prop(self.properties, "export_cloth")

    def execute(self, context: Context | None) -> set[OperatorReturnItems]:
        if context is None:
            return { "CANCELLED" }

        game = SceneProperties.get_game()

        with OperatorContext.begin(self):
            bl_local_collection = context.view_layer.layer_collection.children.get(BlenderNaming.local_collection_name)
            was_local_collection_excluded = False
            if bl_local_collection is not None:
                was_local_collection_excluded = bl_local_collection.exclude
                bl_local_collection.exclude = False

            bl_mesh_objs = self.get_mesh_objects_to_export(context, True)

            model_exporter = self.create_model_exporter(OperatorCommon.scale_factor, game)
            folder_path = os.path.split(self.properties.filepath)[0]
            for model_id_set, bl_mesh_objs_of_model in Enumerable(bl_mesh_objs).group_by(lambda o: BlenderNaming.parse_model_name(o.name)).items():
                bl_armature_obj = bl_mesh_objs_of_model[0].parent
                if bl_armature_obj is not None and not isinstance(bl_armature_obj.data, bpy.types.Armature):
                    bl_armature_obj = None

                model_exporter.export_model(folder_path, model_id_set, bl_mesh_objs_of_model, bl_armature_obj)

            if self.properties.export_cloth or self.requires_cloth_export(game):
                bl_unsplit_mesh_objs = self.get_mesh_objects_to_export(context, False)
                bl_armature_obj = Enumerable(bl_unsplit_mesh_objs).select(lambda o: o.parent).first_or_none(lambda o: o is not None and isinstance(o.data, bpy.types.Armature))
                if bl_armature_obj is not None:
                    cloth_exporter = self.create_cloth_exporter(OperatorCommon.scale_factor, game)
                    cloth_exporter.export_cloths(folder_path, bl_armature_obj, self.get_local_armatures(context))

            if self.properties.export_skeleton or self.requires_skeleton_export(game):
                skeleton_exporter = self.create_skeleton_exporter(OperatorCommon.scale_factor, game)
                for bl_armature_obj in Enumerable(bl_mesh_objs).select(lambda o: o.parent) \
                                                               .of_type(bpy.types.Object) \
                                                               .where(lambda o: isinstance(o.data, bpy.types.Armature)) \
                                                               .distinct():
                    skeleton_exporter.export(folder_path, bl_armature_obj)

            if bl_local_collection is not None:
                bl_local_collection.exclude = was_local_collection_excluded

            if game == CdcGame.TR2013:
                self.copy_tr2013_model_dtps(folder_path)

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

    def create_model_exporter(self, scale_factor: float, game: CdcGame) -> ModelExporter:
        match game:
            case CdcGame.TR2013:
                return Tr2013ModelExporter(scale_factor)
            case CdcGame.SOTTR:
                return ShadowModelExporter(scale_factor)
            case _:
                return ModelExporter(scale_factor, game)

    def requires_skeleton_export(self, game: CdcGame) -> bool:
        return game == CdcGame.TR2013

    def create_skeleton_exporter(self, scale_factor: float, game: CdcGame) -> SkeletonExporter:
        match game:
            case CdcGame.TR2013:
                return Tr2013SkeletonExporter(scale_factor)
            case _:
                return SkeletonExporter(scale_factor, game)

    def requires_cloth_export(self, game: CdcGame) -> bool:
        return game == CdcGame.TR2013

    def create_cloth_exporter(self, scale_factor: float, game: CdcGame) -> ClothExporter:
        match game:
            case CdcGame.TR2013:
                return Tr2013ClothExporter(scale_factor)
            case _:
                return ClothExporter(scale_factor, game)

    def copy_tr2013_model_dtps(self, folder_path: str) -> None:
        model_id_groups: list[tuple[int, ...]] = [
            (2906, 2926, 23746),
            (6744, 23897, 50318, 50476, 50497),
            (21039, 21923, 21935, 23760, 102228),
            (23757, 62322, 62326),
            (23772, 29892, 29898),
            (23780, 34014, 34018, 34029),
            (23792, 106834),
            (23803, 106888),
            (23810, 106839),
            (23818, 78361, 78383),
            (23833, 45359, 46965, 48296, 48772, 48920, 50895),
            (23848, 53803),
            (23872, 58115, 58119, 58127),
            (23884, 60939, 60978, 105868),
            (23892, 62287, 62341, 62349, 62354),
            (23909, 84740),
            (23917, 106893, 108819, 108830, 108839)
        ]
        for model_id_group in model_id_groups:
            model_paths = Enumerable(model_id_group).select(lambda id: os.path.join(folder_path, f"{id}.tr9dtp")).to_list()
            exported_model_path_idx = Enumerable(model_paths).index_of(os.path.isfile)
            if exported_model_path_idx < 0:
                continue

            for i in range(len(model_paths)):
                if i != exported_model_path_idx:
                    shutil.copyfile(model_paths[exported_model_path_idx], model_paths[i])
