bl_info = {
    "name": "SOTTR mesh support",
    "description": "Import/export files for Shadow of the Tomb Raider",
    "author": "arc_",
    "blender": (3, 6, 5),
    "version": (1, 2, 3),
    "location": "File > Import-Export",
    "support": "COMMUNITY",
    "category": "Import-Export"
}

from typing import Callable, Protocol
import bpy

from io_scene_sottr.util.CStructTypeMappings import CStructTypeMappings
from io_scene_sottr.tr.Tr11CStructTypeMappings import Tr11CStructTypeMappings
CStructTypeMappings.register()
Tr11CStructTypeMappings.register()

from io_scene_sottr.operator.ImportAnimationOperator import ImportAnimationOperator
from io_scene_sottr.operator.ImportObjectOperator import ImportObjectOperator
from io_scene_sottr.operator.ExportAnimationOperator import ExportAnimationOperator
from io_scene_sottr.operator.ExportModelOperator import ExportModelOperator
from io_scene_sottr.operator.RegenerateClothBonesOperator import RegenerateClothBonesOperator
from io_scene_sottr.operator.PinClothBonesOperator import PinClothBonesOperator
from io_scene_sottr.operator.UnpinClothBonesOperator import UnpinClothBonesOperator
from io_scene_sottr.properties.BlenderPropertyGroup import BlenderPropertyGroup
from io_scene_sottr.properties.BoneProperties import BoneClothProperties, BoneConstraintProperties, BoneProperties
from io_scene_sottr.properties.ObjectProperties import ObjectClothProperties, ObjectProperties
from io_scene_sottr.properties.ToolSettingProperties import ToolSettingProperties
from io_scene_sottr.ui.ClothStripPanel import ClothStripPanel
from io_scene_sottr.ui.ClothSpringPanel import ClothSpringPanel
from io_scene_sottr.ui.ClothBonesPanel import ClothBonesPanel
from io_scene_sottr.ui.BonePanel import BonePanel

class SottrMenuOperator(Protocol):
    bl_idname: str
    bl_menu: bpy.types.Menu
    bl_menu_item_name: str

menu_operators: list[SottrMenuOperator] = [
    ImportAnimationOperator,
    ImportObjectOperator,
    ExportAnimationOperator,
    ExportModelOperator
]

other_classes: list[type] = [
    RegenerateClothBonesOperator,
    PinClothBonesOperator,
    UnpinClothBonesOperator,

    ClothBonesPanel,
    ClothStripPanel,
    ClothSpringPanel,

    BonePanel
]

custom_property_groups: list[type[BlenderPropertyGroup]] = [
    BoneConstraintProperties,
    BoneClothProperties,
    BoneProperties,
    ObjectClothProperties,
    ObjectProperties,
    ToolSettingProperties
]

menu_item_funcs: dict[SottrMenuOperator, Callable[[bpy.types.Menu, bpy.types.Context], None]] = {}

def make_menu_item_func(operator: SottrMenuOperator) -> Callable[[bpy.types.Menu, bpy.types.Context], None]:
    def draw_menu_item(menu: bpy.types.Menu, context: bpy.types.Context) -> None:
        menu.layout.operator(operator.bl_idname, text = operator.bl_menu_item_name)
    
    return draw_menu_item

def register() -> None:
    for operator in menu_operators:
        bpy.utils.register_class(operator)
        draw_menu_item = make_menu_item_func(operator)
        operator.bl_menu.append(draw_menu_item)
        menu_item_funcs[operator] = draw_menu_item
    
    for cls in other_classes:
        bpy.utils.register_class(cls)
    
    for cls in custom_property_groups:
        cls.register()

def unregister() -> None:
    for operator in menu_operators:
        bpy.utils.unregister_class(operator)
        operator.bl_menu.remove(menu_item_funcs[operator])
        del menu_item_funcs[operator]

    for cls in other_classes:
        bpy.utils.unregister_class(cls)

    for cls in custom_property_groups:
        cls.unregister()
