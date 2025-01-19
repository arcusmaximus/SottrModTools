from enum import IntEnum
from io_scene_tr_reboot.tr.Enumerations import CdcGame, ResourceType
from io_scene_tr_reboot.tr.ResourceBuilder import ResourceBuilder
from io_scene_tr_reboot.tr.ResourceKey import ResourceKey
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader
from io_scene_tr_reboot.tr.ResourceReference import ResourceReference

class _RefOffsets(IntEnum):
    NEW_MODEL = 0x68
    BONES = 0x6C
    BONE_ID_MAP = 0x70

class Tr2013LegacyModel:
    refs: dict[int, ResourceReference]
    body: memoryview

    def __init__(self, data: bytes) -> None:
        reader = ResourceReader(ResourceKey(ResourceType.DTP, -1), data, True, CdcGame.TR2013)
        self.refs = { position - reader.resource_body_pos: ref for position, ref in reader.references.items() }
        self.body = reader.read_bytes(len(data) - reader.resource_body_pos)

    @property
    def new_model_ref(self) -> ResourceReference | None:
        return self.refs.get(_RefOffsets.NEW_MODEL)

    @new_model_ref.setter
    def new_model_ref(self, ref: ResourceReference | None) -> None:
        self.__set_ref(_RefOffsets.NEW_MODEL, ref)

    @property
    def bones_ref(self) -> ResourceReference | None:
        return self.refs.get(_RefOffsets.BONES)

    @bones_ref.setter
    def bones_ref(self, ref: ResourceReference | None) -> None:
        self.__set_ref(_RefOffsets.BONES, ref)

    @property
    def bone_id_map_ref(self) -> ResourceReference | None:
        return self.refs.get(_RefOffsets.BONE_ID_MAP)

    @bone_id_map_ref.setter
    def bone_id_map_ref(self, ref: ResourceReference | None) -> None:
        self.__set_ref(_RefOffsets.BONE_ID_MAP, ref)

    def __set_ref(self, offset: int, ref: ResourceReference | None) -> None:
        if ref is not None:
            self.refs[offset] = ref
        else:
            del self.refs[offset]

    def to_bytes(self) -> memoryview:
        writer = ResourceBuilder(ResourceKey(ResourceType.DTP, -1), CdcGame.TR2013)
        writer.write_bytes(self.body)
        for offset, ref in self.refs.items():
            writer.add_ref(offset, ref)

        return writer.build()
