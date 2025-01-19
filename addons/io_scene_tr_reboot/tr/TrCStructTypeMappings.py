from io_scene_tr_reboot.tr.ResourceBuilder import ResourceBuilder
from io_scene_tr_reboot.tr.ResourceReader import ResourceReader
from io_scene_tr_reboot.tr.ResourceReference import ResourceReference
from io_scene_tr_reboot.util.CStruct import CInt, CLong, CStruct32, CStruct64, CStructTypeMapping

def _map_from_c(offset: int, context: object) -> ResourceReference | None:
    if not isinstance(context, ResourceReader):
        return None

    return context.references.get(context.position + offset)

def _map_to_c(mapped_value: ResourceReference | None, offset: int, context: object) -> int:
    if not isinstance(context, ResourceBuilder) or mapped_value is None:
        return 0

    context.add_ref(context.position + offset, mapped_value)
    return mapped_value.id

class _ResourceReference32TypeMapping(CStructTypeMapping[ResourceReference | None, CInt]):
    def map_from_c(self, c_value: CInt, offset: int, context: object) -> ResourceReference | None:
        return _map_from_c(offset, context)

    def map_to_c(self, mapped_value: ResourceReference | None, offset: int, context: object) -> CInt:
        return _map_to_c(mapped_value, offset, context)

class _ResourceReference64TypeMapping(CStructTypeMapping[ResourceReference | None, CLong]):
    def map_from_c(self, c_value: CLong, offset: int, context: object) -> ResourceReference | None:
        return _map_from_c(offset, context)

    def map_to_c(self, mapped_value: ResourceReference | None, offset: int, context: object) -> CLong:
        return _map_to_c(mapped_value, offset, context)

class TrCStructTypeMappings:
    @staticmethod
    def register():
        CStruct32.register_type_mappings(_ResourceReference32TypeMapping())
        CStruct64.register_type_mappings(_ResourceReference64TypeMapping())
