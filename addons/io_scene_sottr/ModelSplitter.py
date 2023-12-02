from typing import ClassVar, Iterable, NamedTuple, cast
import bpy
from io_scene_sottr.BlenderHelper import BlenderHelper
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.util.DictionaryExtensions import DictionaryExtensions
from io_scene_sottr.util.Enumerable import Enumerable
from io_scene_sottr.util.SlotsBase import SlotsBase

class _LocalArmature(NamedTuple):
    name: str
    bone_names_by_global_id: dict[int, str]
    model_id: int
    model_data_id: int

class ModelSplitter(SlotsBase):
    local_skeleton_vertex_group_prefix: ClassVar[str] = "__local_skeleton_"
    local_mesh_counter: int

    def __init__(self) -> None:
        self.local_mesh_counter = 0

    def split(self, bl_global_armature_obj: bpy.types.Object) -> list[bpy.types.Object]:
        if bpy.context.object:
            bpy.ops.object.mode_set(mode = "OBJECT")            # type: ignore

        local_armatures = self.get_local_armatures(bl_global_armature_obj)
        local_skeleton_ids_by_global_bone_id = self.get_local_skeleton_ids_by_global_bone_id(local_armatures)

        self.delete_local_meshes(local_armatures)

        for bl_global_mesh_obj in Enumerable(cast(Iterable[bpy.types.Object], bl_global_armature_obj.children)).where(lambda o: isinstance(o.data, bpy.types.Mesh)):
            self.split_mesh(bl_global_mesh_obj, local_armatures, local_skeleton_ids_by_global_bone_id)
        
        return Enumerable(local_armatures.values()).select(lambda a: bpy.data.objects[a.name]).to_list()
    
    def get_local_armatures(self, bl_global_armature_obj: bpy.types.Object) -> dict[int, _LocalArmature]:
        local_skeleton_ids = BlenderNaming.parse_global_armature_name(bl_global_armature_obj.data.name)
        local_armatures: dict[int, _LocalArmature] = {}
        
        for bl_armature_obj in Enumerable(bpy.context.scene.objects).where(lambda o: isinstance(o.data, bpy.types.Armature)):
            local_skeleton_id = BlenderNaming.try_parse_local_armature_name(bl_armature_obj.data.name)
            if local_skeleton_id is None or local_skeleton_id not in local_skeleton_ids:
                continue

            bone_names_by_global_id: dict[int, str] = {}
            for bl_bone in cast(bpy.types.Armature, bl_armature_obj.data).bones:
                global_bone_id = BlenderNaming.parse_local_bone_name(bl_bone.name).global_id
                if global_bone_id is not None:
                    bone_names_by_global_id[global_bone_id] = bl_bone.name
            
            bl_empty_obj = Enumerable(cast(Iterable[bpy.types.Object], bl_armature_obj.children))       \
                                .first_or_none(lambda o: cast(bpy.types.ID | None, o.data) is None and BlenderNaming.is_local_empty_name(o.name))
            if bl_empty_obj is None:
                raise Exception(f"Empty object specifying model ID is missing for armature {bl_armature_obj.name}")
            
            model_id_set = BlenderNaming.parse_local_empty_name(bl_empty_obj.name)
            local_armatures[local_skeleton_id] = _LocalArmature(bl_armature_obj.data.name, bone_names_by_global_id, model_id_set.model_id, model_id_set.model_data_id)
        
        if len(local_armatures) != len(local_skeleton_ids):
            raise Exception("Can't split merged mesh - one or more local armatures are missing.")
        
        return local_armatures
    
    def get_local_skeleton_ids_by_global_bone_id(self, local_armatures: dict[int, _LocalArmature]) -> dict[int, list[int]]:
        local_skeleton_ids_by_global_bone_id: dict[int, list[int]] = {}

        for local_skeleton_id, local_armature in local_armatures.items():
            bl_local_armature_obj = bpy.data.objects[local_armature.name]
            bl_local_armature = cast(bpy.types.Armature, bl_local_armature_obj.data)
            for bl_bone in bl_local_armature.bones:
                global_bone_id = BlenderNaming.parse_local_bone_name(bl_bone.name).global_id
                if global_bone_id is None:
                    continue

                DictionaryExtensions.get_or_add(local_skeleton_ids_by_global_bone_id, global_bone_id, lambda: [])   \
                                    .append(local_skeleton_id)
        
        return local_skeleton_ids_by_global_bone_id

    def delete_local_meshes(self, local_armatures: dict[int, _LocalArmature]) -> None:
        local_armature_names = Enumerable(local_armatures.values()).select(lambda a: a.name).to_list()
        local_mesh_names = Enumerable(bpy.context.scene.objects)        \
                                .where(lambda o: o.parent and o.parent.data and o.parent.data.name in local_armature_names and isinstance(o.data, bpy.types.Mesh))  \
                                .select(lambda o: o.name)               \
                                .to_list()
        for local_mesh_name in local_mesh_names:
            bl_local_mesh_obj = bpy.data.objects[local_mesh_name]
            bpy.data.meshes.remove(cast(bpy.types.Mesh, bl_local_mesh_obj.data), do_unlink = True)
    
    def split_mesh(self, bl_global_mesh_obj: bpy.types.Object, local_armatures: dict[int, _LocalArmature], local_skeleton_ids_by_global_bone_id: dict[int, list[int]]) -> None:
        bl_splittable_global_mesh_obj = self.make_splittable_global_mesh(bl_global_mesh_obj, local_armatures, local_skeleton_ids_by_global_bone_id)

        for vertex_group_name in list(bl_splittable_global_mesh_obj.vertex_groups.keys()):
            local_skeleton_id = self.try_parse_local_skeleton_vertex_group_name(vertex_group_name)
            if local_skeleton_id is None:
                continue

            bl_splittable_global_mesh_obj, bl_split_global_mesh_obj = self.separate_faces_by_vertex_group(bl_splittable_global_mesh_obj, vertex_group_name)
            if bl_split_global_mesh_obj is None:
                continue

            local_armature = local_armatures[local_skeleton_id]
            self.convert_global_mesh_to_local(bl_split_global_mesh_obj, local_armature)
            bl_split_global_mesh_obj.name = BlenderNaming.make_local_mesh_name(local_armature.model_id, local_armature.model_data_id, self.local_mesh_counter)
            bl_split_global_mesh_obj.data.name = bl_split_global_mesh_obj.name
            self.local_mesh_counter += 1
            
            bl_local_armature_obj = bpy.data.objects[local_armature.name]
            bl_split_global_mesh_obj.parent = bl_local_armature_obj
            bl_armature_modifier = Enumerable(bl_split_global_mesh_obj.modifiers).of_type(bpy.types.ArmatureModifier).first_or_none()
            if bl_armature_modifier is not None:
                bl_armature_modifier.object = bl_local_armature_obj
            
            bl_local_collection = Enumerable(cast(Iterable[bpy.types.Collection], bl_local_armature_obj.users_collection)).first_or_none()
            if bl_local_collection is not None:
                BlenderHelper.move_object_to_collection(bl_split_global_mesh_obj, bl_local_collection)
        
        bpy.data.meshes.remove(cast(bpy.types.Mesh, bl_splittable_global_mesh_obj.data), do_unlink = True)

    def make_splittable_global_mesh(self, bl_global_mesh_obj: bpy.types.Object, local_armatures: dict[int, _LocalArmature], local_skeleton_ids_by_global_bone_id: dict[int, list[int]]) -> bpy.types.Object:
        bl_global_mesh = cast(bpy.types.Mesh, bl_global_mesh_obj.data)

        local_skeleton_ids_by_vertex_group_idx: list[list[int]] = []
        for bl_global_bone_vertex_group in bl_global_mesh_obj.vertex_groups:
            global_bone_id = BlenderNaming.parse_global_bone_name(bl_global_bone_vertex_group.name)
            local_skeleton_ids = local_skeleton_ids_by_global_bone_id.get(global_bone_id)
            if local_skeleton_ids is None:
                raise Exception(f"Vertex group {bl_global_bone_vertex_group.name} in mesh {bl_global_mesh_obj.name} has no corresponding bone.")
            
            local_skeleton_ids_by_vertex_group_idx.append(local_skeleton_ids)
        
        global_vertex_indices_by_local_skeleton_id: dict[int, list[int]] = Enumerable(local_armatures.keys()).to_dict(lambda id: id, lambda _: [])
        for bl_vertex in bl_global_mesh.vertices:
            local_skeleton_ids: list[int] | None = []
            for bl_vertex_weight in bl_vertex.groups:
                for local_skeleton_id in local_skeleton_ids_by_vertex_group_idx[bl_vertex_weight.group]:
                    if local_skeleton_id not in local_skeleton_ids:
                        local_skeleton_ids.append(local_skeleton_id)

            for local_skeleton_id in local_skeleton_ids:
                global_vertex_indices_by_local_skeleton_id[local_skeleton_id].append(bl_vertex.index)
        
        bl_splittable_global_mesh_obj = BlenderHelper.duplicate_object(bl_global_mesh_obj)
        if not cast(bpy.types.Mesh, bl_splittable_global_mesh_obj.data).has_custom_normals:
            bpy.ops.mesh.customdata_custom_splitnormals_add()       # type: ignore

        for local_skeleton_id, global_vertex_indices in Enumerable(global_vertex_indices_by_local_skeleton_id.items()).order_by_descending(lambda g: len(g[1])):
            if len(global_vertex_indices) == 0:
                break

            bl_local_skeleton_vertex_group = bl_splittable_global_mesh_obj.vertex_groups.new(name = self.make_local_skeleton_vertex_group_name(local_skeleton_id))
            bl_local_skeleton_vertex_group.add(global_vertex_indices, 1.0, "REPLACE")
        
        return bl_splittable_global_mesh_obj
    
    def separate_faces_by_vertex_group(self, bl_mesh_obj: bpy.types.Object, vertex_group_name: str) -> tuple[bpy.types.Object, bpy.types.Object | None]:
        mesh_obj_name = bl_mesh_obj.name

        with BlenderHelper.enter_edit_mode(bl_mesh_obj):
            bl_mesh_obj.vertex_groups.active = bl_mesh_obj.vertex_groups[vertex_group_name]

            bpy.ops.mesh.select_mode(type = "VERT")             # type: ignore
            bpy.ops.mesh.select_all(action = "DESELECT")        # type: ignore
            bpy.ops.object.vertex_group_select()                # type: ignore
            bpy.ops.mesh.select_mode(type = "FACE")             # type: ignore
            try:
                bpy.ops.mesh.separate()                         # type: ignore
            except:
                return (bl_mesh_obj, None)
        
        bl_orig_obj = bpy.data.objects[mesh_obj_name]
        bl_separated_obj = Enumerable(bpy.context.selected_objects).first_or_none(lambda o: o != bl_orig_obj)
        return (bl_orig_obj, bl_separated_obj)
    
    def convert_global_mesh_to_local(self, bl_global_mesh_obj: bpy.types.Object, local_armature: _LocalArmature) -> None:
        i = 0
        while i < len(bl_global_mesh_obj.vertex_groups):
            bl_vertex_group = bl_global_mesh_obj.vertex_groups[i]
            if bl_vertex_group.name.startswith(ModelSplitter.local_skeleton_vertex_group_prefix):
                bl_global_mesh_obj.vertex_groups.remove(bl_vertex_group)
            else:
                global_bone_id = BlenderNaming.parse_global_bone_name(bl_vertex_group.name)
                local_bone_name = local_armature.bone_names_by_global_id.get(global_bone_id)
                if local_bone_name is None:
                    bl_global_mesh_obj.vertex_groups.remove(bl_vertex_group)
                else:
                    bl_vertex_group.name = local_bone_name
                    i += 1
    
    def make_local_skeleton_vertex_group_name(self, local_skeleton_id: int):
        return ModelSplitter.local_skeleton_vertex_group_prefix + str(local_skeleton_id)

    def try_parse_local_skeleton_vertex_group_name(self, name: str) -> int | None:
        if not name.startswith(ModelSplitter.local_skeleton_vertex_group_prefix):
            return None

        return int(name[len(ModelSplitter.local_skeleton_vertex_group_prefix):])
