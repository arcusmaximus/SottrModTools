
import struct
from typing import Sequence
from io_scene_sottr.tr.VertexFormat import VertexFormat
from io_scene_sottr.util.SlotsBase import SlotsBase

class Vertex(SlotsBase):
    attributes: dict[int, tuple[float, ...]]

    def __init__(self) -> None:
        self.attributes = {}

    def read(self, vertex_buffers: Sequence[bytes | memoryview], index: int, format: VertexFormat) -> None:
        for format_attr in format.attributes:
            buffer = vertex_buffers[format_attr.vertex_buffer_idx]
            offset_in_buffer = format.vertex_sizes[format_attr.vertex_buffer_idx] * index + format_attr.offset
            value: tuple[float, ...]

            match format_attr.format:
                case 0:
                    value = struct.unpack_from("<1f", buffer, offset_in_buffer)

                case 1:
                    value = struct.unpack_from("<2f", buffer, offset_in_buffer)

                case 2:
                    value = struct.unpack_from("<3f", buffer, offset_in_buffer)
                
                case 3:
                    value = struct.unpack_from("<4f", buffer, offset_in_buffer)

                case 4 | 5 | 6 | 7 | 13 | 22:       # R8G8B8A8_UNORM
                    value = (
                        buffer[offset_in_buffer + 0] / 255.0,
                        buffer[offset_in_buffer + 1] / 255.0,
                        buffer[offset_in_buffer + 2] / 255.0,
                        buffer[offset_in_buffer + 3] / 255.0
                    )
                
                case 8 | 23:                        # R8G8B8A8_UINT
                    value = (
                        buffer[offset_in_buffer + 0],
                        buffer[offset_in_buffer + 1],
                        buffer[offset_in_buffer + 2],
                        buffer[offset_in_buffer + 3]
                    )
                
                case 9:                             # R16G16_SINT
                    value = struct.unpack_from("<2h", buffer, offset_in_buffer)
                
                case 10:                            # R16G16B16A16_SINT
                    value = struct.unpack_from("<4h", buffer, offset_in_buffer)

                case 11 | 24:                       # R16G16B16A16_UINT
                    value = struct.unpack_from("<4H", buffer, offset_in_buffer)

                case 12:                            # R32G32B32A32_UINT
                    value = struct.unpack_from("<4I", buffer, offset_in_buffer)

                case 14 | 25:                       # R16G16_SNORM
                    value = struct.unpack_from("<2h", buffer, offset_in_buffer)
                    value = (value[0] / 32768.0, value[1] / 32768.0)
                
                case 15 | 26:                       # R16G16B16A16_SNORM
                    value = struct.unpack_from("<4h", buffer, offset_in_buffer)
                    value = (
                        value[0] / 32768.0,
                        value[1] / 32768.0,
                        value[2] / 32768.0,
                        value[3] / 32768.0
                    )

                case 16:                            # R16G16_UNORM
                    value = struct.unpack_from("<2H", buffer, offset_in_buffer)
                    value = (value[0] / 65535.0, value[1] / 65535.0)
                
                case 17:                            # R16G16B16A16_UNORM
                    value = struct.unpack_from("<4H", buffer, offset_in_buffer)
                    value = (
                        value[0] / 65535.0,
                        value[1] / 65535.0,
                        value[2] / 65535.0,
                        value[3] / 65535.0
                    )

                case 18:                            # R10G10B10A2_UINT
                    packed_value: int = struct.unpack_from("<I", buffer, offset_in_buffer)[0]
                    value = (
                        packed_value & 0x3FF,
                        (packed_value >> 10) & 0x3FF,
                        (packed_value >> 20) & 0x3FF,
                        (packed_value >> 30)
                    )
                
                case 19 | 20:                       # R10G10B10A2_UNORM
                    packed_value: int = struct.unpack_from("<I", buffer, offset_in_buffer)[0]
                    value = (
                        (packed_value & 0x3FF) / 1023.0,
                        ((packed_value >> 10) & 0x3FF) / 1023.0,
                        ((packed_value >> 20) & 0x3FF) / 1023.0,
                        (packed_value >> 30) / 3.0
                    )

                case _:
                    raise Exception(f"Encountered unsupported vertex attribute format {format_attr.format}")

            self.attributes[format_attr.name_hash] = value

    def write(self, vertex_buffers: list[bytearray], index: int, format: VertexFormat) -> None:
        for format_attr in format.attributes:
            buffer: bytearray = vertex_buffers[format_attr.vertex_buffer_idx]
            offset_in_buffer = format.vertex_sizes[format_attr.vertex_buffer_idx] * index + format_attr.offset
            value: tuple[float, ...] = self.attributes[format_attr.name_hash]

            match format_attr.format:
                case 0:
                    struct.pack_into("<1f", buffer, offset_in_buffer, *value)

                case 1:
                    struct.pack_into("<2f", buffer, offset_in_buffer, *value)

                case 2:
                    struct.pack_into("<3f", buffer, offset_in_buffer, *value)
                
                case 3:
                    struct.pack_into("<4f", buffer, offset_in_buffer, *value)

                case 4 | 5 | 6 | 7 | 13 | 22:       # R8G8B8A8_UNORM
                    buffer[offset_in_buffer + 0] = int(value[0] * 255)
                    buffer[offset_in_buffer + 1] = int(value[1] * 255)
                    buffer[offset_in_buffer + 2] = int(value[2] * 255)
                    buffer[offset_in_buffer + 3] = int(value[3] * 255)
                
                case 8 | 23:                        # R8G8B8A8_UINT
                    buffer[offset_in_buffer + 0] = int(value[0])
                    buffer[offset_in_buffer + 1] = int(value[1])
                    buffer[offset_in_buffer + 2] = int(value[2])
                    buffer[offset_in_buffer + 3] = int(value[3])
                
                case 9:                             # R16G16_SINT
                    struct.pack_into("<2h", buffer, offset_in_buffer, *value)
                
                case 10:                            # R16G16B16A16_SINT
                    struct.pack_into("<4h", buffer, offset_in_buffer, *value)

                case 11 | 24:                       # R16G16B16A16_UINT
                    struct.pack_into("<4H", buffer, offset_in_buffer, *value)

                case 12:                            # R32G32B32A32_UINT
                    struct.pack_into("<4I", buffer, offset_in_buffer, *value)

                case 14 | 25:                       # R16G16_SNORM
                    struct.pack_into(
                        "<2h",
                        buffer,
                        offset_in_buffer,
                        int(value[0] * 32768),
                        int(value[1] * 32768)
                    )
                
                case 15 | 26:                       # R16G16B16A16_SNORM
                    struct.pack_into(
                        "<4h",
                        buffer,
                        offset_in_buffer,
                        int(value[0] * 32768),
                        int(value[1] * 32768),
                        int(value[2] * 32768),
                        int(value[3] * 32768)
                    )

                case 16:                            # R16G16_UNORM
                    struct.pack_into(
                        "<2H",
                        buffer,
                        offset_in_buffer,
                        int(value[0] * 65535),
                        int(value[1] * 65535)
                    )
                
                case 17:                            # R16G16B16A16_UNORM
                    struct.pack_into(
                        "<4H",
                        buffer,
                        offset_in_buffer,
                        int(value[0] * 65535),
                        int(value[1] * 65535),
                        int(value[2] * 65535),
                        int(value[3] * 65535)
                    )

                case 18:                            # R10G10B10A2_UINT
                    packed_value = int(value[0]) | (int(value[1]) << 10) | (int(value[2]) << 20) | (int(value[3]) << 30)
                    struct.pack_into("<I", buffer, offset_in_buffer, packed_value)
                
                case 19 | 20:                       # R10G10B10A2_UNORM
                    packed_value = (int(value[0] * 1023.0 + 0.5)) |       \
                                   (int(value[1] * 1023.0 + 0.5) << 10) | \
                                   (int(value[2] * 1023.0 + 0.5) << 20) | \
                                   (int(value[3] * 3.0    + 0.5) << 30)
                    struct.pack_into("<I", buffer, offset_in_buffer, packed_value)

                case _:
                    raise Exception(f"Encountered unsupported vertex attribute {format_attr.format}")