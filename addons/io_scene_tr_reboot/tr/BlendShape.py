from array import array
from typing import Optional, Sequence, cast
from mathutils import Vector
from io_scene_tr_reboot.tr.VertexOffsets import VertexOffsets
from io_scene_tr_reboot.util.BinaryReader import BinaryReader
from io_scene_tr_reboot.util.BinaryWriter import BinaryWriter
from ctypes import sizeof
from io_scene_tr_reboot.util.CStruct import CInt, CLong, CStruct
from io_scene_tr_reboot.util.Enumerable import Enumerable
from io_scene_tr_reboot.util.SlotsBase import SlotsBase

class _BlendShapesHeader(CStruct):
    num_blend_shapes: CInt
    num_vertex_offsets: CInt
    field_8: CInt
    positions_offset: CInt
    normals_offset: CInt
    colors_offset: CInt
    segments_offset: CInt
    vertex_indices_offset: CInt
    blend_shape_bitmask_ptr: CLong
    blend_shape_data_ptr: CLong
    blend_shape_srvs_ptr: CLong

assert(sizeof(_BlendShapesHeader) == 0x38)

class BlendShape(SlotsBase):
    name: str | None
    vertices: dict[int, VertexOffsets]

    def __init__(self) -> None:
        self.name = None
        self.vertices = {}

    @staticmethod
    def read(reader: BinaryReader, model_data_header_pos: int, num_blend_shapes: int, blend_shape_names: list[str] | None, num_vertices: int) -> list[Optional["BlendShape"]]:
        header = reader.read_struct(_BlendShapesHeader)

        reader.position = model_data_header_pos + header.blend_shape_bitmask_ptr
        supported_blendshape_bitmasks: Sequence[int] = reader.read_uint32_list((num_blend_shapes + 0x1F) >> 5)
        if header.num_blend_shapes == 0:
            reader.align(0x20)
            return []

        reader.position = model_data_header_pos + header.segments_offset
        num_vertex_batches: int = (num_vertices + 0x3F) >> 6
        blend_shape_ranges: Sequence[int] = reader.read_uint32_list(num_vertex_batches * header.num_blend_shapes)

        reader.position = model_data_header_pos + header.positions_offset
        position_offsets: Sequence[int] = reader.read_uint32_list(header.num_vertex_offsets)

        reader.position = model_data_header_pos + header.normals_offset
        normal_offsets: Sequence[int] = reader.read_uint32_list(header.num_vertex_offsets)

        reader.position = model_data_header_pos + header.colors_offset
        color_offsets: Sequence[int] = reader.read_uint32_list(header.num_vertex_offsets)

        reader.position = model_data_header_pos + header.vertex_indices_offset
        vertex_indices: memoryview = reader.read_bytes(header.num_vertex_offsets)
        reader.align(0x20)

        blend_shapes: list[BlendShape] = []
        for _ in range(header.num_blend_shapes):
            blend_shape = BlendShape()
            blend_shapes.append(blend_shape)

        range_idx: int = 0
        for vertex_batch_idx in range(num_vertex_batches):
            for blend_shape_idx in range(header.num_blend_shapes):
                range_start  = blend_shape_ranges[range_idx] >> 8
                range_length = blend_shape_ranges[range_idx] & 0xFF

                for range_vertex_idx in range(range_length):
                    position_offset = BlendShape.unpack_vertex_offset(position_offsets[range_start + range_vertex_idx], 8.0)
                    normal_offset   = BlendShape.unpack_vertex_offset(normal_offsets[range_start + range_vertex_idx], 2.0)
                    color_offset    = BlendShape.unpack_vertex_offset(color_offsets[range_start + range_vertex_idx], 1.0)
                    vertex_idx = vertex_batch_idx * 64 + vertex_indices[range_start + range_vertex_idx]
                    blend_shapes[blend_shape_idx].vertices[vertex_idx] = VertexOffsets(position_offset, normal_offset, color_offset)

                range_idx = range_idx + 1

        blend_shapes_with_gaps = cast(list[BlendShape | None], blend_shapes)
        for blend_shape_idx in range(len(supported_blendshape_bitmasks) * 32):
            if (supported_blendshape_bitmasks[blend_shape_idx >> 5] & (1 << (blend_shape_idx & 0x1F))) == 0:
                blend_shapes_with_gaps.insert(blend_shape_idx, None)

        if blend_shape_names is not None:
            for i, blend_shape in enumerate(blend_shapes_with_gaps):
                if blend_shape is not None:
                    blend_shape.name = blend_shape_names[i]

        return blend_shapes_with_gaps

    @staticmethod
    def write(writer: BinaryWriter, model_data_header_pos: int, blend_shapes: list[Optional["BlendShape"]], num_vertices: int) -> None:
        header_pos = writer.position
        header = _BlendShapesHeader()
        header.num_blend_shapes = Enumerable(blend_shapes).count(lambda b: b is not None)
        header.num_vertex_offsets = Enumerable(blend_shapes).sum(lambda b: b is not None and len(b.vertices) or 0)
        writer.write_struct(header)
        writer.align(0x20)

        supported_blendshape_bitmasks: list[int] = [0] * ((len(blend_shapes) + 0x1F) >> 5)
        for i, blend_shape in enumerate(blend_shapes):
            if blend_shape is not None:
                supported_blendshape_bitmasks[i >> 5] |= 1 << (i & 0x1F)

        header.blend_shape_bitmask_ptr = writer.position - model_data_header_pos
        writer.write_uint32_list(supported_blendshape_bitmasks)
        writer.align(0x20)

        num_vertex_batches: int = (num_vertices + 0x3F) >> 6
        blend_shape_ranges = array("I", [0]) * (num_vertex_batches * header.num_blend_shapes)
        position_offsets   = array("I", [0]) * header.num_vertex_offsets
        normal_offsets     = array("I", [0]) * header.num_vertex_offsets
        color_offsets      = array("I", [0]) * header.num_vertex_offsets
        vertex_indices     = array("B", [0]) * header.num_vertex_offsets

        range_idx: int = 0
        range_start: int = 0
        vertex_offset_idx: int = 0
        for vertex_batch_idx in range(num_vertex_batches):
            for blend_shape in blend_shapes:
                if blend_shape is None:
                    continue

                range_length: int = 0
                for batch_vertex_idx in range(64):
                    vertex = blend_shape.vertices.get(vertex_batch_idx * 64 + batch_vertex_idx)
                    if vertex is None:
                        continue

                    position_offsets[vertex_offset_idx] = BlendShape.pack_vertex_offset(vertex.position_offset, 8.0)
                    normal_offsets[vertex_offset_idx]   = BlendShape.pack_vertex_offset(vertex.normal_offset, 2.0)
                    color_offsets[vertex_offset_idx]    = BlendShape.pack_vertex_offset(vertex.color_offset, 1.0)
                    vertex_indices[vertex_offset_idx] = batch_vertex_idx
                    vertex_offset_idx += 1
                    range_length += 1

                blend_shape_ranges[range_idx] = range_length | (range_start << 8)
                range_start += range_length
                range_idx += 1

        header.segments_offset = writer.position - model_data_header_pos
        writer.write_bytes(memoryview(blend_shape_ranges))
        writer.align(0x20)

        header.positions_offset = writer.position - model_data_header_pos
        writer.write_bytes(memoryview(position_offsets))
        writer.align(0x20)

        header.normals_offset = writer.position - model_data_header_pos
        writer.write_bytes(memoryview(normal_offsets))
        writer.align(0x20)

        header.colors_offset = writer.position - model_data_header_pos
        writer.write_bytes(memoryview(color_offsets))
        writer.align(0x20)

        header.vertex_indices_offset = writer.position - model_data_header_pos
        writer.write_bytes(memoryview(vertex_indices))
        writer.align(0x20)

        end_pos = writer.position
        writer.position = header_pos
        writer.write_struct(header)
        writer.position = end_pos

    @staticmethod
    def unpack_vertex_offset(value: int, scale: float) -> Vector:
        return Vector((
            ((value         & 0x3FF) / 1023.0 * 2.0 - 1.0) * scale,
            (((value >> 10) & 0x3FF) / 1023.0 * 2.0 - 1.0) * scale,
            (((value >> 20) & 0x3FF) / 1023.0 * 2.0 - 1.0) * scale
        ))

    @staticmethod
    def pack_vertex_offset(offset: Vector, scale: float) -> int:
        max_component = max(abs(offset.x), abs(offset.y), abs(offset.z))
        if max_component > scale:
            offset = offset / max_component * scale

        return (int((offset.x + scale) / (scale * 2.0) * 1023.0 + 0.5)) | \
               (int((offset.y + scale) / (scale * 2.0) * 1023.0 + 0.5) << 10) | \
               (int((offset.z + scale) / (scale * 2.0) * 1023.0 + 0.5) << 20)
