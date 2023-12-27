from mathutils import Quaternion, Vector
from io_scene_sottr.tr.ResourceBuilder import ResourceBuilder
from io_scene_sottr.tr.ResourceReader import ResourceReader
from io_scene_sottr.tr.ResourceReference import ResourceReference
from io_scene_sottr.util.CStruct import CFloat, CLong, CStruct, CStructTypeMapping

class CVec3(CStruct):
    x: CFloat
    y: CFloat
    z: CFloat

class CVec4(CStruct):
    x: CFloat
    y: CFloat
    z: CFloat
    w: CFloat

class _VectorTypeMapping(CStructTypeMapping[Vector, CVec4]):
    def map_from_c(self, c_value: CVec4, offset: int, context: object) -> Vector:
        return Vector((c_value.x, c_value.y, c_value.z))
    
    def map_to_c(self, mapped_value: Vector, offset: int, context: object) -> CVec4:
        vec = CVec4()
        vec.x = mapped_value.x
        vec.y = mapped_value.y
        vec.z = mapped_value.z
        vec.w = 1.0
        return vec

class _QuaterionTypeMapping(CStructTypeMapping[Quaternion, CVec4]):
    def map_from_c(self, c_value: CVec4, offset: int, context: object) -> Quaternion:
        return Quaternion((c_value.w, c_value.x, c_value.y, c_value.z))
    
    def map_to_c(self, mapped_value: Quaternion, offset: int, context: object) -> CVec4:
        vec = CVec4()
        vec.w = mapped_value.w
        vec.x = mapped_value.x
        vec.y = mapped_value.y
        vec.z = mapped_value.z
        return vec

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

class CStructTypeMappings:
    @staticmethod
    def register():
        CStruct.register_type_mappings(
            _VectorTypeMapping(),
            _QuaterionTypeMapping(),
            _ResourceReferenceTypeMapping()
        )
