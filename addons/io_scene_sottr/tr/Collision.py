from abc import abstractmethod
from enum import IntEnum
from typing import ClassVar, NamedTuple
from mathutils import Matrix
from io_scene_sottr.tr.ResourceReader import ResourceReader
from io_scene_sottr.util.Enumerable import Enumerable
from io_scene_sottr.util.SlotsBase import SlotsBase

class CollisionType(IntEnum):
    SPHERE = 0
    CAPSULE = 1
    BOX = 4
    DOUBLERADIICAPSULE = 6

class CollisionKey(NamedTuple):
    type: CollisionType
    hash: int

class CollisionInput(NamedTuple):
    reader: ResourceReader
    transform: Matrix

class Collision(SlotsBase):
    type_mapping: ClassVar[dict[CollisionType, type["Collision"]]] = {}
        
    hash: int
    global_bone_id: int
    transform: Matrix

    def __init__(self, hash: int) -> None:
        self.hash = hash
        self.global_bone_id = -1
        self.transform = Matrix()
    
    @property
    def type(self) -> CollisionType:
        return Enumerable(Collision.type_mapping.items()).first(lambda p: p[1] == type(self))[0]
    
    @staticmethod
    def read_with_transform(type: CollisionType, hash: int, reader: ResourceReader, transform: Matrix) -> "Collision":
        collision = Collision.type_mapping[type](hash)
        collision.read(reader)
        collision.transform = transform
        return collision
    
    @abstractmethod
    def read(self, reader: ResourceReader) -> None: ...

class CollisionSphere(Collision):
    radius: float

    def __init__(self, hash: int) -> None:
        super().__init__(hash)
        self.radius = 1.0
    
    def read(self, reader: ResourceReader) -> None:
        self.radius = reader.read_float()
        self.global_bone_id = reader.read_uint16()

class CollisionCapsule(Collision):
    radius: float
    length: float

    def __init__(self, hash: int) -> None:
        super().__init__(hash)
        self.radius = 1.0
        self.length = 1.0
    
    def read(self, reader: ResourceReader) -> None:
        self.radius = reader.read_float()
        self.length = reader.read_float()
        self.global_bone_id = reader.read_uint16()

class CollisionDoubleRadiiCapsule(Collision):
    radius_1: float
    radius_2: float
    length: float

    def __init__(self, hash: int) -> None:
        super().__init__(hash)
        self.radius_1 = 1.0
        self.radius_2 = 1.0
        self.length = 1.0
    
    def read(self, reader: ResourceReader) -> None:
        self.radius_1 = reader.read_float()
        self.radius_2 = reader.read_float()
        self.length = reader.read_float()
        self.global_bone_id = reader.read_uint16()

class CollisionBox(Collision):
    width: float
    depth: float
    height: float

    def __init__(self, hash: int) -> None:
        super().__init__(hash)
        self.width = 1.0
        self.depth = 1.0
        self.height = 1.0
    
    def read(self, reader: ResourceReader) -> None:
        self.width = reader.read_float()
        self.depth = reader.read_float()
        self.height = reader.read_float()
        self.global_bone_id = reader.read_uint16()

Collision.type_mapping = {
    CollisionType.BOX:                 CollisionBox,
    CollisionType.CAPSULE:             CollisionCapsule,
    CollisionType.DOUBLERADIICAPSULE:  CollisionDoubleRadiiCapsule,
    CollisionType.SPHERE:              CollisionSphere
}
