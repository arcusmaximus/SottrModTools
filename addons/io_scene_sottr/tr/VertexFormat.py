from ctypes import sizeof
from typing import Literal
from io_scene_sottr.tr.VertexAttribute import VertexAttribute
from io_scene_sottr.util.BinaryReader import BinaryReader
from io_scene_sottr.util.BinaryWriter import BinaryWriter
from io_scene_sottr.util.CStruct import CArray, CByte, CInt, CShort, CStruct, CULong
from io_scene_sottr.util.Enumerable import Enumerable
from io_scene_sottr.util.SlotsBase import SlotsBase

class _VertexFormatHeader(CStruct):
    hash: CULong
    num_attributes: CShort
    vertex_sizes: CArray[CByte, Literal[2]]
    padding: CInt

class VertexFormat(SlotsBase):
    hash: int
    vertex_sizes: list[int]
    attributes: list[VertexAttribute]

    def __init__(self) -> None:
        self.hash = 0
        self.vertex_sizes = [0, 0]
        self.attributes = []
    
    def has_attribute(self, name_hash: int) -> bool:
        return Enumerable(self.attributes).any(lambda a: a.name_hash == name_hash)
    
    def add_attribute(self, name_hash: int, format: int, vertex_buffer_idx: int) -> VertexAttribute:
        attr = VertexAttribute()
        attr.name_hash = name_hash
        attr.vertex_buffer_idx = vertex_buffer_idx
        attr.offset = self.vertex_sizes[vertex_buffer_idx]
        attr.format = format
        
        self.attributes.append(attr)
        self.vertex_sizes[vertex_buffer_idx] += VertexFormat.get_vertex_attr_size(format)
        return attr

    def read(self, reader: BinaryReader) -> None:
        header = reader.read_struct(_VertexFormatHeader)
        self.hash = header.hash
        self.vertex_sizes = list(header.vertex_sizes)

        for _ in range(header.num_attributes):
            attr = reader.read_struct(VertexAttribute)
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

    @staticmethod
    def get_vertex_attr_size(format: int) -> int:
        match format:
            case 0:
                return 1 * 4

            case 1:
                return 2 * 4

            case 2:
                return 3 * 4
            
            case 3:
                return 4 * 4

            case 4 | 5 | 6 | 7 | 13 | 22:       # R8G8B8A8_UNORM
                return 4 * 1
            
            case 8 | 23:                        # R8G8B8A8_UINT
                return 4 * 1
            
            case 9:                             # R16G16_SINT
                return 2 * 2
            
            case 10:                            # R16G16B16A16_SINT
                return 4 * 2

            case 11 | 24:                       # R16G16B16A16_UINT
                return 4 * 2

            case 12:                            # R32G32B32A32_UINT
                return 4 * 4

            case 14 | 25:                       # R16G16_SNORM
                return 2 * 2
            
            case 15 | 26:                       # R16G16B16A16_SNORM
                return 4 * 2

            case 16:                            # R16G16_UNORM
                return 2 * 2
            
            case 17:                            # R16G16B16A16_UNORM
                return 4 * 2

            case 18:                            # R10G10B10A2_UINT
                return 4
            
            case 19 | 20:                       # R10G10B10A2_UNORM
                return 4

            case _:
                raise Exception(f"Vertex attribute format {format} is not supported")

    @property
    def size(self) -> int:
        return sizeof(_VertexFormatHeader) + len(self.attributes) * sizeof(VertexAttribute)
