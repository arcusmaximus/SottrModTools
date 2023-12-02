bl_info = {
    "name": "SOTTR mesh support",
    "description": "Import/export files in the Shadow of the Tomb Raider format",
    "author": "arc_",
    "blender": (2, 80, 0),
    "version": (0, 1, 5),
    "location": "File > Import-Export",
    "support": "COMMUNITY",
    "category": "Import-Export"
}

from typing import Callable, Protocol
import bpy
from bpy.types import Context, Menu
from io_scene_sottr.tr.CStructTypeMappings import CStructTypeMappings
CStructTypeMappings.register()

from io_scene_sottr.operator.ImportObjectOperator import ImportObjectOperator
from io_scene_sottr.operator.ExportModelOperator import ExportModelOperator

class SottrOperator(Protocol):
    bl_idname: str
    bl_menu: Menu
    bl_menu_item_name: str

operators: list[SottrOperator] = [
    ImportObjectOperator,
    ExportModelOperator
]

menu_item_funcs: dict[SottrOperator, Callable[[Menu, Context], None]] = {}

def make_menu_item_func(operator: SottrOperator) -> Callable[[Menu, Context], None]:
    def draw_menu_item(menu: Menu, context: Context) -> None:
        menu.layout.operator(operator.bl_idname, text = operator.bl_menu_item_name)
    
    return draw_menu_item

def register() -> None:
    for operator in operators:
        bpy.utils.register_class(operator)
        
        draw_menu_item = make_menu_item_func(operator)
        operator.bl_menu.append(draw_menu_item)                     # type: ignore
        menu_item_funcs[operator] = draw_menu_item

def unregister() -> None:
    for operator in operators:
        bpy.utils.unregister_class(operator)                        # type: ignore

        operator.bl_menu.remove(menu_item_funcs[operator])          # type: ignore
        del menu_item_funcs[operator]
