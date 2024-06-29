from io_scene_sottr.tr.Mesh import Mesh
from io_scene_sottr.tr.MeshPart import MeshPart
from io_scene_sottr.tr.ModelDataHeader import ModelDataHeader
from io_scene_sottr.util.BinaryReader import BinaryReader
from io_scene_sottr.util.BinaryWriter import BinaryWriter
from io_scene_sottr.util.Enumerable import Enumerable
from io_scene_sottr.util.SlotsBase import SlotsBase

class ModelData(SlotsBase):
    id: int
    header: ModelDataHeader
    meshes: list[Mesh]

    def __init__(self, id: int) -> None:
        self.id = id
        self.header = ModelDataHeader()
        self.header.data2_offset = 0xFFFFFFFF
        self.meshes = []

    def read(self, reader: BinaryReader) -> None:
        self.header = reader.read_struct(ModelDataHeader)

        if self.header.data1_size != 0 or self.header.data2_offset != 0xFFFFFFFF:
            raise NotImplementedError()
        
        reader.skip(self.header.num_lod_levels * 0x40)
        reader.skip(self.header.num_bone_mappings * 4)
        reader.align(0x20)

        for _ in range(self.header.num_meshes):
            mesh = Mesh(self.header)
            mesh.read_header(reader)
            self.meshes.append(mesh)
        
        for mesh in self.meshes:
            mesh.read_bone_indices(reader)
        
        for mesh in self.meshes:
            mesh.read_content(reader)

        if self.header.data6_offset != 0:
            reader.skip(self.header.num_blend_shapes * 0x40)
        
        indices = reader.read_uint16_list(self.header.num_indexes)
        reader.align(0x20)

        mesh_idx: int = 0
        for _ in range(self.header.num_mesh_parts):
            mesh: Mesh = self.meshes[mesh_idx]
            mesh_part: MeshPart = reader.read_struct(MeshPart)
            mesh_part.indices = indices[mesh_part.first_index_idx:mesh_part.first_index_idx + mesh_part.num_triangles * 3]

            mesh.parts.append(mesh_part)
            if len(mesh.parts) == mesh.mesh_header.num_parts:
                mesh_idx = mesh_idx + 1

        if reader.position != len(reader.data):
            raise Exception("Unread data remaining at end of file")

    def write(self, writer: BinaryWriter) -> None:
        self.header.signature = int.from_bytes(b"Mesh", "little")
        self.header.num_bone_mappings = Enumerable(self.meshes).select_many(lambda m: m.bone_indices).max(default_value = -1) + 1
        self.header.num_blend_shapes = len(self.meshes[0].blend_shapes)
        self.header.num_meshes = len(self.meshes)
        self.header.num_mesh_parts = Enumerable(self.meshes).sum(lambda m: len(m.parts))
        self.header.num_indexes = Enumerable(self.meshes).select_many(lambda m: m.parts).sum(lambda p: len(p.indices))
        
        if self.header.num_bone_mappings > 0:
            self.header.is_skinned = 1

        writer.write_struct(self.header)

        if self.header.data1_size != 0 or \
           self.header.data2_offset != 0xFFFFFFFF or \
           self.header.num_lod_levels != 0 or \
           self.header.data6_offset != 0:
            raise NotImplementedError()

        writer.write_int32_list(range(self.header.num_bone_mappings))
        writer.align(0x20)
        
        for mesh in self.meshes:
            mesh.write_header(writer)
        
        for mesh in self.meshes:
            mesh.write_bone_indices(writer)
        
        for mesh in self.meshes:
            mesh.write_content(writer)
        
        cumulative_index_count = 0
        for mesh in self.meshes:
            for mesh_part in mesh.parts:
                mesh_part.first_index_idx = cumulative_index_count
                mesh_part.num_triangles = len(mesh_part.indices) // 3
                writer.write_uint16_list(mesh_part.indices)
                
                cumulative_index_count += len(mesh_part.indices)
        writer.align(0x20)
        
        for mesh in self.meshes:
            for mesh_part in mesh.parts:
                writer.write_struct(mesh_part)