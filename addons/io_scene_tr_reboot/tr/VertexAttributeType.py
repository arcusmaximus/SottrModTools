from abc import abstractmethod
import struct
from typing import ClassVar

class VertexAttributeType:
    id: int
    size: ClassVar[int]

    def __init__(self, id: int) -> None:
        self.id = id

    @abstractmethod
    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]: ...

    @abstractmethod
    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]): ...

class VertexAttributeType_FLOAT1(VertexAttributeType):
    size = 1 * 4

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        return struct.unpack_from("<1f", buffer, offset)

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        struct.pack_into("<1f", buffer, offset, *value)

class VertexAttributeType_FLOAT2(VertexAttributeType):
    size = 2 * 4

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        return struct.unpack_from("<2f", buffer, offset)

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        struct.pack_into("<2f", buffer, offset, *value)

class VertexAttributeType_FLOAT3(VertexAttributeType):
    size = 3 * 4

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        return struct.unpack_from("<3f", buffer, offset)

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        struct.pack_into("<3f", buffer, offset, *value)

class VertexAttributeType_FLOAT4(VertexAttributeType):
    size = 4 * 4

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        return struct.unpack_from("<4f", buffer, offset)

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        struct.pack_into("<4f", buffer, offset, *value)

class VertexAttributeType_R8G8B8A8_UNORM(VertexAttributeType):
    size = 4 * 1

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        return (
            buffer[offset + 0] / 255.0,
            buffer[offset + 1] / 255.0,
            buffer[offset + 2] / 255.0,
            buffer[offset + 3] / 255.0
        )

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        buffer[offset + 0] = int(value[0] * 255)
        buffer[offset + 1] = int(value[1] * 255)
        buffer[offset + 2] = int(value[2] * 255)
        buffer[offset + 3] = int(value[3] * 255)

class VertexAttributeType_R8G8B8A8_UINT(VertexAttributeType):
    size = 4 * 1

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        return (
            buffer[offset + 0],
            buffer[offset + 1],
            buffer[offset + 2],
            buffer[offset + 3]
        )

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        buffer[offset + 0] = int(value[0])
        buffer[offset + 1] = int(value[1])
        buffer[offset + 2] = int(value[2])
        buffer[offset + 3] = int(value[3])

class VertexAttributeType_R16G16_SINT(VertexAttributeType):
    size = 2 * 2

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        return struct.unpack_from("<2h", buffer, offset)

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        struct.pack_into("<2h", buffer, offset, *value)

class VertexAttributeType_R16G16B16A16_SINT(VertexAttributeType):
    size = 4 * 2

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        return struct.unpack_from("<4h", buffer, offset)

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        struct.pack_into("<4h", buffer, offset, *value)

class VertexAttributeType_R16G16B16A16_UINT(VertexAttributeType):
    size = 4 * 2

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        return struct.unpack_from("<4H", buffer, offset)

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        struct.pack_into("<4H", buffer, offset, *value)

class VertexAttributeType_R32G32B32A32_UINT(VertexAttributeType):
    size = 4 * 4

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        return struct.unpack_from("<4I", buffer, offset)

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        struct.pack_into("<4I", buffer, offset, *value)

class VertexAttributeType_R16G16_SNORM(VertexAttributeType):
    size = 2 * 2

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        value = struct.unpack_from("<2h", buffer, offset)
        return (value[0] / 32768.0, value[1] / 32768.0)

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        struct.pack_into(
            "<2h",
            buffer,
            offset,
            int(value[0] * 32768),
            int(value[1] * 32768)
        )

class VertexAttributeType_R16G16B16A16_SNORM(VertexAttributeType):
    size = 4 * 2

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        value = struct.unpack_from("<4h", buffer, offset)
        return (
            value[0] / 32768.0,
            value[1] / 32768.0,
            value[2] / 32768.0,
            value[3] / 32768.0
        )

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        struct.pack_into(
            "<4h",
            buffer,
            offset,
            int(value[0] * 32768),
            int(value[1] * 32768),
            int(value[2] * 32768),
            int(value[3] * 32768)
        )

class VertexAttributeType_R16G16_UNORM(VertexAttributeType):
    size = 2 * 2

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        value = struct.unpack_from("<2H", buffer, offset)
        return (value[0] / 65535.0, value[1] / 65535.0)

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        struct.pack_into(
            "<2H",
            buffer,
            offset,
            int(value[0] * 65535),
            int(value[1] * 65535)
        )

class VertexAttributeType_R16G16B16A16_UNORM(VertexAttributeType):
    size = 4 * 2

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        value = struct.unpack_from("<4H", buffer, offset)
        return (
            value[0] / 65535.0,
            value[1] / 65535.0,
            value[2] / 65535.0,
            value[3] / 65535.0
        )

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        struct.pack_into(
            "<4H",
            buffer,
            offset,
            int(value[0] * 65535),
            int(value[1] * 65535),
            int(value[2] * 65535),
            int(value[3] * 65535)
        )

class VertexAttributeType_R10G10B10A2_UINT(VertexAttributeType):
    size = 4

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        packed_value: int = struct.unpack_from("<I", buffer, offset)[0]
        return (
            packed_value & 0x3FF,
            (packed_value >> 10) & 0x3FF,
            (packed_value >> 20) & 0x3FF,
            (packed_value >> 30)
        )

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        packed_value = int(value[0]) | (int(value[1]) << 10) | (int(value[2]) << 20) | (int(value[3]) << 30)
        struct.pack_into("<I", buffer, offset, packed_value)

class VertexAttributeType_R10G10B10A2_UNORM(VertexAttributeType):
    size = 4

    def read(self, buffer: bytes | memoryview, offset: int) -> tuple[float, ...]:
        packed_value: int = struct.unpack_from("<I", buffer, offset)[0]
        return (
            (packed_value & 0x3FF) / 1023.0,
            ((packed_value >> 10) & 0x3FF) / 1023.0,
            ((packed_value >> 20) & 0x3FF) / 1023.0,
            (packed_value >> 30) / 3.0
        )

    def write(self, buffer: bytearray | memoryview, offset: int, value: tuple[float, ...]):
        packed_value = (int(value[0] * 1023.0 + 0.5)) |       \
                       (int(value[1] * 1023.0 + 0.5) << 10) | \
                       (int(value[2] * 1023.0 + 0.5) << 20) | \
                       (int(value[3] * 3.0    + 0.5) << 30)
        struct.pack_into("<I", buffer, offset, packed_value)
