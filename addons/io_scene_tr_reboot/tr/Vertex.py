from typing import Sequence
from io_scene_tr_reboot.tr.VertexFormat import VertexFormat
from io_scene_tr_reboot.util.SlotsBase import SlotsBase

class Vertex(SlotsBase):
    attributes: dict[int, tuple[float, ...]]

    def __init__(self) -> None:
        self.attributes = {}

    def read(self, vertex_buffers: Sequence[bytes | memoryview], index: int, format: VertexFormat) -> None:
        for format_attr in format.attributes:
            buffer = vertex_buffers[format_attr.vertex_buffer_idx]
            offset_in_buffer = format.vertex_sizes[format_attr.vertex_buffer_idx] * index + format_attr.offset
            self.attributes[format_attr.name_hash] = format_attr.type.read(buffer, offset_in_buffer)

    def write(self, vertex_buffers: list[bytearray], index: int, format: VertexFormat) -> None:
        for format_attr in format.attributes:
            buffer: bytearray = vertex_buffers[format_attr.vertex_buffer_idx]
            offset_in_buffer = format.vertex_sizes[format_attr.vertex_buffer_idx] * index + format_attr.offset
            format_attr.type.write(buffer, offset_in_buffer, self.attributes[format_attr.name_hash])
