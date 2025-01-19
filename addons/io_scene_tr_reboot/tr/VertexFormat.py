from ctypes import sizeof
from typing import Literal
from io_scene_tr_reboot.tr.VertexAttribute import VertexAttribute
from io_scene_tr_reboot.tr.VertexAttributeType import VertexAttributeType
from io_scene_tr_reboot.tr.VertexAttributeTypes import VertexAttributeTypes
from io_scene_tr_reboot.util.BinaryReader import BinaryReader
from io_scene_tr_reboot.util.BinaryWriter import BinaryWriter
from io_scene_tr_reboot.util.CStruct import CArray, CByte, CInt, CShort, CStruct, CULong
from io_scene_tr_reboot.util.Enumerable import Enumerable
from io_scene_tr_reboot.util.SlotsBase import SlotsBase

class _VertexFormatHeader(CStruct):
    hash: CULong
    num_attributes: CShort
    vertex_sizes: CArray[CByte, Literal[2]]
    padding: CInt

class VertexFormat(SlotsBase):
    hash: int
    vertex_sizes: list[int]
    attributes: list[VertexAttribute]
    types: VertexAttributeTypes

    def __init__(self, types: VertexAttributeTypes) -> None:
        self.hash = 0
        self.vertex_sizes = [0, 0]
        self.attributes = []
        self.types = types

    def has_attribute(self, name_hash: int) -> bool:
        return Enumerable(self.attributes).any(lambda a: a.name_hash == name_hash)

    def add_attribute(self, name_hash: int, type: VertexAttributeType, vertex_buffer_idx: int) -> VertexAttribute:
        attr = VertexAttribute()
        attr.name_hash = name_hash
        attr.vertex_buffer_idx = vertex_buffer_idx
        attr.offset = self.vertex_sizes[vertex_buffer_idx]
        attr.type = type
        attr.type_id = type.id

        self.attributes.append(attr)
        self.vertex_sizes[vertex_buffer_idx] += type.size
        return attr

    def read(self, reader: BinaryReader) -> None:
        header = reader.read_struct(_VertexFormatHeader)
        self.hash = header.hash
        self.vertex_sizes = list(header.vertex_sizes)

        for _ in range(header.num_attributes):
            attr = reader.read_struct(VertexAttribute)
            type = self.types.get(attr.type_id)
            if type is None:
                raise Exception("Unsupported vertex attribute type")

            attr.type = type
            self.attributes.append(attr)

    def write(self, writer: BinaryWriter) -> None:
        header = _VertexFormatHeader()
        header.hash = self.hash
        header.num_attributes = len(self.attributes)
        for i in range(len(self.vertex_sizes)):
            header.vertex_sizes[i] = self.vertex_sizes[i]

        writer.write_struct(header)
        for attr in self.attributes:
            writer.write_struct(attr)

    @property
    def size(self) -> int:
        return sizeof(_VertexFormatHeader) + len(self.attributes) * sizeof(VertexAttribute)
