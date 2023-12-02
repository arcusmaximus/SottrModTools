from ctypes import sizeof
from io_scene_sottr.tr.ResourceKey import ResourceKey
from io_scene_sottr.tr.ResourceReader import ResourceReader
from io_scene_sottr.tr.ResourceReference import ResourceReference
from io_scene_sottr.util.CStruct import CByte, CInt, CStruct
from io_scene_sottr.util.SlotsBase import SlotsBase

class Material(SlotsBase):
    pixel_shader_textures: list[ResourceKey]
    vertex_shader_textures: list[ResourceKey]

    def __init__(self) -> None:
        self.pixel_shader_textures = []
        self.vertex_shader_textures = []

    def read(self, reader: ResourceReader) -> None:
        reader.skip(0x54)
        magic = bytes(reader.read_bytes(4))
        if magic != b"DtaM":
            raise Exception("Invalid magic in material resource")
        
        for shader_set_ref in reader.read_ref_list(9):
            if shader_set_ref is None:
                continue
            
            reader.seek(shader_set_ref)
            shader_set = reader.read_struct(_MaterialShaderSet)
            if shader_set.ps_textures_ref is not None:
                self.read_shader_textures(reader, shader_set.ps_textures_ref, shader_set.num_ps_textures, self.pixel_shader_textures)
            
            if shader_set.vs_textures_ref is not None:
                self.read_shader_textures(reader, shader_set.vs_textures_ref, shader_set.num_vs_textures, self.vertex_shader_textures)

    def read_shader_textures(self, reader: ResourceReader, ref: ResourceReference, count: int, textures: list[ResourceKey]) -> None:
        reader.seek(ref)
        for _ in range(count):
            texture_ref = reader.read_ref()
            reader.skip(4 + 4)
            #shader_register = (reader.read_uint16() >> 11) & 0x1F
            #reader.skip(2)
            if texture_ref is not None and texture_ref not in textures:
                textures.append(texture_ref)

class _MaterialShaderSet(CStruct):
    pixel_shader_ref: ResourceReference | None
    vertex_shader_ref: ResourceReference | None
    flags: CInt

    num_ps_textures_sub: CByte
    num_ps_texture_ranges: CByte
    num_ps_textures: CByte
    ps_texture_range_start: CByte
    ps_textures_ref: ResourceReference | None
    num_ps_constants: CInt
    field_24: CInt
    ps_constants_ref: ResourceReference | None

    num_vs_textures_sub: CByte
    num_vs_texture_ranges: CByte
    num_vs_textures: CByte
    vs_texture_range_start: CByte
    field_34: CInt
    vs_textures_ref: ResourceReference | None
    num_vs_constants: CInt
    field_44: CInt
    vs_constants_ref: ResourceReference | None

    field_50: CInt
    field_54: CInt
    tesselation_shader_set_ref: ResourceReference | None
    shader_input_elements_ref: ResourceReference | None

assert(sizeof(_MaterialShaderSet) == 0x68)
