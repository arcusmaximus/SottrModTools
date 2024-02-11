from typing import Annotated, Protocol
import bpy
from bpy.types import Context
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.exchange.ClothImporter import ClothImporter
from io_scene_sottr.exchange.CollisionImporter import CollisionImporter
from io_scene_sottr.exchange.ModelImporter import ModelImporter
from io_scene_sottr.ModelMerger import ModelMerger
from io_scene_sottr.exchange.SkeletonImporter import SkeletonImporter
from io_scene_sottr.operator.BlenderOperatorBase import ImportOperatorBase, ImportOperatorProperties
from io_scene_sottr.operator.OperatorCommon import OperatorCommon
from io_scene_sottr.operator.OperatorContext import OperatorContext
from io_scene_sottr.properties.BlenderPropertyGroup import Prop
from io_scene_sottr.tr.Collection import Collection
from io_scene_sottr.util.Enumerable import Enumerable

class _Properties(ImportOperatorProperties, Protocol):
    import_unlinked_models:         Annotated[bool, Prop("Import unlinked models")]
    import_lods:                    Annotated[bool, Prop("Import LODs")]
    import_cloth:                   Annotated[bool, Prop("Import cloth and collisions")]
    split_into_parts:               Annotated[bool, Prop("Split meshes into parts")]
    merge_with_existing_armatures:  Annotated[bool, Prop("Merge with existing armature(s)", default = True)]

class ImportObjectOperator(ImportOperatorBase[_Properties]):
    bl_idname = "import_scene.tr11objectref"
    bl_menu_item_name = "SOTTR object (.tr11objectref)"

    filename_ext = ".tr11objectref"

    def execute(self, context: Context) -> set[str]:
        with OperatorContext.begin(self):
            tr_collection = Collection(self.properties.filepath)

            skeleton_importer = SkeletonImporter(OperatorCommon.scale_factor, not self.properties.import_cloth)
            bl_armature_obj = skeleton_importer.import_from_collection(tr_collection)
            
            model_importer = ModelImporter(
                OperatorCommon.scale_factor,
                self.properties.import_unlinked_models,
                self.properties.import_lods,
                self.properties.split_into_parts
            )
            model_importer.import_from_collection(tr_collection, bl_armature_obj)

            if self.properties.import_cloth and bl_armature_obj is not None:
                collision_importer = CollisionImporter(OperatorCommon.scale_factor)
                collision_importer.import_from_collection(tr_collection, bl_armature_obj)
                
                cloth_importer = ClothImporter(OperatorCommon.scale_factor)
                cloth_importer.import_from_collection(tr_collection, bl_armature_obj)

            if self.properties.merge_with_existing_armatures and bl_armature_obj is not None:
                self.merge()

            return { "FINISHED" }

    def merge(self) -> None:
        bl_armature_objs = Enumerable(bpy.context.scene.objects).where(lambda o: isinstance(o.data, bpy.types.Armature)).to_list()
        bl_global_armature_obj = Enumerable(bl_armature_objs).first_or_none(lambda o: BlenderNaming.is_global_armature_name(o.name))
        if bl_global_armature_obj is None and len(bl_armature_objs) == 1:
            return

        merger = ModelMerger()
        for bl_armature_obj in bl_armature_objs:
            if bl_armature_obj == bl_global_armature_obj:
                continue
                
            if Enumerable(bl_armature_obj.children).any(lambda o: not o.data and BlenderNaming.is_local_empty_name(o.name)):
                continue
            
            bl_global_armature_obj = merger.add(bl_global_armature_obj, bl_armature_obj)
