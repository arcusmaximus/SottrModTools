from io_scene_sottr.tr.ResourceBuilder import ResourceBuilder
from io_scene_sottr.tr.ResourceKey import ResourceKey
from io_scene_sottr.tr.ResourceReader import ResourceReader
from io_scene_sottr.util.SlotsBase import SlotsBase

class Model(SlotsBase):
    id: int
    model_data_resource: ResourceKey | None
    texture_resources: list[ResourceKey | None]
    material_resources: list[ResourceKey | None]

    def __init__(self, id: int) -> None:
        self.id = id
        self.model_data_resource = None
        self.texture_resources = []
        self.material_resources = []
    
    def read(self, reader: ResourceReader) -> None:
        self.model_data_resource = reader.read_ref()
        texture_refs_ref = reader.read_ref()
        material_refs_ref = reader.read_ref()

        if texture_refs_ref is not None:
            reader.seek(texture_refs_ref)
            reader.skip(8)
            while reader.position < len(reader.data) and (material_refs_ref is None or reader.position < reader.resource_body_pos + material_refs_ref.offset):
                self.texture_resources.append(reader.read_ref())
        
        if material_refs_ref is not None:
            reader.seek(material_refs_ref)
            reader.skip(8)
            while reader.position < len(reader.data):
                self.material_resources.append(reader.read_ref())

    def write(self, writer: ResourceBuilder) -> None:
        writer.write_ref(self.model_data_resource)
        texture_refs_ref = writer.write_local_ref()
        material_refs_ref = writer.write_local_ref()

        texture_refs_ref.offset = writer.position
        writer.write_uint64(0)
        for texture_resource in self.texture_resources:
            writer.write_ref(texture_resource)
        
        material_refs_ref.offset = writer.position
        writer.write_uint64(0)
        for material_resource in self.material_resources:
            writer.write_ref(material_resource)
