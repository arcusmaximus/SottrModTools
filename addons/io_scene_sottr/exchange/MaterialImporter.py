from typing import NamedTuple, cast
import bpy
import os
from io_scene_sottr.BlenderNaming import BlenderNaming
from io_scene_sottr.tr.Collection import Collection
from io_scene_sottr.tr.Material import Material
from io_scene_sottr.tr.ResourceKey import ResourceKey
from io_scene_sottr.util.DdsFile import DdsFile, DdsType
from io_scene_sottr.util.SlotsBase import SlotsBase

class _TextureNodeSet(NamedTuple):
    diffuse: bpy.types.ShaderNodeTexImage | None
    normal:  bpy.types.ShaderNodeTexImage | None

class MaterialImporter(SlotsBase):
    def import_material(self, tr_collection: Collection, material_resource: ResourceKey) -> bpy.types.Material | None:
        material_name = BlenderNaming.make_material_name(material_resource.id)
        
        bl_material = cast(bpy.types.Material | None, bpy.data.materials.get(material_name))
        if bl_material is not None:
            return bl_material
        
        tr_material = tr_collection.get_material(material_resource)
        if tr_material is None:
            return None
        
        bl_material = self.__create_empty_material(material_name)

        bl_texture_nodes = self.__add_texture_nodes(bl_material, tr_collection, tr_material)
        
        bl_transparent_node = bl_material.node_tree.nodes.new("ShaderNodeBsdfTransparent")
        bl_transparent_node.location = (300, 0)
        
        bl_diffuse_shader_node = bl_material.node_tree.nodes.new("ShaderNodeBsdfDiffuse")
        bl_diffuse_shader_node.location = (300, -100)

        if bl_texture_nodes.diffuse is not None:
            bl_material.node_tree.links.new(bl_texture_nodes.diffuse.outputs[0], bl_diffuse_shader_node.inputs[0])

        bl_transparent_node.width = max(bl_transparent_node.width, bl_diffuse_shader_node.width)
        bl_diffuse_shader_node.width = bl_transparent_node.width

        bl_normal_node: bpy.types.Node | None = None
        if bl_texture_nodes.normal is not None:
            bl_normal_node = bl_material.node_tree.nodes.new("ShaderNodeNormalMap")
            bl_normal_node.location = (300, -250)
            cast(bpy.types.NodeSocketFloat, bl_normal_node.inputs[0]).default_value = 0.5
            bl_material.node_tree.links.new(bl_texture_nodes.normal.outputs[0], bl_normal_node.inputs[1])
            bl_material.node_tree.links.new(bl_normal_node.outputs[0], bl_diffuse_shader_node.inputs[2])

        bl_mix_node = bl_material.node_tree.nodes.new("ShaderNodeMixShader")
        bl_mix_node.location = (500, 0)
        bl_material.node_tree.links.new(bl_transparent_node.outputs[0], bl_mix_node.inputs[1])
        bl_material.node_tree.links.new(bl_diffuse_shader_node.outputs[0], bl_mix_node.inputs[2])
        if bl_texture_nodes.diffuse is not None:
            bl_material.node_tree.links.new(bl_texture_nodes.diffuse.outputs[1], bl_mix_node.inputs[0])
        
        bl_output_node = bl_material.node_tree.nodes.new("ShaderNodeOutputMaterial")
        bl_output_node.location = (700, 0)
        bl_material.node_tree.links.new(bl_mix_node.outputs[0], bl_output_node.inputs[0])

        return bl_material

    def __create_empty_material(self, name: str) -> bpy.types.Material:
        bl_material = bpy.data.materials.new(name)
        bl_material.use_nodes = True
        bl_material.blend_method = "BLEND"
        bl_material.show_transparent_back = False
        for node in bl_material.node_tree.nodes:
            bl_material.node_tree.nodes.remove(node)
        
        return bl_material
    
    def __add_texture_nodes(self, bl_material: bpy.types.Material, tr_collection: Collection, tr_material: Material) -> _TextureNodeSet:
        bl_texture_nodes: list[bpy.types.ShaderNodeTexImage] = []

        texture_resources: list[ResourceKey] = list(tr_material.pixel_shader_textures)
#        texture_resources.extend(
#            Enumerable(tr_mesh_part.texture_indices).where(lambda i: i != 0xFFFFFFFF)
#                                                    .select(lambda i: tr_model.texture_resources[i])
#                                                    .where(lambda r: r is not None)
#                                                    .cast(ResourceKey)
#        )
        
        diffuse_texture_idx = -1
        diffuse_texture_size = -1

        normal_texture_idx = -1
        normal_texture_size = -1

        for texture_resource in sorted(texture_resources, key = lambda t: t.id):
            texture_file_path = tr_collection.get_resource_file_path(texture_resource)
            if texture_file_path is None:
                continue
            
            texture_type = DdsFile.get_type(texture_file_path)
            texture_size = os.path.getsize(texture_file_path) 
            if texture_type == DdsType.RGB and (diffuse_texture_idx < 0 or texture_size > diffuse_texture_size):
                diffuse_texture_idx = len(bl_texture_nodes)
                diffuse_texture_size = texture_size
            elif texture_type == DdsType.NORMAL and (normal_texture_idx < 0 or texture_size > normal_texture_size):
                normal_texture_idx = len(bl_texture_nodes)
                normal_texture_size = texture_size

            bl_image = cast(bpy.types.Image | None, bpy.data.images.get(os.path.basename(texture_file_path)))
            if bl_image is None:
                bl_image = bpy.data.images.load(texture_file_path)
            
            bl_texture_node = cast(bpy.types.ShaderNodeTexImage, bl_material.node_tree.nodes.new("ShaderNodeTexImage"))
            bl_texture_node.image = bl_image
            bl_texture_node.location = (0, len(bl_texture_nodes) * -40)
            bl_texture_node.hide = True
            bl_texture_nodes.append(bl_texture_node)
        
        return _TextureNodeSet(
            diffuse_texture_idx >= 0 and bl_texture_nodes[diffuse_texture_idx] or None,
            normal_texture_idx  >= 0 and bl_texture_nodes[normal_texture_idx]  or None
        )
    