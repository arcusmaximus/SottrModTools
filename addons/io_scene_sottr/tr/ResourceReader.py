from io_scene_sottr.tr.Enumerations import ResourceType
from io_scene_sottr.tr.ResourceKey import ResourceKey
from io_scene_sottr.tr.ResourceReference import ResourceReference
from io_scene_sottr.util.BinaryReader import BinaryReader
from io_scene_sottr.util.CStruct import CFloat, CStruct

class ResourceReader(BinaryReader):
    resource: ResourceKey
    references: dict[int, ResourceReference]
    resource_body_pos: int

    def __init__(self, resource: ResourceKey, data: bytes, has_references: bool) -> None:
        super().__init__(data)

        self.resource = resource
        self.references = {}
        if not has_references:
            return

        num_internal_refs = self.read_int32()
        num_wide_external_refs = self.read_int32()
        num_int_patches = self.read_int32()
        num_short_patches = self.read_int32()
        num_packed_external_refs = self.read_int32()

        self.resource_body_pos = self.position + num_internal_refs*8 + num_wide_external_refs*16 + num_int_patches*4 + num_short_patches*8 + num_packed_external_refs*4

        for _ in range(num_internal_refs):
            pointer_pos = self.resource_body_pos + self.read_int32()
            target_offset = self.read_int32()
            self.references[pointer_pos] = ResourceReference(resource.type, resource.id, target_offset)
        
        for _ in range(num_wide_external_refs):
            pointer_pos = self.resource_body_pos + self.read_int32()
            target_type = ResourceType(self.read_int32())
            target_id = self.read_int32()
            target_offset = self.read_int32()
            self.references[pointer_pos] = ResourceReference(target_type, target_id, target_offset)
        
        self.skip(num_int_patches * 4)
        self.skip(num_short_patches * 8)

        for _ in range(num_packed_external_refs):
            packed_pointer = self.read_uint32()
            target_type = ResourceType(packed_pointer >> 25)
            pointer_pos = self.resource_body_pos + (packed_pointer & 0x1FFFFFF) * 4

            prev_pos = self.position
            self.position = pointer_pos
            target_id = self.read_uint32() & 0x7FFFFFFF
            self.position = prev_pos

            self.references[pointer_pos] = ResourceReference(target_type, target_id, 0)
    
    def read_ref(self) -> ResourceReference | None:
        ref: ResourceReference | None = self.read_ref_at(0)
        self.skip(8)
        return ref
    
    def read_ref_at(self, offset: int) -> ResourceReference | None:
        return self.references.get(self.position + offset)

    def read_ref_list(self, count: int) -> list[ResourceReference | None]:
        refs: list[ResourceReference | None] = []
        for _ in range(count):
            refs.append(self.read_ref())
        
        return refs

    def seek(self, ref: ResourceReference) -> None:
        if ref.type != self.resource.type or ref.id != self.resource.id:
            raise Exception("Attempt to seek to an external resource")

        self.position = self.resource_body_pos + ref.offset

class CVec4(CStruct):
    x: CFloat
    y: CFloat
    z: CFloat
    w: CFloat
