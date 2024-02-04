from typing import Annotated
import bpy
from io_scene_sottr.properties.BlenderPropertyGroup import BlenderAttachedPropertyGroup, BlenderPropertyGroup, Prop, PropSubType
from io_scene_sottr.util.Enumerable import Enumerable

def search_bones(self: BlenderPropertyGroup, context: bpy.types.Context, edit_text: str) -> list[str]:
    if not context or not context.armature:
        return [""]
    
    return Enumerable(context.armature.bones).select(lambda b: b.name) \
                                             .order_by(lambda b: b) \
                                             .where(lambda b: b.startswith(edit_text)) \
                                             .to_list()

class BoneClothProperties(BlenderPropertyGroup):
    bounceback_factor: Annotated[float, Prop("Bounceback strength", min = 0, max = 1, subtype = PropSubType.FACTOR)]

class BoneProperties(BlenderAttachedPropertyGroup[bpy.types.Bone]):
    property_name = "tr11_properties"

    counterpart_bone_name: Annotated[str, Prop("Counterpart", search = search_bones)]
    cloth: Annotated[BoneClothProperties, Prop("Cloth properties")]
