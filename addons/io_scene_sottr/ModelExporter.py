from array import array
import random
from typing import Iterable, NamedTuple, Sequence, cast
import bpy
import os
from mathutils import Vector
from io_scene_sottr.BlenderHelper import BlenderHelper
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.tr.BlendShape import BlendShape
from io_scene_sottr.tr.Enumerations import ResourceType
from io_scene_sottr.tr.Hashes import Hashes
from io_scene_sottr.tr.Mesh import Mesh
from io_scene_sottr.tr.MeshPart import MeshPart
from io_scene_sottr.tr.Model import Model
from io_scene_sottr.tr.ModelData import ModelData
from io_scene_sottr.tr.ResourceBuilder import ResourceBuilder
from io_scene_sottr.tr.ResourceKey import ResourceKey
from io_scene_sottr.tr.Vertex import Vertex
from io_scene_sottr.tr.VertexFormat import VertexFormat
from io_scene_sottr.tr.VertexOffsets import VertexOffsets
from io_scene_sottr.util.BinaryWriter import BinaryWriter
from io_scene_sottr.util.Enumerable import Enumerable
from io_scene_sottr.util.SlotsBase import SlotsBase

class _BlenderMeshMaps(NamedTuple):
    color_maps: dict[int, bpy.types.ByteColorAttribute]
    uv_maps: dict[int, bpy.types.MeshUVLoopLayer]
    vertex_groups: dict[int, bpy.types.VertexGroup]

class _VertexWeight:
    bone_id: int
    weight: int

    def __init__(self, bone_id: int, weight: int) -> None:
        self.bone_id = bone_id
        self.weight = weight

class ModelExporter(SlotsBase):
    scale_factor: float
    
    def __init__(self, scale_factor: float) -> None:
        self.scale_factor = scale_factor
    
    def export_model(self, folder_path: str, model_id: int, model_data_id: int, bl_objs: list[bpy.types.Object]) -> None:
        if bpy.context.object:
            bpy.ops.object.mode_set(mode = "OBJECT")            # type: ignore
        
        tr_model = self.create_model(model_id, model_data_id, bl_objs)
        tr_model_data = self.create_model_data(tr_model, bl_objs)

        model_file_path = os.path.join(folder_path, f"{model_id}.tr11model")
        with open(model_file_path, "wb") as model_file:
            model_resource_builder = ResourceBuilder(ResourceKey(ResourceType.MODEL, model_id))
            tr_model.write(model_resource_builder)
            model_file.write(model_resource_builder.build())
        
        model_data_file_path = os.path.join(folder_path, f"{model_data_id}.tr11modeldata")
        with open(model_data_file_path, "wb") as model_data_file:
            tr_model_data.write(BinaryWriter(model_data_file))
    
    def create_model(self, model_id: int, model_data_id: int, bl_objs: list[bpy.types.Object]) -> Model:
        tr_model = Model(model_id)
        tr_model.model_data_resource = ResourceKey(ResourceType.MODEL, model_data_id)
        tr_model.material_resources = Enumerable(bl_objs).select(lambda o: o.data)                                          \
                                                         .cast(bpy.types.Mesh)                                              \
                                                         .select_many(lambda m: m.materials)                                \
                                                         .where(lambda m: cast(bpy.types.Material | None, m) is not None)   \
                                                         .select(lambda m: BlenderNaming.parse_material_name(m.name))       \
                                                         .distinct()                                                        \
                                                         .select(lambda i: ResourceKey(ResourceType.MATERIAL, i))           \
                                                         .cast(ResourceKey | None)                                          \
                                                         .to_list()
        return tr_model
    
    def create_model_data(self, tr_model: Model, bl_objs: list[bpy.types.Object]) -> ModelData:
        tr_model_data = ModelData(cast(ResourceKey, tr_model.model_data_resource).id)
        tr_model_data.header.flags = 0xE01
        
        bl_shape_keys = Enumerable(bl_objs).select(lambda o: o.data)        \
                                           .cast(bpy.types.Mesh)            \
                                           .select_many(lambda m: (m.shape_keys and Enumerable(m.shape_keys.key_blocks).skip(1) or []))
        if bl_shape_keys.any():
            tr_model_data.header.has_blend_shapes = True
            tr_model_data.header.num_blend_shapes = bl_shape_keys.max(lambda bl_shape_key: BlenderNaming.parse_shape_key_name(bl_shape_key.name).local_id) + 1
        
        for bl_obj in bl_objs:
            tr_model_data.meshes.append(self.create_mesh(tr_model, tr_model_data, bl_obj))
        
        self.unsign_normals(tr_model_data)
        self.calc_bounding_box(tr_model_data)
        return tr_model_data
    
    def create_mesh(self, tr_model: Model, tr_model_data: ModelData, bl_obj: bpy.types.Object) -> Mesh:
        with BlenderHelper.prepare_for_model_export(bl_obj):
            if not Enumerable(bl_obj.modifiers).of_type(bpy.types.TriangulateModifier).any():
                bl_obj.modifiers.new("Triangulate", "TRIANGULATE")

            bl_mesh = self.get_evaluated_bl_mesh(bl_obj)
            bl_mesh.calc_normals_split()

            bl_mesh_maps = _BlenderMeshMaps(
                self.collect_bl_color_maps(bl_mesh),
                self.collect_bl_uv_maps(bl_mesh),
                self.collect_bl_vertex_groups(bl_obj)
            )

            tr_mesh = Mesh(tr_model_data.header)
            tr_mesh.bone_indices = list(bl_mesh_maps.vertex_groups.keys())
            use_16bit_skin_indices = len(tr_mesh.bone_indices) - 1 > 0xFF

            self.populate_vertex_format(tr_mesh.vertex_format, bl_mesh_maps)
            bl_corner_to_tr_vertex = self.create_vertices(tr_mesh, bl_mesh, bl_mesh_maps, use_16bit_skin_indices)
            self.create_mesh_parts(tr_model, tr_mesh, bl_mesh, bl_corner_to_tr_vertex, use_16bit_skin_indices)
            self.create_blend_shapes(tr_model_data, tr_mesh, bl_obj, bl_mesh, bl_corner_to_tr_vertex)
            self.shrink_uvs(tr_mesh, bl_mesh_maps)

            return tr_mesh

    def collect_bl_color_maps(self, bl_mesh: bpy.types.Mesh) -> dict[int, bpy.types.ByteColorAttribute]:
        attr_name_hashes = [Hashes.color1, Hashes.color2]
        if len(bl_mesh.color_attributes) > len(attr_name_hashes):
            raise Exception(f"Mesh {bl_mesh.name} has more than {len(attr_name_hashes)} color attributes, which is not supported.")
        
        bl_color_maps: dict[int, bpy.types.ByteColorAttribute] = {}
        for i, bl_color_map in enumerate(bl_mesh.color_attributes):
            if not isinstance(bl_color_map, bpy.types.ByteColorAttribute):
                raise Exception(f"Color attribute {i} in mesh {bl_mesh.name} must use the Byte Color format. Please convert or delete it.")
            
            if bl_color_map.domain != "POINT":
                raise Exception(f"Color attribute {bl_color_map.name} in mesh {bl_mesh.name} must use the Vertex domain. Please convert or delete it.")
            
            bl_color_maps[attr_name_hashes[i]] = bl_color_map
        
        return bl_color_maps
    
    def collect_bl_uv_maps(self, bl_mesh: bpy.types.Mesh) -> dict[int, bpy.types.MeshUVLoopLayer]:
        attr_name_hashes = [Hashes.texcoord1, Hashes.texcoord2, Hashes.texcoord3, Hashes.texcoord4]
        if len(bl_mesh.uv_layers) > len(attr_name_hashes):
            raise Exception(f"Mesh {bl_mesh.name} has more than {len(attr_name_hashes)} UV maps, which is not supported.")

        bl_uv_maps: dict[int, bpy.types.MeshUVLoopLayer] = {}
        for i, bl_uv_map in enumerate(bl_mesh.uv_layers):
            bl_uv_maps[attr_name_hashes[i]] = bl_uv_map

        return bl_uv_maps
    
    def collect_bl_vertex_groups(self, bl_obj: bpy.types.Object) -> dict[int, bpy.types.VertexGroup]:
        return Enumerable(bl_obj.vertex_groups).to_dict(lambda g: BlenderNaming.get_bone_local_id(g.name))
    
    def populate_vertex_format(self, tr_vertex_format: VertexFormat, bl_mesh_maps: _BlenderMeshMaps) -> None:
        tr_vertex_format.hash = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        tr_vertex_format.add_attribute(Hashes.position, 2, 0)
        tr_vertex_format.add_attribute(Hashes.normal, 5, 1)
        tr_vertex_format.add_attribute(Hashes.binormal, 5, 1)
        tr_vertex_format.add_attribute(Hashes.tangent, 5, 1)

        for attr_name_hash in bl_mesh_maps.color_maps.keys():
            tr_vertex_format.add_attribute(attr_name_hash, 4, 1)

        for attr_name_hash in bl_mesh_maps.uv_maps.keys():
            tr_vertex_format.add_attribute(attr_name_hash, 25, 1)
        
        if len(bl_mesh_maps.vertex_groups) > 0:
            tr_vertex_format.add_attribute(Hashes.skin_weights, 24, 1)
            tr_vertex_format.add_attribute(Hashes.skin_indices, 11, 1)

    def create_vertices(self, tr_mesh: Mesh, bl_mesh: bpy.types.Mesh, bl_mesh_maps: _BlenderMeshMaps, use_16bit_skin_indices: bool) -> list[int]:
        bl_vertex_to_tr_vertices: list[list[int] | None] = [None] * len(bl_mesh.vertices)
        bl_corner_to_tr_vertex: list[int] = [-1] * len(bl_mesh.loops)
        for bl_corner_idx, bl_corner in enumerate(bl_mesh.loops):
            bl_vertex_idx = bl_corner.vertex_index
            tr_vertex_idxs = bl_vertex_to_tr_vertices[bl_vertex_idx]
            if tr_vertex_idxs is None:
                tr_vertex_idxs = []
                bl_vertex_to_tr_vertices[bl_vertex_idx] = tr_vertex_idxs

            tr_vertex_idx = -1
            for existing_tr_vertex_idx in tr_vertex_idxs:
                if self.can_reuse_tr_vertex_for_bl_corner(tr_mesh.vertices[existing_tr_vertex_idx], bl_mesh, bl_mesh_maps, bl_corner_idx):
                    tr_vertex_idx = existing_tr_vertex_idx
                    break
            
            if tr_vertex_idx < 0:
                tr_mesh.vertices.append(self.create_vertex(bl_mesh, bl_mesh_maps, bl_corner_idx, use_16bit_skin_indices))
                tr_vertex_idx = len(tr_mesh.vertices) - 1
                tr_vertex_idxs.append(tr_vertex_idx)
            
            bl_corner_to_tr_vertex[bl_corner_idx] = tr_vertex_idx

        return bl_corner_to_tr_vertex
    
    def can_reuse_tr_vertex_for_bl_corner(self, tr_vertex: Vertex, bl_mesh: bpy.types.Mesh, bl_mesh_maps: _BlenderMeshMaps, bl_corner_idx: int) -> bool:
        bl_corner = bl_mesh.loops[bl_corner_idx]
        
        if not self.are_vectors_equal(tr_vertex.attributes[Hashes.normal], cast(Vector, bl_corner.normal)):
            return False
        
        for attr_name_hash, bl_uv_map in bl_mesh_maps.uv_maps.items():
            if not self.are_vectors_equal(tr_vertex.attributes[attr_name_hash], cast(Vector, bl_uv_map.data[bl_corner_idx].uv)):
                return False

        return True

    def create_vertex(self, bl_mesh: bpy.types.Mesh, bl_mesh_maps: _BlenderMeshMaps, bl_corner_idx: int, use_16bit_skin_indices: bool) -> Vertex:
        bl_corner = bl_mesh.loops[bl_corner_idx]
        bl_vertex_idx = bl_corner.vertex_index
        bl_vertex = bl_mesh.vertices[bl_vertex_idx]
        
        tr_vertex = Vertex()
        tr_vertex.attributes[Hashes.position] = cast(tuple[float, ...], cast(Vector, bl_vertex.co) / self.scale_factor)
        tr_vertex.attributes[Hashes.normal]   = cast(tuple[float, ...], cast(Vector, bl_corner.normal).copy())
        tr_vertex.attributes[Hashes.tangent]  = cast(tuple[float, ...], cast(Vector, bl_corner.tangent).copy())
        tr_vertex.attributes[Hashes.binormal] = cast(tuple[float, ...], cast(Vector, bl_corner.bitangent).copy())

        for attr_name_hash, bl_color_map in bl_mesh_maps.color_maps.items():
            tr_vertex.attributes[attr_name_hash] = tuple(cast(Sequence[float], bl_color_map.data[bl_vertex_idx].color))
        
        for attr_name_hash, bl_uv_map in bl_mesh_maps.uv_maps.items():
            uv_coord = cast(Vector, bl_uv_map.data[bl_corner_idx].uv)
            if abs(uv_coord.x) > 15 or abs(uv_coord.y) > 15:
                raise Exception(f"Mesh {bl_mesh.name} has out-of-bounds UV coordinates. Please check and fix UV map {bl_uv_map.name}.")
            
            tr_vertex.attributes[attr_name_hash] = cast(tuple[float, ...], uv_coord.copy())

        if len(bl_mesh_maps.vertex_groups) == 0:
            return tr_vertex

        skin_index_count = use_16bit_skin_indices and 4 or 8
        skin_index_shift = use_16bit_skin_indices and 16 or 8

        vertex_weights = Enumerable(bl_vertex.groups).select(lambda w: _VertexWeight(w.group, int(w.weight * 255))) \
                                                     .where(lambda w: w.weight > 0)                                 \
                                                     .order_by_descending(lambda w: w.weight)                       \
                                                     .take(skin_index_count)                                        \
                                                     .to_list()

        if len(vertex_weights) > 0:
            weight_sum = Enumerable(vertex_weights).sum(lambda w: w.weight)
            vertex_weights[0].weight += 255 - weight_sum

        skin_indices = [0, 0, 0, 0]
        skin_weights = [0, 0, 0, 0]
        weight_idx = 0

        for bl_vertex_weight in vertex_weights:
            skin_indices[weight_idx % 4] |= bl_vertex_weight.bone_id << (skin_index_shift * (weight_idx // 4))
            skin_weights[weight_idx % 4] |= bl_vertex_weight.weight  << (8 * (weight_idx // 4))
            weight_idx += 1
        
        tr_vertex.attributes[Hashes.skin_indices] = tuple(skin_indices)
        tr_vertex.attributes[Hashes.skin_weights] = tuple(skin_weights)

        return tr_vertex

    def create_mesh_parts(self, tr_model: Model, tr_mesh: Mesh, bl_mesh: bpy.types.Mesh, bl_corner_to_tr_vertex: list[int], use_16bit_skin_indices: bool) -> None:
        if len(bl_mesh.materials) == 0:
            raise Exception(f"Mesh {bl_mesh.name} has no materials assigned.")
        
        bl_faces_by_material_idx: dict[int, list[bpy.types.MeshPolygon]] = Enumerable(bl_mesh.polygons).group_by(lambda p: p.material_index)
        for bl_material_idx, bl_faces in bl_faces_by_material_idx.items():
            bl_material = cast(bpy.types.Material | None, bl_mesh.materials[bl_material_idx])
            if bl_material is None:
                raise Exception(f"Mesh {bl_mesh.name} has faces referencing an empty material slot.")

            tr_material_id = BlenderNaming.parse_material_name(bl_material.name)

            tr_mesh_part = MeshPart()
            tr_mesh_part.field_0 = Vector()
            tr_mesh_part.flags = 0x40030
            tr_mesh_part.has_8_weights_per_vertex = not use_16bit_skin_indices
            tr_mesh_part.has_16bit_skin_indices = use_16bit_skin_indices

            tr_mesh_part.material_idx = Enumerable(tr_model.material_resources).index_of(lambda m: m is not None and m.id == tr_material_id)
            for i in range(len(tr_mesh_part.texture_indices)):
                tr_mesh_part.texture_indices[i] = 0xFFFFFFFF

            tr_mesh_part.indices = array("H", [0]) * (len(bl_faces) * 3)
            index_idx = 0
            for bl_face in bl_faces:
                if bl_face.loop_total != 3:
                    raise Exception(f"Mesh {bl_mesh.name} contains non-triangular faces.")

                for bl_corner_idx in cast(Iterable[int], bl_face.loop_indices):
                    tr_mesh_part.indices[index_idx] = bl_corner_to_tr_vertex[bl_corner_idx]
                    index_idx += 1
            
            tr_mesh.parts.append(tr_mesh_part)

    def create_blend_shapes(self, tr_model_data: ModelData, tr_mesh: Mesh, bl_obj: bpy.types.Object, bl_mesh: bpy.types.Mesh, bl_corner_to_tr_vertex: list[int]) -> None:
        tr_mesh.blend_shapes = [None] * tr_model_data.header.num_blend_shapes
        if cast(bpy.types.Key | None, bl_mesh.shape_keys) is None:
            return
        
        tr_vertex_to_bl_corner: list[int] = [-1] * len(tr_mesh.vertices)
        for bl_corner_idx, tr_vertex_idx in enumerate(bl_corner_to_tr_vertex):
            tr_vertex_to_bl_corner[tr_vertex_idx] = bl_corner_idx
        
        base_vertex_positions = [0] * (len(bl_mesh.vertices) * 3)
        bl_mesh.vertices.foreach_get("co", base_vertex_positions)      # type: ignore
        
        base_corner_normals = [0] * (len(bl_mesh.loops) * 3)
        bl_mesh.loops.foreach_get("normal", base_corner_normals)       # type: ignore

        shape_vertex_positions = [0] * (len(bl_mesh.vertices) * 3)
        shape_corner_normals = [0] * (len(bl_mesh.loops) * 3)
        
        bl_obj.show_only_shape_key = True
        cast(bpy.types.Mesh, bl_obj.data).use_auto_smooth = False
        color_offset = Vector((0.0, 0.0, 0.4, 0.0))                         # Z component = normal blending suppression strength
        for bl_shape_key_idx in range(1, len(bl_mesh.shape_keys.key_blocks)):
            bl_obj.active_shape_key_index = bl_shape_key_idx
            tr_blend_shape_idx = BlenderNaming.parse_shape_key_name(bl_obj.active_shape_key.name).local_id

            bl_mesh = self.get_evaluated_bl_mesh(bl_obj)
            bl_mesh.calc_normals_split()
            bl_mesh.vertices.foreach_get("co", shape_vertex_positions)      # type: ignore
            bl_mesh.loops.foreach_get("normal", shape_corner_normals)       # type: ignore
            
            tr_blend_shape = BlendShape()
            for tr_vertex_idx, bl_corner_idx in enumerate(tr_vertex_to_bl_corner):
                bl_vertex_idx = bl_mesh.loops[bl_corner_idx].vertex_index
                
                base_position = (
                    base_vertex_positions[3 * bl_vertex_idx + 0],
                    base_vertex_positions[3 * bl_vertex_idx + 1],
                    base_vertex_positions[3 * bl_vertex_idx + 2]
                )
                base_normal = (
                    base_corner_normals[3 * bl_corner_idx + 0],
                    base_corner_normals[3 * bl_corner_idx + 1],
                    base_corner_normals[3 * bl_corner_idx + 2]
                )
                bl_shape_vertex = bl_mesh.vertices[bl_vertex_idx]
                bl_shape_corner = bl_mesh.loops[bl_corner_idx]

                if self.are_vectors_equal(base_position, cast(Vector, bl_shape_vertex.co)) and \
                   self.are_vectors_equal(base_normal,   cast(Vector, bl_shape_corner.normal)):
                    continue

                bl_shape_corner = bl_mesh.loops[bl_corner_idx]
                tr_blend_shape.vertices[tr_vertex_idx] = VertexOffsets(
                    (cast(Vector, bl_shape_vertex.co) - Vector(base_position)) / self.scale_factor,
                    cast(Vector, bl_shape_corner.normal) - Vector(base_normal),
                    color_offset
                )

            if len(tr_blend_shape.vertices) > 0:
                tr_mesh.blend_shapes[tr_blend_shape_idx] = tr_blend_shape
        
        bl_obj.show_only_shape_key = False

    def are_vectors_equal(self, a: Vector | tuple[float, ...], b: Vector | tuple[float, ...]) -> bool:
        for i in range(len(a)):
            if abs(a[i] - b[i]) > 0.0001:
                return False
        
        return True
    
    def unsign_normals(self, tr_model_data: ModelData) -> None:
        for tr_mesh in tr_model_data.meshes:
            for tr_vertex in tr_mesh.vertices:
                self.unsign_vector(tr_vertex, Hashes.normal)
                self.unsign_vector(tr_vertex, Hashes.tangent)
                self.unsign_vector(tr_vertex, Hashes.binormal)
    
    def unsign_vector(self, tr_vertex: Vertex, attr_name_hash: int) -> None:
        vector = tr_vertex.attributes[attr_name_hash]
        tr_vertex.attributes[attr_name_hash] = (
                                                   (vector[0] + 1.0) / 2.0,
                                                   (vector[1] + 1.0) / 2.0,
                                                   (vector[2] + 1.0) / 2.0,
                                                   0.0
                                               )
    
    def shrink_uvs(self, tr_mesh: Mesh, bl_mesh_maps: _BlenderMeshMaps) -> None:
        for tr_vertex in tr_mesh.vertices:
            for attr_name_hash in bl_mesh_maps.uv_maps:
                vector = tr_vertex.attributes[attr_name_hash]
                tr_vertex.attributes[attr_name_hash] = (vector[0] / 16.0, (1 - vector[1]) / 16.0)
    
    def calc_bounding_box(self, tr_model_data: ModelData) -> None:
        x_min: float = 0.0
        y_min: float = 0.0
        z_min: float = 0.0

        x_max: float = 0.0
        y_max: float = 0.0
        z_max: float = 0.0
        
        first: bool = True

        for tr_mesh in tr_model_data.meshes:
            for tr_vertex in tr_mesh.vertices:
                position = tr_vertex.attributes[Hashes.position]
                if first:
                    (x_min, y_min, z_min) = position
                    (x_max, y_max, z_max) = position
                    first = False
                else:
                    x_min = min(x_min, position[0])
                    y_min = min(y_min, position[1])
                    z_min = min(z_min, position[2])

                    x_max = max(x_max, position[0])
                    y_max = max(y_max, position[1])
                    z_max = max(z_max, position[2])
        
        tr_model_data.header.bound_box_min = Vector((x_min, y_min, z_min))
        tr_model_data.header.bound_box_max = Vector((x_max, y_max, z_max))

    def get_evaluated_bl_mesh(self, bl_obj: bpy.types.Object) -> bpy.types.Mesh:
        bl_obj_eval = cast(bpy.types.Object, bl_obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bl_mesh_eval = cast(bpy.types.Mesh, bl_obj_eval.data)
        return bl_mesh_eval
