from typing import Iterable, cast
import bpy
from bpy.types import Context, Menu, Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import BoolProperty, StringProperty          # type: ignore
from io_scene_sottr.BlenderNaming import BlenderNaming

from io_scene_sottr.ModelImporter import ModelImporter
from io_scene_sottr.ModelMerger import ModelMerger
from io_scene_sottr.operator.OperatorCommon import OperatorCommon
from io_scene_sottr.util.Enumerable import Enumerable

class ImportObjectOperator(Operator, ImportHelper):         # type: ignore
    bl_idname = "import_scene.tr11objectref"
    
    bl_menu = cast(Menu, bpy.types.TOPBAR_MT_file_import)
    bl_menu_item_name = "SOTTR object (.tr11objectref)"

    filename_ext = ".tr11objectref"
    filter_glob: StringProperty(                                # type: ignore
        default = "*" + filename_ext,
        options = { "HIDDEN" }
    )
    import_unlinked_models: BoolProperty(                       # type: ignore
        name = "Import unlinked models"
    )
    merge_with_existing_armatures: BoolProperty(                # type: ignore
        name = "Merge with existing armature(s)",
        default = True
    )
    import_lods: BoolProperty(                                  # type: ignore
        name = "Import LODs"
    )
    split_into_parts: BoolProperty(                             # type: ignore
        name = "Split meshes into parts"
    )
    bl_label = "Import"

    def execute(self, context: Context) -> set[str]:
        importer = ModelImporter(
            OperatorCommon.scale_factor,
            getattr(self.properties, "import_unlinked_models"),
            getattr(self.properties, "import_lods"),
            getattr(self.properties, "split_into_parts")
        )
        import_result = importer.import_collection(getattr(self.properties, "filepath"))

        if getattr(self.properties, "merge_with_existing_armatures") and import_result.bl_armature_obj is not None:
            self.merge()

        return { "FINISHED" }

    def merge(self) -> None:
        bl_armature_objs = Enumerable(bpy.context.scene.objects).where(lambda o: isinstance(o.data, bpy.types.Armature)).to_list()
        bl_global_armature_obj = Enumerable(bl_armature_objs).first_or_none(lambda o: BlenderNaming.is_global_armature_name(o.data.name))
        if bl_global_armature_obj is None and len(bl_armature_objs) == 1:
            return

        merger = ModelMerger()
        for bl_armature_obj in bl_armature_objs:
            if bl_armature_obj == bl_global_armature_obj:
                continue
                
            if Enumerable(cast(Iterable[bpy.types.Object], bl_armature_obj.children)).any(lambda o: cast(bpy.types.ID | None, o.data) is None and BlenderNaming.is_local_empty_name(o.name)):
                continue
            
            bl_global_armature_obj = merger.add(bl_global_armature_obj, bl_armature_obj)
