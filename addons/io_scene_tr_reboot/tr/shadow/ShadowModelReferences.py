from io_scene_tr_reboot.tr.ModelReferences import ModelReferences
from io_scene_tr_reboot.tr.ResourceBuilder import ResourceBuilder
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader

class ShadowModelReferences(ModelReferences):
    def read(self, reader: ResourceReader) -> None:
        self.model_data_resource = reader.read_ref()
        texture_refs_ref = reader.read_ref()
        material_refs_ref = reader.read_ref()

        if texture_refs_ref is not None:
            reader.seek(texture_refs_ref)
            reader.read_ref()
            while reader.position < len(reader.data) and (material_refs_ref is None or reader.position < reader.resource_body_pos + material_refs_ref.offset):
                self.texture_resources.append(reader.read_ref())
        
        if material_refs_ref is not None:
            reader.seek(material_refs_ref)
            reader.read_ref()
            while reader.position < len(reader.data):
                self.material_resources.append(reader.read_ref())

    def write(self, writer: ResourceBuilder) -> None:
        writer.write_ref(self.model_data_resource)
        texture_refs_ref = writer.write_internal_ref()
        material_refs_ref = writer.write_internal_ref()

        texture_refs_ref.offset = writer.position
        writer.write_ref(None)
        for texture_resource in self.texture_resources:
            writer.write_ref(texture_resource)
        
        material_refs_ref.offset = writer.position
        writer.write_ref(None)
        for material_resource in self.material_resources:
            writer.write_ref(material_resource)
