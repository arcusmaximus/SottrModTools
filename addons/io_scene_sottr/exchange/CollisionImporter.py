from typing import Any, Iterable, cast
import bpy
import bmesh
from mathutils import Matrix, Vector
from io_scene_sottr.BlenderHelper import BlenderHelper
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.tr.Collection import Collection
from io_scene_sottr.tr.Collision import Collision, CollisionBox, CollisionCapsule, CollisionDoubleRadiiCapsule, CollisionSphere
from io_scene_sottr.util.Enumerable import Enumerable
from io_scene_sottr.util.SlotsBase import SlotsBase

class CollisionImporter(SlotsBase):
    scale_factor: float

    def __init__(self, scale_factor: float) -> None:
        self.scale_factor = scale_factor

    def import_from_collection(self, tr_collection: Collection, bl_armature_obj: bpy.types.Object) -> list[bpy.types.Object]:
        bl_collision_empty = BlenderHelper.create_object(None, BlenderNaming.make_collision_empty_name(tr_collection.name))
        bl_collision_empty.parent = bl_armature_obj
        
        bl_collision_objs: list[bpy.types.Object] = []
        for tr_collision in tr_collection.get_collisions():
            bl_collision_obj = self.import_collision(tr_collection, tr_collision, bl_armature_obj)
            if bl_collision_obj is None:
                continue

            bl_collision_obj.parent = bl_collision_empty
            bl_collision_objs.append(bl_collision_obj)
        
        return bl_collision_objs
    
    def import_collision(self, tr_collection: Collection, tr_collision: Collision, bl_armature_obj: bpy.types.Object | None) -> bpy.types.Object | None:
        collision_name = BlenderNaming.make_collision_name(tr_collection.name, tr_collision.type, tr_collision.hash)
        
        if isinstance(tr_collision, CollisionBox):
            bpy.ops.mesh.primitive_cube_add(size = 1, calc_uvs = False)
            bl_cube_obj = bpy.context.object
            bl_cube_obj.scale = Vector((tr_collision.width, tr_collision.depth, tr_collision.height)) * self.scale_factor
            bpy.ops.object.transform_apply()
        elif isinstance(tr_collision, CollisionSphere):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions = 3, radius = tr_collision.radius * self.scale_factor)
            bpy.ops.object.shade_smooth()
        elif isinstance(tr_collision, CollisionCapsule) or isinstance(tr_collision, CollisionDoubleRadiiCapsule):
            radius1 = tr_collision.radius_1 if isinstance(tr_collision, CollisionDoubleRadiiCapsule) else tr_collision.radius
            radius2 = tr_collision.radius_2 if isinstance(tr_collision, CollisionDoubleRadiiCapsule) else tr_collision.radius
            if radius1 > 100 or radius2 > 100:
                return None

            bm_mesh = bmesh.new()

            result: dict[str, Any] = bmesh.ops.create_uvsphere(
                bm_mesh,
                u_segments = 16,
                v_segments = 8,
                radius = radius1 * self.scale_factor,
                matrix = Matrix.Translation((0, 0, -tr_collision.length * self.scale_factor / 2))
            )
            bmesh.ops.delete(
                bm_mesh,
                geom = Enumerable[bmesh.types.BMVert](result["verts"]).where(lambda v: cast(Vector, v.co).z > -tr_collision.length * self.scale_factor / 2 + 0.0001)
                                                                      .to_list()
            )

            result = bmesh.ops.create_uvsphere(
                bm_mesh,
                u_segments = 16,
                v_segments = 8,
                radius = radius2 * self.scale_factor,
                matrix = Matrix.Translation((0, 0, tr_collision.length * self.scale_factor / 2))
            )
            bmesh.ops.delete(
                bm_mesh,
                geom = Enumerable[bmesh.types.BMVert](result["verts"]).where(lambda v: cast(Vector, v.co).z < tr_collision.length * self.scale_factor / 2 - 0.0001)
                                                                      .to_list()
            )

            bmesh.ops.create_cone(
                bm_mesh,
                segments = 16,
                radius1 = radius1 * self.scale_factor,
                radius2 = radius2 * self.scale_factor,
                depth = tr_collision.length * self.scale_factor
            )

            bmesh.ops.remove_doubles(bm_mesh, dist = 0.0001, verts = list(cast(Iterable[bmesh.types.BMVert], bm_mesh.verts)))

            bl_mesh = bpy.data.meshes.new(collision_name)
            bm_mesh.to_mesh(bl_mesh)
            bm_mesh.free()

            BlenderHelper.create_object(bl_mesh)
            bpy.ops.object.shade_smooth()
        else:
            return None

        bl_obj = bpy.context.object
        bl_obj.name = collision_name
        bl_obj.data.name = bl_obj.name
        bl_obj.hide_set(True)
        BlenderHelper.move_object_to_collection(bl_obj, bpy.context.scene.collection)

        if bl_armature_obj is not None:
            bl_bone = Enumerable(cast(bpy.types.Armature, bl_armature_obj.data).bones).first_or_none(
                lambda b: BlenderNaming.parse_bone_name(b.name).global_id == tr_collision.global_bone_id)
            
            if bl_bone is not None:
                bl_vertex_group = bl_obj.vertex_groups.new(name = bl_bone.name)
                bl_vertex_group.add(range(len(cast(bpy.types.Mesh, bl_obj.data).vertices)), 1.0, "REPLACE")

                transform = Matrix(tr_collision.transform)
                transform.translation = transform.translation * self.scale_factor
                bl_obj.matrix_local = transform

                bl_obj.parent = bl_armature_obj
                bl_modifier = cast(bpy.types.ArmatureModifier, bl_obj.modifiers.new("Armature", "ARMATURE"))
                bl_modifier.object = bl_armature_obj

        return bl_obj
