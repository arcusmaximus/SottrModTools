from io import BytesIO
from typing import cast
from io_scene_sottr.tr.ResourceKey import ResourceKey
from io_scene_sottr.tr.ResourceReference import ResourceReference
from io_scene_sottr.util.BinaryWriter import BinaryWriter

class ResourceBuilder(BinaryWriter):
    resource: ResourceKey
    references: dict[int, ResourceReference]
    
    def __init__(self, resource: ResourceKey) -> None:
        super().__init__(BytesIO())
        self.resource = resource
        self.references = {}
    
    def add_ref(self, offset: int, ref: ResourceReference) -> None:
        self.references[offset] = ref

    def write_local_ref(self, offset: int = -1) -> ResourceReference:
        ref = ResourceReference(self.resource.type, self.resource.id, offset)
        self.write_ref(ref)
        return ref
    
    def write_ref(self, ref: ResourceKey | ResourceReference | None) -> None:
        if ref is None:
            self.write_uint64(0)
            return
        
        if not isinstance(ref, ResourceReference):
            ref = ResourceReference(ref.type, ref.id, 0)
        
        self.add_ref(self.position, ref)
        self.write_uint64(ref.id)    
    
    def build(self) -> memoryview:
        internal_refs: dict[int, ResourceReference] = {}
        external_refs: dict[int, ResourceReference] = {}
        for offset, ref in self.references.items():
            if ref.type == self.resource.type and ref.id == self.resource.id:
                internal_refs[offset] = ref
            else:
                external_refs[offset] = ref
        
        result = BytesIO()
        result_writer = BinaryWriter(result)
        result_writer.write_int32(len(internal_refs))
        result_writer.write_int32(0)
        result_writer.write_int32(0)
        result_writer.write_int32(0)
        result_writer.write_int32(len(external_refs))

        for offset, ref in internal_refs.items():
            result_writer.write_int32(offset)
            result_writer.write_int32(ref.offset)
        
        for offset, ref in external_refs.items():
            result_writer.write_uint32((ref.type << 25) | (offset // 4))
        
        result_writer.write_bytes(cast(BytesIO, self.stream).getbuffer())
        return result.getbuffer()
