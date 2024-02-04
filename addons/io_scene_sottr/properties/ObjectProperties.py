from typing import Annotated
import bpy
from io_scene_sottr.properties.BlenderPropertyGroup import BlenderAttachedPropertyGroup, BlenderPropertyGroup, Prop, PropSubType
from io_scene_sottr.util.Enumerable import Enumerable

def search_bones(self: BlenderPropertyGroup, context: bpy.types.Context, edit_text: str) -> list[str]:
    bl_armature_obj = context.object
    while True:
        if not bl_armature_obj:
            return [""]
        
        if isinstance(bl_armature_obj.data, bpy.types.Armature):
            break

        bl_armature_obj = bl_armature_obj.parent
    
    return Enumerable(bl_armature_obj.data.bones).select(lambda b: b.name) \
                                                 .order_by(lambda b: b) \
                                                 .where(lambda b: b.startswith(edit_text)) \
                                                 .to_list()

class ObjectClothProperties(BlenderPropertyGroup):
    parent_bone_name: Annotated[str, Prop("Parent", search = search_bones)]
    gravity_factor: Annotated[float, Prop("Gravity factor", min = -2, max = 2, default = 1)]
    wind_factor: Annotated[float, Prop("Wind factor", min = 0, max = 1, subtype = PropSubType.FACTOR)]
    stiffness: Annotated[float, Prop("Stiffness", min = 0, max = 1, subtype = PropSubType.FACTOR)]
    dampening: Annotated[float, Prop("Dampening", min = 0, max = 1, default = 0.2, subtype = PropSubType.FACTOR)]

class ObjectProperties(BlenderAttachedPropertyGroup[bpy.types.Object]):
    property_name = "tr11_properties"

    cloth: Annotated[ObjectClothProperties, Prop("Cloth properties")]
