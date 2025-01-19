from abc import abstractmethod
from typing import TYPE_CHECKING, Annotated, Protocol
import bpy
from bpy.types import Context
from io_scene_tr_reboot.BlenderHelper import BlenderHelper
from io_scene_tr_reboot.BlenderNaming import BlenderNaming
from io_scene_tr_reboot.PermanentSkeletonMerger import PermanentModelMerger
from io_scene_tr_reboot.SkeletonMerger import SkeletonMerger
from io_scene_tr_reboot.TemporarySkeletonMerger import TemporaryModelMerger
from io_scene_tr_reboot.exchange.ClothImporter import ClothImporter
from io_scene_tr_reboot.exchange.CollisionImporter import CollisionImporter
from io_scene_tr_reboot.exchange.ModelImporter import ModelImporter
from io_scene_tr_reboot.exchange.SkeletonImporter import SkeletonImporter
from io_scene_tr_reboot.exchange.tr2013.Tr2013ModelImporter import Tr2013ModelImporter
from io_scene_tr_reboot.operator.BlenderOperatorBase import ImportOperatorBase, ImportOperatorProperties
from io_scene_tr_reboot.operator.OperatorCommon import OperatorCommon
from io_scene_tr_reboot.operator.OperatorContext import OperatorContext
from io_scene_tr_reboot.properties.BlenderPropertyGroup import Prop
from io_scene_tr_reboot.tr.Enumerations import CdcGame
from io_scene_tr_reboot.tr.FactoryFactory import FactoryFactory
from io_scene_tr_reboot.util.Enumerable import Enumerable

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems
else:
    OperatorReturnItems = str

class _Properties(ImportOperatorProperties, Protocol):
    import_lods:                    Annotated[bool, Prop("Import LODs")]
    split_into_parts:               Annotated[bool, Prop("Split meshes into parts")]
    merge_with_existing_skeletons:  Annotated[bool, Prop("Merge with existing skeleton(s)", default = True)]
    keep_original_skeletons:        Annotated[bool, Prop("Keep original skeletons", default = True)]

class ImportObjectOperatorBase(ImportOperatorBase[_Properties]):
    bl_idname = ""
    bl_menu_item_name = ""
    filename_ext = ""

    @property
    @abstractmethod
    def game(self) -> CdcGame: ...

    def execute(self, context: Context | None) -> set[OperatorReturnItems]:
        if context is None:
            return { "CANCELLED" }

        with OperatorContext.begin(self):
            tr_collection = FactoryFactory.get(self.game).create_collection(self.properties.filepath)

            skeleton_importer = self.create_skeleton_importer(OperatorCommon.scale_factor)
            bl_armature_obj = skeleton_importer.import_from_collection(tr_collection)

            model_importer = self.create_model_importer(
                OperatorCommon.scale_factor,
                self.properties.import_lods,
                self.properties.split_into_parts
            )
            model_importer.import_from_collection(tr_collection, bl_armature_obj)

            if bl_armature_obj is not None:
                collision_importer = self.create_collision_importer(OperatorCommon.scale_factor)
                collision_importer.import_from_collection(tr_collection, bl_armature_obj)

                cloth_importer = self.create_cloth_importer(OperatorCommon.scale_factor)
                cloth_importer.import_from_collection(tr_collection, bl_armature_obj)

            if self.properties.merge_with_existing_skeletons and bl_armature_obj is not None:
                self.merge(context)

            BlenderHelper.view_all()
            return { "FINISHED" }

    def merge(self, context: bpy.types.Context) -> None:
        bl_armature_objs = Enumerable(context.scene.objects).where(lambda o: isinstance(o.data, bpy.types.Armature)).to_list()
        bl_global_armature_obj = Enumerable(bl_armature_objs).first_or_none(lambda o: BlenderNaming.is_global_armature_name(o.name))
        if bl_global_armature_obj is None and len(bl_armature_objs) == 1:
            return

        merger: SkeletonMerger = self.properties.keep_original_skeletons and TemporaryModelMerger() or PermanentModelMerger()
        for bl_armature_obj in bl_armature_objs:
            if bl_armature_obj == bl_global_armature_obj:
                continue

            if Enumerable(bl_armature_obj.children).any(lambda o: not o.data and BlenderNaming.is_local_empty_name(o.name)):
                continue

            bl_global_armature_obj = merger.add(bl_global_armature_obj, bl_armature_obj)

    def create_skeleton_importer(self, scale_factor: float) -> SkeletonImporter:
        return SkeletonImporter(scale_factor)

    def create_model_importer(self, scale_factor: float, import_lods: bool, split_into_parts: bool) -> ModelImporter:
        return ModelImporter(scale_factor, import_lods, split_into_parts)

    def create_collision_importer(self, scale_factor: float) -> CollisionImporter:
        return CollisionImporter(scale_factor)

    def create_cloth_importer(self, scale_factor: float) -> ClothImporter:
        return ClothImporter(scale_factor)

class ImportTr2013ObjectOperator(ImportObjectOperatorBase):
    bl_idname = "import_scene.tr9objectref"
    bl_menu_item_name = "TR2013 object (.tr9objectref)"
    filename_ext = ".tr9objectref"

    @property
    def game(self) -> CdcGame:
        return CdcGame.TR2013

    def create_model_importer(self, scale_factor: float, import_lods: bool, split_into_parts: bool) -> ModelImporter:
        return Tr2013ModelImporter(scale_factor, import_lods, split_into_parts)

class ImportRiseObjectOperator(ImportObjectOperatorBase):
    bl_idname = "import_scene.tr10objectref"
    bl_menu_item_name = "ROTTR object (.tr10objectref)"
    filename_ext = ".tr10objectref"

    @property
    def game(self) -> CdcGame:
        return CdcGame.ROTTR

class ImportShadowObjectOperator(ImportObjectOperatorBase):
    bl_idname = "import_scene.tr11objectref"
    bl_menu_item_name = "SOTTR object (.tr11objectref)"
    filename_ext = ".tr11objectref"

    @property
    def game(self) -> CdcGame:
        return CdcGame.SOTTR
