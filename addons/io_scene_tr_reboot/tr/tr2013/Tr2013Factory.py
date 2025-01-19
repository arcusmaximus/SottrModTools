from typing import cast
from mathutils import Vector
from io_scene_tr_reboot.tr.Bone import IBone
from io_scene_tr_reboot.tr.BoneConstraint import IBoneConstraint
from io_scene_tr_reboot.tr.Cloth import Cloth
from io_scene_tr_reboot.tr.Collection import Collection
from io_scene_tr_reboot.tr.Collision import Collision, CollisionType
from io_scene_tr_reboot.tr.Enumerations import CdcGame
from io_scene_tr_reboot.tr.IFactory import IFactory
from io_scene_tr_reboot.tr.Mesh import IMesh
from io_scene_tr_reboot.tr.MeshPart import IMeshPart
from io_scene_tr_reboot.tr.Model import IModel
from io_scene_tr_reboot.tr.Skeleton import ISkeleton
from io_scene_tr_reboot.tr.tr2013.Tr2013Bone import Tr2013Bone
from io_scene_tr_reboot.tr.tr2013.Tr2013Cloth import Tr2013Cloth
from io_scene_tr_reboot.tr.tr2013.Tr2013Collection import Tr2013Collection
from io_scene_tr_reboot.tr.tr2013.Tr2013Collision import Tr2013Collision
from io_scene_tr_reboot.tr.tr2013.Tr2013Mesh import Tr2013Mesh
from io_scene_tr_reboot.tr.tr2013.Tr2013MeshPart import Tr2013MeshPart
from io_scene_tr_reboot.tr.tr2013.Tr2013Model import Tr2013Model
from io_scene_tr_reboot.tr.tr2013.Tr2013Skeleton import Tr2013Skeleton

class Tr2013Factory(IFactory):
    @property
    def game(self) -> CdcGame:
        return CdcGame.TR2013

    def create_collection(self, object_ref_file_path: str) -> Collection:
        return Tr2013Collection(object_ref_file_path)

    def create_model(self, model_id: int, model_data_id: int) -> IModel:
        return Tr2013Model(model_id, model_data_id)

    def create_mesh(self, model: IModel) -> IMesh:
        return Tr2013Mesh(cast(Tr2013Model, model).header)

    def create_mesh_part(self) -> IMeshPart:
        return Tr2013MeshPart()

    def create_skeleton(self, id: int) -> ISkeleton:
        return Tr2013Skeleton(id)

    def create_bone(self) -> IBone:
        bone = Tr2013Bone()
        bone.min = Vector()
        bone.max = Vector()
        bone.info_ref = None
        return bone

    def deserialize_bone_constraint(self, data: str) -> IBoneConstraint | None:
        return None

    def create_cloth(self, definition_id: int, tune_id: int) -> Cloth:
        return Tr2013Cloth(definition_id, tune_id)

    def create_collision(self, type: CollisionType, hash: int) -> Collision:
        return Tr2013Collision.create(type, hash)

    def deserialize_collision(self, data: str) -> Collision:
        return Tr2013Collision.deserialize(data)
