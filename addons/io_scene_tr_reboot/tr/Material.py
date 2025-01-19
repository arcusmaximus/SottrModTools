from abc import abstractmethod
from typing import Protocol
from io_scene_tr_reboot.tr.ResourceKey import ResourceKey
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader
from io_scene_tr_reboot.tr.ResourceReference import ResourceReference

class IMaterialPass(Protocol):
    ps_textures_ref: ResourceReference | None
    num_ps_textures: int

    vs_textures_ref: ResourceReference | None
    num_vs_textures: int

class Material:
    pixel_shader_textures: list[ResourceKey]
    vertex_shader_textures: list[ResourceKey]

    def __init__(self) -> None:
        self.pixel_shader_textures = []
        self.vertex_shader_textures = []

    def read(self, reader: ResourceReader) -> None:
        reader.skip(self.magic_offset)
        magic = bytes(reader.read_bytes(4))
        if magic != b"DtaM":
            raise Exception("Invalid magic in material resource")

        for pass_ref in reader.read_ref_list(self.num_passes):
            if pass_ref is None:
                continue

            reader.seek(pass_ref)
            material_pass = self.read_pass(reader)
            if material_pass.ps_textures_ref is not None:
                self.read_pass_textures(reader, material_pass.ps_textures_ref, material_pass.num_ps_textures, self.pixel_shader_textures)

            if material_pass.vs_textures_ref is not None:
                self.read_pass_textures(reader, material_pass.vs_textures_ref, material_pass.num_vs_textures, self.vertex_shader_textures)

    def read_pass_textures(self, reader: ResourceReader, ref: ResourceReference, count: int, textures: list[ResourceKey]) -> None:
        reader.seek(ref)
        for _ in range(count):
            texture_ref = reader.read_ref()
            reader.skip(self.pass_texture_extra_info_size)
            if texture_ref is not None and texture_ref not in textures:
                textures.append(texture_ref)

    @property
    @abstractmethod
    def magic_offset(self) -> int: ...

    @property
    @abstractmethod
    def num_passes(self) -> int: ...

    @property
    @abstractmethod
    def pass_texture_extra_info_size(self) -> int: ...

    @abstractmethod
    def read_pass(self, reader: ResourceReader) -> IMaterialPass: ...
