from mathutils import Matrix, Quaternion, Vector
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

class CMatrix(CStruct):
    m00: CFloat
    m01: CFloat
    m02: CFloat
    m03: CFloat

    m10: CFloat
    m11: CFloat
    m12: CFloat
    m13: CFloat

    m20: CFloat
    m21: CFloat
    m22: CFloat
    m23: CFloat

    m30: CFloat
    m31: CFloat
    m32: CFloat
    m33: CFloat

class _VectorTypeMapping(CStructTypeMapping[Vector, CVec4]):
    def map_from_c(self, c_value: CVec4, offset: int, context: object) -> Vector:
        return Vector((c_value.x, c_value.y, c_value.z))
    
    def map_to_c(self, mapped_value: Vector, offset: int, context: object) -> CVec4:
        vec = CVec4()
        vec.x = mapped_value.x
        vec.y = mapped_value.y
        vec.z = mapped_value.z
        vec.w = 0.0
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

class _MatrixTypeMapping(CStructTypeMapping[Matrix, CMatrix]):
    def map_from_c(self, c_value: CMatrix, offset: int, context: object) -> Matrix:
        return Matrix(((c_value.m00, c_value.m10, c_value.m20, c_value.m30),
                       (c_value.m01, c_value.m11, c_value.m21, c_value.m31),
                       (c_value.m02, c_value.m12, c_value.m22, c_value.m32),
                       (c_value.m03, c_value.m13, c_value.m23, c_value.m33)))
    
    def map_to_c(self, mapped_value: Matrix, offset: int, context: object) -> CMatrix:
        matrix = CMatrix()
        matrix.m00 = mapped_value[0][0]
        matrix.m01 = mapped_value[1][0]
        matrix.m02 = mapped_value[2][0]
        matrix.m03 = mapped_value[3][0]

        matrix.m10 = mapped_value[0][1]
        matrix.m11 = mapped_value[1][1]
        matrix.m12 = mapped_value[2][1]
        matrix.m13 = mapped_value[3][1]

        matrix.m20 = mapped_value[0][2]
        matrix.m21 = mapped_value[1][2]
        matrix.m22 = mapped_value[2][2]
        matrix.m23 = mapped_value[3][2]

        matrix.m30 = mapped_value[0][3]
        matrix.m31 = mapped_value[1][3]
        matrix.m32 = mapped_value[2][3]
        matrix.m33 = mapped_value[3][3]
        return matrix

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
            _MatrixTypeMapping(),
            _ResourceReferenceTypeMapping()
        )
