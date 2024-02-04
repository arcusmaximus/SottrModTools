import re
from typing import ClassVar, Iterable, NamedTuple
from io_scene_sottr.tr.Cloth import CollisionKey, CollisionType
from io_scene_sottr.util.Conditional import coalesce
from io_scene_sottr.util.Enumerable import Enumerable

class BlenderModelIdSet(NamedTuple):
    model_id: int
    model_data_id: int

class BlenderMeshIdSet(NamedTuple):
    model_id: int
    model_data_id: int
    mesh_idx: int

class BlenderBoneIdSet(NamedTuple):
    skeleton_id: int | None
    global_id: int | None
    local_id: int | None

class BlenderBlendShapeIdSet(NamedTuple):
    global_id: int | None
    local_id: int

class BlenderClothStripIdSet(NamedTuple):
    skeleton_id: int
    definition_id: int
    component_id: int
    strip_id: int

class BlenderNaming:
    local_collection_name: ClassVar[str] = "Split meshes for export"
    
    hidden_bone_group_name: ClassVar[str] = "Non-deforming bones"

    pinned_cloth_bone_group_name: ClassVar[str] = "Pinned cloth bones"
    pinned_cloth_bone_palette_name: ClassVar[str] = "THEME01"

    @staticmethod
    def make_mesh_name(collection_name: str, model_id: int, model_data_id: int, mesh_idx: int) -> str:
        return BlenderNaming.make_collection_item_name(collection_name, f"model_{model_id}_{model_data_id}_{mesh_idx}")
    
    @staticmethod
    def make_local_mesh_name(model_id: int, model_data_id: int, mesh_idx: int) -> str:
        return BlenderNaming.make_mesh_name("split", model_id, model_data_id, mesh_idx)
    
    @staticmethod
    def try_parse_mesh_name(name: str) -> BlenderMeshIdSet | None:
        match = re.fullmatch(r"\w+_model_(\d+)_(\d+)_(\d+)(?:\.\d+)?", name)
        if match is None:
            return None
    
        return BlenderMeshIdSet(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    
    @staticmethod
    def parse_mesh_name(name: str) -> BlenderMeshIdSet:
        mesh_id_set = BlenderNaming.try_parse_mesh_name(name)
        if mesh_id_set is None:
            raise Exception(f"{name} is not a valid mesh name.")

        return mesh_id_set
    
    @staticmethod
    def parse_model_name(name: str) -> BlenderModelIdSet:
        mesh_id_set = BlenderNaming.parse_mesh_name(name)
        return BlenderModelIdSet(mesh_id_set.model_id, mesh_id_set.model_data_id)
    
    @staticmethod
    def make_local_empty_name(model_id: int, model_data_id: int) -> str:
        return f"split_{model_id}_{model_data_id}"
    
    @staticmethod
    def is_local_empty_name(name: str) -> bool:
        return name.startswith("split_")
    
    @staticmethod
    def parse_local_empty_name(name: str) -> BlenderModelIdSet:
        match = re.fullmatch(r"split_(\d+)_(\d+)(?:\.\d+)?", name)
        if match is None:
            raise Exception(f"{name} is not a valid local empty name")
        
        return BlenderModelIdSet(int(match.group(1)), int(match.group(2)))
    
    @staticmethod
    def make_color_map_name(idx: int) -> str:
        return f"color{1 + idx}"
    
    @staticmethod
    def parse_color_map_name(name: str) -> int:
        match = re.fullmatch(r"color(\d+)", name)
        if match is None:
            raise Exception(f"{name} is not a valid color attribute name.")
        
        return int(match.group(1)) - 1
    
    @staticmethod
    def make_uv_map_name(idx: int) -> str:
        return f"texcoord{1 + idx}"
    
    @staticmethod
    def parse_uv_map_name(name: str) -> int:
        match = re.fullmatch(r"texcoord(\d+)", name)
        if match is None:
            raise Exception(f"{name} is not a valid UV map name.")
        
        return int(match.group(1)) - 1
    
    @staticmethod
    def make_global_armature_name(local_skeleton_ids: Iterable[int]) -> str:
        return "merged_skeleton_" + "_".join(
            Enumerable(local_skeleton_ids).order_by(lambda id: id)      \
                                          .select(lambda id: str(id))
        )
    
    @staticmethod
    def is_global_armature_name(name: str) -> bool:
        return name.startswith("merged_skeleton_")
    
    @staticmethod
    def parse_global_armature_name(name: str) -> list[int]:
        match = re.fullmatch(r"merged_skeleton_([_\d]+)(?:\.\d+)?", name)
        if match is None:
            raise Exception(f"{name} is not a valid merged armature name.")
        
        return Enumerable(match.group(1).split("_")).select(lambda id: int(id)).to_list()
    
    @staticmethod
    def make_local_armature_name(collection_name: str, id: int) -> str:
        return BlenderNaming.make_collection_item_name(collection_name, f"skeleton_{id}")
    
    @staticmethod
    def try_parse_local_armature_name(name: str) -> int | None:
        match = re.fullmatch(r"\w+_skeleton_(\d+)(?:\.\d+)?", name)
        if match is None:
            return None
        
        return int(match.group(1))
    
    @staticmethod
    def parse_local_armature_name(name: str) -> int:
        local_skeleton_id = BlenderNaming.try_parse_local_armature_name(name)
        if local_skeleton_id is None:
            raise Exception(f"{name} is not a valid armature name.")
        
        return local_skeleton_id
    
    @staticmethod
    def make_bone_name(skeleton_id: int | None, global_id: int | None, local_id: int | None) -> str:
        if skeleton_id is not None:
            if local_id is None:
                raise Exception("Must provide local bone ID when providing skeleton ID")
            
            return f"bone_{skeleton_id}_{coalesce(global_id, 'x')}_{local_id}"
        elif local_id is not None:
            return f"bone_{coalesce(global_id, 'x')}_{local_id}"
        elif global_id is not None:
            return f"bone_{global_id}"
        else:
            raise Exception("Must provide at least one ID for bone name")
    
    @staticmethod
    def try_parse_bone_name(name: str) -> BlenderBoneIdSet | None:
        match = re.fullmatch(r"bone_(x|\d+)(?:_(x|\d+))?(?:_(\d+))?", name)
        if match is None:
            return None
        
        if match.group(3) is not None:
            return BlenderBoneIdSet(
                int(match.group(1)),
                int(match.group(2)) if match.group(2) != "x" else None,
                int(match.group(3))
            )
        elif match.group(2) is not None:
            return BlenderBoneIdSet(
                None,
                int(match.group(1)) if match.group(1) != "x" else None,
                int(match.group(2))
            )
        else:
            return BlenderBoneIdSet(
                None,
                int(match.group(1)),
                None
            )
    
    @staticmethod
    def parse_bone_name(name: str) -> BlenderBoneIdSet:
        bone_id_set = BlenderNaming.try_parse_bone_name(name)
        if bone_id_set is None:
            raise Exception(f"{name} is not a valid bone name.")

        return bone_id_set
    
    @staticmethod
    def get_bone_local_id(name: str) -> int:
        bone_id_set = BlenderNaming.parse_bone_name(name)
        if bone_id_set.local_id is None:
            raise Exception(f"{name} is not a local bone.")
        
        return bone_id_set.local_id
    
    @staticmethod
    def make_shape_key_name(global_id: int | None, local_id: int) -> str:
        return f"shapekey_{coalesce(global_id, 'x')}_{local_id}"
    
    @staticmethod
    def parse_shape_key_name(name: str) -> BlenderBlendShapeIdSet:
        match = re.fullmatch(r"shapekey_(x|\d+)_(\d+)", name)
        if match is not None:
            return BlenderBlendShapeIdSet(
                int(match.group(1)) if match.group(1) != "x" else None,
                int(match.group(2))
            )
        
        match = re.fullmatch(r"shapekey_(\d+)", name)
        if match is not None:
            return BlenderBlendShapeIdSet(None, int(match.group(1)))

        raise Exception(f"{name} is not a valid shape key name.")

    @staticmethod
    def make_material_name(id: int) -> str:
        return f"material_{id}"

    @staticmethod
    def parse_material_name(name: str) -> int:
        match = re.fullmatch(r"material_(\d+)(?:\.\d+)?", name)
        if match is None:
            raise Exception(f"{name} is not a valid material name.")

        return int(match.group(1))

    @staticmethod
    def make_action_name(id: int, model_data_id: int | None, mesh_idx: int | None) -> str:
        name = f"animation_{id}"
        if model_data_id is not None and mesh_idx is not None:
            name += f"_{model_data_id}_{mesh_idx}"
        
        return name
    
    @staticmethod
    def try_parse_action_name(name: str) -> int | None:
        match = re.fullmatch(r"animation_(\d+)(?:_\d+)?(?:\.\d+)?", name)
        if match is None:
            return None
        
        return int(match.group(1))
    
    @staticmethod
    def make_cloth_empty_name(collection_name: str) -> str:
        return BlenderNaming.make_collection_item_name(collection_name, f"cloth")
    
    @staticmethod
    def is_cloth_empty_name(name: str) -> bool:
        return name.endswith("_cloth")
    
    @staticmethod
    def make_cloth_strip_name(collection_name: str, skeleton_id: int, definition_id: int, component_id: int, strip_id: int) -> str:
        return BlenderNaming.make_collection_item_name(collection_name, f"clothstrip_{skeleton_id}_{definition_id}_{component_id}_{strip_id}")
    
    @staticmethod
    def try_parse_cloth_strip_name(name: str) -> BlenderClothStripIdSet | None:
        match = re.fullmatch(r"\w+_clothstrip_(\d+)_(\d+)_(\d+)_(\d+)", name)
        if match is None:
            return None
        
        return BlenderClothStripIdSet(int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)))
    
    @staticmethod
    def parse_cloth_strip_name(name: str) -> BlenderClothStripIdSet:
        id_set = BlenderNaming.try_parse_cloth_strip_name(name)
        if id_set is None:
            raise Exception(f"{name} is not a valid cloth strip name")
        
        return id_set
    
    @staticmethod
    def make_collision_empty_name(collection_name: str) -> str:
        return BlenderNaming.make_collection_item_name(collection_name, "collisions")
    
    @staticmethod
    def is_collision_empty_name(name: str) -> bool:
        return name.endswith("_collisions")
    
    @staticmethod
    def make_collision_name(collection_name: str, collision_type: CollisionType, collision_hash: int) -> str:
        return BlenderNaming.make_collection_item_name(collection_name, f"collision_{collision_type.name.lower()}_{collision_hash:016X}")
    
    @staticmethod
    def parse_collision_name(name: str) -> CollisionKey:
        match = re.fullmatch(r"\w+_collision_([a-z]+)_([0-9A-F]+)", name)
        if match is None:
            raise Exception(f"{name} is not a valid collision name")
        
        return CollisionKey(CollisionType[match.group(1).upper()], int(match.group(2), base = 16))

    @staticmethod
    def make_collection_item_name(collection_name: str, suffix: str) -> str:
        result = f"{collection_name}_{suffix}"
        if len(result) > 59:
            result = result[-59:]
        
        return result
