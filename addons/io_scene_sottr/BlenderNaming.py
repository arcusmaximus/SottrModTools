import re
from typing import ClassVar, Iterable, NamedTuple

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

class BlenderNaming:
    local_collection_name: ClassVar[str] = "Split meshes for export"
    hidden_bone_collection_name: ClassVar[str] = "Non-deforming bones"

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
    def parse_bone_name(name: str) -> BlenderBoneIdSet:
        match = re.fullmatch(r"bone_(x|\d+)(?:_(x|\d+))?(?:_(\d+))?", name)
        if match is None:
            raise Exception(f"{name} is not a valid bone name.")
        
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
    def make_collection_item_name(collection_name: str, suffix: str) -> str:
        result = f"{collection_name}_{suffix}"
        if len(result) > 59:
            result = result[-59:]
        
        return result
