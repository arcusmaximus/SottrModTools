from typing import Annotated
import bpy
from io_scene_tr_reboot.properties.BlenderPropertyGroup import BlenderAttachedPropertyGroup, BlenderPropertyGroup, Prop, PropSubType
from io_scene_tr_reboot.util.Enumerable import Enumerable

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
    gravity_factor: Annotated[float, Prop("Gravity Factor", min = -2, max = 2, default = 1)]
    wind_factor: Annotated[float, Prop("Wind Factor", min = 0, max = 1, subtype = PropSubType.FACTOR)]
    stiffness: Annotated[float, Prop("Pose Follow Factor", min = 0, max = 1, subtype = PropSubType.FACTOR)]
    rigidity: Annotated[float, Prop("Rigidity", min = 0, max = 1, default = 0.6, subtype = PropSubType.FACTOR)]
    dampening: Annotated[float, Prop("Drag", min = 0, max = 1, default = 0.2, subtype = PropSubType.FACTOR)]

class ObjectCollisionProperties(BlenderPropertyGroup):
    data: Annotated[str, Prop("Data")]

class ObjectMeshProperties(BlenderPropertyGroup):
    draw_group_id: Annotated[int, Prop("Draw Group ID")]
    flags: Annotated[int, Prop("Flags")]

class ObjectSkeletonProperties(BlenderPropertyGroup):
    global_blend_shape_ids: Annotated[str, Prop("Local -> global blend shape ID mappings")]

class ObjectProperties(BlenderAttachedPropertyGroup[bpy.types.Object]):
    property_name = "tr11_properties"

    blend_shape_normals_source_file_path: Annotated[str, Prop("Shape Key Normals Source", description = ".trXmodeldata file to copy shape key normals from")]
    cloth: Annotated[ObjectClothProperties, Prop("Cloth properties")]
    collision: Annotated[ObjectCollisionProperties, Prop("Collision properties")]
    mesh: Annotated[ObjectMeshProperties, Prop("Mesh properties")]
    skeleton: Annotated[ObjectSkeletonProperties, Prop("Skeleton properties")]
