from io_scene_sottr.tr.ResourceBuilder import ResourceBuilder
from io_scene_sottr.tr.ResourceReader import ResourceReader
from io_scene_sottr.tr.ResourceReference import ResourceReference
from io_scene_sottr.util.CStruct import CLong, CStruct, CStructTypeMapping

class _ResourceReferenceTypeMapping(CStructTypeMapping[ResourceReference | None, CLong]):
    def map_from_c(self, c_value: CLong, offset: int, context: object) -> ResourceReference | None:
        if not isinstance(context, ResourceReader):
            return None
        
        return context.references.get(context.position + offset)

    def map_to_c(self, mapped_value: ResourceReference | None, offset: int, context: object) -> CLong:
        if not isinstance(context, ResourceBuilder) or mapped_value is None:
            return 0
        
        context.add_ref(context.position + offset, mapped_value)
        return mapped_value.id

class Tr11CStructTypeMappings:
    @staticmethod
    def register():
        CStruct.register_type_mappings(
            _ResourceReferenceTypeMapping()
        )
