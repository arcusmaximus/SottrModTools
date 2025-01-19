from io import BytesIO
from typing import cast
from io_scene_tr_reboot.tr.Enumerations import CdcGame
from io_scene_tr_reboot.tr.ResourceKey import ResourceKey
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader
from io_scene_tr_reboot.tr.ResourceReference import ResourceReference
from io_scene_tr_reboot.util.BinaryWriter import BinaryWriter

class ResourceBuilder(BinaryWriter):
    resource: ResourceKey
    references: dict[int, ResourceReference]
    game: CdcGame
    pointer_size: int

    def __init__(self, resource: ResourceKey, game: CdcGame) -> None:
        super().__init__(BytesIO())
        self.resource = resource
        self.references = {}
        self.game = game
        self.pointer_size = 4 if game == CdcGame.TR2013 else 8

    def add_ref(self, offset: int, ref: ResourceReference) -> None:
        self.references[offset] = ref

    def make_internal_ref(self, offset: int = -1) -> ResourceReference:
        if offset < 0:
            offset = self.position

        return ResourceReference(self.resource.type, self.resource.id, offset)

    def write_reader(self, reader: ResourceReader) -> None:
        self.__write_resource(
            reader.resource,
            { position - reader.resource_body_pos: ref for position, ref in reader.references.items() },
            memoryview(reader.data)[reader.resource_body_pos:len(reader.data)]
        )

    def write_builder(self, builder: "ResourceBuilder") -> None:
        self.__write_resource(builder.resource, builder.references, cast(BytesIO, builder.stream).getbuffer())

    def __write_resource(self, resource: ResourceKey, refs: dict[int, ResourceReference], body: memoryview) -> None:
        for offset, ref in refs.items():
            if ref.type == resource.type and ref.id == resource.id:
                ref = ResourceReference(self.resource.type, self.resource.id, self.position + ref.offset)

            self.add_ref(self.position + offset, ref)

        self.write_bytes(body)

    def write_internal_ref(self, offset: int = -1) -> ResourceReference:
        ref = self.make_internal_ref(offset)
        self.write_ref(ref)
        return ref

    def write_ref(self, ref: ResourceKey | ResourceReference | None) -> None:
        if ref is None:
            if self.pointer_size == 4:
                self.write_uint32(0)
            else:
                self.write_uint64(0)
            return

        if not isinstance(ref, ResourceReference):
            ref = ResourceReference(ref.type, ref.id, 0)

        self.add_ref(self.position, ref)
        if self.game == CdcGame.TR2013:
            if ref.offset != 0:
                self.write_uint32((ref.type << 24) | ref.id)
            else:
                self.write_uint32(ref.id)
        else:
            self.write_uint64(ref.id)

    def build(self) -> memoryview:
        if len(self.references) == 0:
            return cast(BytesIO, self.stream).getbuffer()

        internal_refs: dict[int, ResourceReference] = {}
        wide_external_refs: dict[int, ResourceReference] = {}
        packed_external_refs: dict[int, ResourceReference] = {}
        for offset, ref in self.references.items():
            if ref.type == self.resource.type and ref.id == self.resource.id:
                internal_refs[offset] = ref
            elif ref.offset != 0:
                wide_external_refs[offset] = ref
            else:
                packed_external_refs[offset] = ref

        result = BytesIO()
        result_writer = BinaryWriter(result)
        result_writer.write_int32(len(internal_refs))
        result_writer.write_int32(len(wide_external_refs))
        result_writer.write_int32(0)
        result_writer.write_int32(0)
        result_writer.write_int32(len(packed_external_refs))

        for offset, ref in internal_refs.items():
            result_writer.write_int32(offset)
            result_writer.write_int32(ref.offset)

        for offset, ref in wide_external_refs.items():
            if self.game == CdcGame.TR2013:
                result_writer.write_uint64((ref.offset << 39) | ((offset // 4) << 16))
            else:
                result_writer.write_int32(ref.type)
                result_writer.write_int32(ref.id)
                result_writer.write_int32(ref.offset)

        for offset, ref in packed_external_refs.items():
            result_writer.write_uint32((ref.type << 25) | (offset // 4))

        result_writer.write_bytes(cast(BytesIO, self.stream).getbuffer())
        return result.getbuffer()
