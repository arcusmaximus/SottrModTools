from types import TracebackType
from typing import Iterable, cast
import bpy
from io_scene_sottr.util.Enumerable import Enumerable
from io_scene_sottr.util.SlotsBase import SlotsBase

class BlenderHelper:
    @staticmethod
    def enter_edit_mode(bl_obj: bpy.types.Object | None = None) -> "BlenderEditContext":
        if bl_obj is not None:
            bpy.ops.object.select_all(action = "DESELECT")          # type: ignore
            bl_obj.select_set(True)
            bpy.context.view_layer.objects.active = bl_obj
        
        return BlenderEditContext()

    @staticmethod
    def prepare_for_export(bl_obj: bpy.types.Object) -> "BlenderExportContext":
        return BlenderExportContext(bl_obj)

    @staticmethod
    def create_object(bl_data: bpy.types.ID | None, name: str | None = None) -> bpy.types.Object:
        bl_obj = bpy.data.objects.new(name or (bl_data and bl_data.name) or "", bl_data)
        BlenderHelper.__add_object_to_scene(bl_obj)
        return bl_obj

    @staticmethod
    def duplicate_object(bl_obj: bpy.types.Object) -> bpy.types.Object:
        bl_copied_obj = cast(bpy.types.Object, bl_obj.copy())
        if bl_obj.data:
            bl_copied_obj.data = bl_obj.data.copy()
        
        BlenderHelper.__add_object_to_scene(bl_copied_obj)
        return bl_copied_obj
    
    @staticmethod
    def __add_object_to_scene(bl_obj: bpy.types.Object) -> None:
        bpy.context.scene.collection.objects.link(bl_obj)
        
        bpy.ops.object.select_all(action = "DESELECT")              # type: ignore
        bl_obj.select_set(True)
        bpy.context.view_layer.objects.active = bl_obj
    
    @staticmethod
    def join_objects(bl_target_obj: bpy.types.Object, bl_source_objs: Iterable[bpy.types.Object]) -> None:
        bpy.ops.object.select_all(action = "DESELECT")              # type: ignore
        for bl_source_obj in bl_source_objs:
            bl_source_obj.select_set(True)
        
        bl_target_obj.select_set(True)
        bpy.context.view_layer.objects.active = bl_target_obj
        bpy.ops.object.join()                                       # type: ignore
    
    @staticmethod
    def move_object_to_collection(bl_obj: bpy.types.Object, bl_collection: bpy.types.Collection) -> None:
        for bl_existing_collection in list(cast(Iterable[bpy.types.Collection], bl_obj.users_collection)):
            bl_existing_collection.objects.unlink(bl_obj)
        
        bl_collection.objects.link(bl_obj)

class BlenderEditContext(SlotsBase):
    def __init__(self) -> None:
        bpy.ops.object.mode_set(mode = "EDIT")              # type: ignore
    
    def __enter__(self) -> None:
        pass

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        bpy.ops.object.mode_set(mode = "OBJECT")            # type: ignore

class BlenderExportContext(SlotsBase):
    bl_obj: bpy.types.Object
    modifiers_enabled: list[bool]
    shape_key_values: list[float]
    active_shape_key_idx: int
    only_active_shape_key: bool
    use_auto_smooth: bool

    def __init__(self, bl_obj: bpy.types.Object) -> None:
        self.bl_obj = bl_obj

        self.modifiers_enabled = Enumerable(bl_obj.modifiers).select(lambda m: m.show_viewport).to_list()
        for bl_modifier in bl_obj.modifiers:
            if not isinstance(bl_modifier, bpy.types.TriangulateModifier):
                bl_modifier.show_viewport = False
        
        bl_mesh = cast(bpy.types.Mesh, bl_obj.data)
        if cast(bpy.types.Key | None, bl_mesh.shape_keys) is None:
            self.shape_key_values = []
        else:
            self.shape_key_values = Enumerable(bl_mesh.shape_keys.key_blocks).select(lambda s: s.value).to_list()
            for bl_shape_key in bl_mesh.shape_keys.key_blocks:
                bl_shape_key.value = 0

        self.active_shape_key_idx = bl_obj.active_shape_key_index
        self.only_active_shape_key = bl_obj.show_only_shape_key
        bl_obj.show_only_shape_key = False

        self.use_auto_smooth = bl_mesh.use_auto_smooth
        if bl_mesh.has_custom_normals:
            bl_mesh.use_auto_smooth = True
        
        bpy.ops.object.select_all(action = "DESELECT")              # type: ignore        
        bl_obj.select_set(True)
        bpy.context.view_layer.objects.active = bl_obj
    
    def __enter__(self) -> None:
        pass

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        for i, enabled in enumerate(self.modifiers_enabled):
            self.bl_obj.modifiers[i].show_viewport = enabled
        
        bl_mesh = cast(bpy.types.Mesh, self.bl_obj.data)
        if cast(bpy.types.Key | None, bl_mesh.shape_keys) is not None:
            for i, value in enumerate(self.shape_key_values):
                bl_mesh.shape_keys.key_blocks[i].value = value

        self.bl_obj.active_shape_key_index = self.active_shape_key_idx
        self.bl_obj.show_only_shape_key = self.only_active_shape_key
        bl_mesh.use_auto_smooth = self.use_auto_smooth
