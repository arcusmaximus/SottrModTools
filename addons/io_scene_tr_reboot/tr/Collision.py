from abc import abstractmethod
from enum import IntEnum
from typing import ClassVar, NamedTuple, cast
from mathutils import Matrix
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader
from io_scene_tr_reboot.util.Enumerable import Enumerable
from io_scene_tr_reboot.util.Serializer import Serializer

class CollisionType(IntEnum):
    SPHERE = 0
    CAPSULE = 1
    PLANE = 2
    WEDGE = 3
    BOX = 4
    FACE = 5
    DOUBLERADIICAPSULE = 6

class CollisionKey(NamedTuple):
    type: CollisionType
    hash: int

class CollisionInput(NamedTuple):
    reader: ResourceReader
    transform: Matrix

class Collision:
    type_mapping: ClassVar[dict[CollisionType, type["Collision"]]] = {}

    @classmethod
    def create(cls, type: CollisionType, hash: int) -> "Collision":
        return cls.type_mapping[type](hash)

    hash: int
    global_bone_id: int
    transform: Matrix | None

    def __init__(self, hash: int) -> None:
        self.hash = hash
        self.global_bone_id = -1
        self.transform = None       # type: ignore

    @property
    def type(self) -> CollisionType:
        return Enumerable(self.type_mapping.items()).first(lambda p: p[1] == type(self))[0]

    @abstractmethod
    def _read(self, reader: ResourceReader) -> None: ...

    def serialize(self) -> str:
        return Serializer.serialize_object(self, { "type": str(self.type) })

    @classmethod
    def deserialize(cls, data: str) -> "Collision":
        def create_collision(values: dict[str, str]) -> Collision:
            type = CollisionType(int(values["type"]))
            hash = int(values["hash"])
            return cls.create(type, hash)

        return cast(Collision, Serializer.deserialize_object(data, create_collision))

class CollisionSphere(Collision):
    radius: float

    def __init__(self, hash: int) -> None:
        super().__init__(hash)
        self.radius = 1.0

class CollisionCapsule(Collision):
    radius: float
    length: float | None
    target_global_bone_id: int | None

    def __init__(self, hash: int) -> None:
        super().__init__(hash)
        self.radius = 1.0
        self.length = None
        self.target_global_bone_id = None

class CollisionDoubleRadiiCapsule(Collision):
    radius_1: float
    radius_2: float
    length: float

    def __init__(self, hash: int) -> None:
        super().__init__(hash)
        self.radius_1 = 1.0
        self.radius_2 = 1.0
        self.length = 1.0

class CollisionBox(Collision):
    width: float
    depth: float
    height: float

    def __init__(self, hash: int) -> None:
        super().__init__(hash)
        self.width = 1.0
        self.depth = 1.0
        self.height = 1.0
