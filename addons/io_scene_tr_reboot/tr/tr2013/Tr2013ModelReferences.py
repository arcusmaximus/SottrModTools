from io_scene_tr_reboot.tr.ModelReferences import ModelReferences
from io_scene_tr_reboot.tr.ResourceBuilder import ResourceBuilder
from io_scene_tr_reboot.tr.ResourceKey import ResourceKey
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader
from io_scene_tr_reboot.tr.ResourceReference import ResourceReference

class Tr2013ModelReferences(ModelReferences):
    cloth_definition_ref: ResourceReference | None

    def __init__(self, model_data_id: int) -> None:
        super().__init__(model_data_id)
        self.cloth_definition_ref = None

    def read(self, reader: ResourceReader) -> None:
        self.model_data_resource = reader.read_ref()
        texture_refs_ref = reader.read_ref()
        material_refs_ref = reader.read_ref()
        self.cloth_definition_ref = reader.read_ref()

        if texture_refs_ref is not None:
            reader.seek(texture_refs_ref)
            self.texture_resources = self.read_ref_array(reader)

        if material_refs_ref is not None:
            reader.seek(material_refs_ref)
            self.material_resources = self.read_ref_array(reader)

    def read_ref_array(self, reader: ResourceReader) -> list[ResourceKey | None]:
        count = reader.read_int32()
        if reader.pointer_size == 8:
            reader.skip(4)

        resources: list[ResourceKey | None] = []
        for _ in range(count):
            resources.append(reader.read_ref())

        return resources

    def write(self, writer: ResourceBuilder) -> None:
        writer.write_ref(self.model_data_resource)
        texture_refs_ref = writer.write_internal_ref()
        material_refs_ref = writer.write_internal_ref()
        writer.write_ref(self.cloth_definition_ref)

        texture_refs_ref.offset = writer.position
        self.write_ref_array(writer, self.texture_resources)

        material_refs_ref.offset = writer.position
        self.write_ref_array(writer, self.material_resources)

    def write_ref_array(self, writer: ResourceBuilder, resources: list[ResourceKey | None]) -> None:
        writer.write_int32(len(resources))
        if writer.pointer_size == 8:
            writer.write_int32(0)

        for resource in resources:
            writer.write_ref(resource)
