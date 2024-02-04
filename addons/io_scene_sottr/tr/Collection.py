from ctypes import sizeof
import os
from typing import ClassVar, Iterator, Literal, NamedTuple
from mathutils import Matrix
from io_scene_sottr.tr.Cloth import Cloth, CollisionType
from io_scene_sottr.tr.Collision import Collision
from io_scene_sottr.tr.ResourceReference import ResourceReference
from io_scene_sottr.tr.Enumerations import ResourceType
from io_scene_sottr.tr.Hashes import Hashes
from io_scene_sottr.tr.Material import Material
from io_scene_sottr.tr.Model import Model
from io_scene_sottr.tr.ModelData import ModelData
from io_scene_sottr.tr.ResourceReader import ResourceReader
from io_scene_sottr.tr.ResourceKey import ResourceKey
from io_scene_sottr.tr.Skeleton import Skeleton
from io_scene_sottr.util.CStruct import CArray, CInt, CLong, CStruct, CUInt, CULong
from io_scene_sottr.util.Enumerable import Enumerable
from io_scene_sottr.util.SlotsBase import SlotsBase

class _ObjectHeader(CStruct):
    zone_id: CInt
    field_4: CInt
    zone_name_ref: ResourceReference | None
    type_name_hash: CInt
    field_14: CInt
    field_18: CLong
    field_20: CLong
    num_simple_components: CInt
    field_2C: CInt
    simple_components_ref: ResourceReference | None
    num_transformed_component_types: CInt
    field_3C: CInt
    transformed_components_ref: ResourceReference | None
    num_transformed_component_counts: CInt
    field_4C: CInt
    transformed_component_counts_ref: ResourceReference | None
    model_refs: CArray[ResourceReference | None, Literal[2]]
    field_68: CLong
    field_70: CLong
    skeleton_ref: ResourceReference | None
    field_80: CInt
    field_84: CInt
    field_88: CLong
    cloth_definition_ref: ResourceReference | None

assert(sizeof(_ObjectHeader) == 0x98)

class _ObjectSimpleComponent(CStruct):
    type_hash: CInt
    count: CInt
    dtp_ref: ResourceReference | None

assert(sizeof(_ObjectSimpleComponent) == 0x10)

class _ObjectTransformedComponentArray(CStruct):
    type_hash: CUInt
    count: CInt
    items_ref: ResourceReference | None

assert(sizeof(_ObjectTransformedComponentArray) == 0x10)

class _ObjectTransformedComponent(CStruct):
    transform: Matrix
    field_40: CInt
    id: CInt
    field_48: CLong
    field_50: CLong
    hash: CULong
    dtp_ref: ResourceReference | None
    field_68: CULong

assert(sizeof(_ObjectTransformedComponent) == 0x70)

class CollectionTransformedComponent(NamedTuple):
    hash: int
    dtp_ref: ResourceReference
    transform: Matrix

class Collection(SlotsBase):
    class ResourceTypeInfo(NamedTuple):
        folder_name: str
        extensions: list[str]
    
    class ModelInstance(NamedTuple):
        resource: ResourceKey
        transform: Matrix

    __resource_type_infos: ClassVar[dict[ResourceType, ResourceTypeInfo]] = {
        ResourceType.ANIMATION:     ResourceTypeInfo("Animation",   [".tr11anim"]),
        ResourceType.DTP:           ResourceTypeInfo("Dtp",         [".tr11dtp"]),
        ResourceType.MATERIAL:      ResourceTypeInfo("Material",    [".tr11material"]),
        ResourceType.MODEL:         ResourceTypeInfo("Model",       [".tr11model", ".tr11modeldata"]),
        ResourceType.PSDRES:        ResourceTypeInfo("PsdRes",      [".tr11psdres"]),
        ResourceType.SCRIPT:        ResourceTypeInfo("Script",      [".tr11script"]),
        ResourceType.SHADERLIB:     ResourceTypeInfo("ShaderLib",   [".tr11shaderlib"]),
        ResourceType.TEXTURE:       ResourceTypeInfo("Texture",     [".dds"]),
        ResourceType.TRIGGER:       ResourceTypeInfo("Trigger",     [".tr11trigger"])
    }

    folder_path: str
    name: str
    header: _ObjectHeader
    simple_components: dict[int, ResourceReference]
    transformed_components: dict[int, list[CollectionTransformedComponent]]
    
    root_model_resources: list[ResourceKey]

    __skeleton: Skeleton | None
    __collisions: list[Collision] | None

    def __init__(self, object_ref_file_path: str) -> None:
        self.folder_path = os.path.split(object_ref_file_path)[0]
        self.name = os.path.splitext(os.path.basename(object_ref_file_path))[0]
        self.root_model_resources = []
        self.__skeleton = None
        self.__collisions = None

        index_resource = self.__get_object_resource(object_ref_file_path)
        reader = self.get_resource_reader(index_resource, True)
        if reader is None:
            raise Exception(f"Object resource {index_resource} does not exist")

        self.header = reader.read_struct(_ObjectHeader)

        self.simple_components = {}
        if self.header.simple_components_ref is not None:
            reader.seek(self.header.simple_components_ref)
            for _ in range(self.header.num_simple_components):
                component = reader.read_struct(_ObjectSimpleComponent)
                if component.dtp_ref is not None:
                    self.simple_components[component.type_hash] = component.dtp_ref

        self.transformed_components = {}
        if self.header.transformed_components_ref is not None:
            reader.seek(self.header.transformed_components_ref)
            transformed_component_arrays = reader.read_struct_list(_ObjectTransformedComponentArray, self.header.num_transformed_component_types)
            for transformed_component_array in transformed_component_arrays:
                if transformed_component_array.items_ref is None:
                    continue

                components_of_type: list[CollectionTransformedComponent] = []
                self.transformed_components[transformed_component_array.type_hash] = components_of_type

                reader.seek(transformed_component_array.items_ref)
                for _ in range(transformed_component_array.count):
                    component = reader.read_struct(_ObjectTransformedComponent)
                    if component.dtp_ref is not None:
                        components_of_type.append(CollectionTransformedComponent(component.hash, component.dtp_ref, component.transform))
    
    def get_model_instances(self) -> list[ModelInstance]:
        instances: list[Collection.ModelInstance] = Enumerable(self.root_model_resources).select(lambda r: Collection.ModelInstance(r, Matrix())).to_list()
        
        meshref_components = self.transformed_components.get(Hashes.meshref)
        if meshref_components is None:
            return instances
        
        for meshref_component in meshref_components:
            meshref_reader = self.get_resource_reader(meshref_component.dtp_ref, True)
            if meshref_reader is None:
                continue

            model_id = meshref_reader.read_uint32_at(0xC)
            instances.append(Collection.ModelInstance(ResourceKey(ResourceType.MODEL, model_id), meshref_component.transform))

        return instances
    
    def get_model_resources(self) -> Iterator[ResourceKey]:
        resource_type_info = Collection.__resource_type_infos[ResourceType.MODEL]
        folder_path = os.path.join(self.folder_path, resource_type_info.folder_name)
        for file_info in os.scandir(folder_path):
            if file_info.is_file() and os.path.splitext(file_info.name)[1] == resource_type_info.extensions[0]:
                resource_id = int(os.path.splitext(file_info.name)[0])
                yield ResourceKey(ResourceType.MODEL, resource_id)
    
    def get_model(self, resource: ResourceKey) -> Model | None:
        reader = self.get_resource_reader(resource, True)
        if reader is None:
            return None
        
        model = Model(resource.id)
        model.read(reader)
        return model
    
    def get_model_data(self, resource: ResourceKey) -> ModelData | None:
        reader = self.get_resource_reader(resource, False)
        if reader is None:
            return None

        model_data = ModelData(resource.id)
        model_data.read(reader)
        return model_data
    
    def get_material(self, resource: ResourceKey) -> Material | None:
        reader = self.get_resource_reader(resource, True)
        if reader is None:
            return None
        
        material = Material()
        material.read(reader)
        return material
    
    def get_skeleton(self) -> Skeleton | None:
        if self.__skeleton is not None:
            return self.__skeleton

        if self.header.skeleton_ref is None:
            return None
        
        reader = self.get_resource_reader(self.header.skeleton_ref, True)
        if reader is None:
            return None

        self.__skeleton = Skeleton(self.header.skeleton_ref.id)
        self.__skeleton.read(reader)
        return self.__skeleton
    
    def get_collisions(self) -> list[Collision]:
        if self.__collisions is not None:
            return self.__collisions

        type_hashes: dict[CollisionType, int] = {
            CollisionType.BOX:                 Hashes.genericboxshapelist,
            CollisionType.CAPSULE:             Hashes.genericcapsuleshapelist,
            CollisionType.DOUBLERADIICAPSULE:  Hashes.genericdoubleradiicapsuleshapelist,
            CollisionType.SPHERE:              Hashes.genericsphereshapelist
        }
        self.__collisions = []
        for type, type_hash in type_hashes.items():
            components_of_type = self.transformed_components.get(type_hash)
            if components_of_type is None:
                continue

            for component in components_of_type:
                reader = self.get_resource_reader(component.dtp_ref, False)
                if reader is not None:
                    self.__collisions.append(Collision.read_with_transform(type, component.hash, reader, component.transform))
        
        return self.__collisions
    
    def get_cloth(self) -> Cloth | None:
        cloth_component_ref = self.simple_components.get(Hashes.cloth)
        if cloth_component_ref is None or self.header.cloth_definition_ref is None:
            return None

        cloth_component_reader = self.get_resource_reader(cloth_component_ref, True)
        cloth_reader = self.get_resource_reader(self.header.cloth_definition_ref, True)
        if cloth_component_reader is None or cloth_reader is None:
            return None
        
        collisions = self.get_collisions()

        cloth = Cloth(self.header.cloth_definition_ref.id, cloth_component_ref.id)
        cloth.read(cloth_reader, cloth_component_reader, collisions)
        return cloth
    
    def get_resources(self, resource_type: ResourceType) -> Iterator[ResourceKey]:
        resource_type_info = Collection.__resource_type_infos[resource_type]
        folder_path = os.path.join(self.folder_path, resource_type_info.folder_name)
        for file_info in os.scandir(folder_path):
            file_name, file_extension = os.path.splitext(file_info.name)
            if file_info.is_file() and file_extension in resource_type_info.extensions:
                resource_id = int(file_name)
                yield ResourceKey(resource_type, resource_id)
    
    def get_resource_file_path(self, resource: ResourceKey) -> str | None:
        type_info = self.__resource_type_infos[resource.type]
        for extension in type_info.extensions:
            file_path = os.path.join(self.folder_path, type_info.folder_name, str(resource.id) + extension)
            if os.path.isfile(file_path):
                return file_path
        
        return None
    
    @staticmethod
    def make_resource_file_name(resource: ResourceKey) -> str:
        return str(resource.id) + Collection.__resource_type_infos[resource.type].extensions[0]
    
    @staticmethod
    def parse_resource_file_path(file_path: str) -> ResourceKey:
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        resource_id = int(file_name)
        for resource_type, resource_type_info in Collection.__resource_type_infos.items():
            if file_extension in resource_type_info.extensions:
                return ResourceKey(resource_type, resource_id)
        
        raise Exception(f"{file_path} is not a valid resource file path")
    
    def get_resource_reader(self, resource: ResourceKey, has_references: bool) -> ResourceReader | None:
        file_path = self.get_resource_file_path(resource)
        if file_path is None:
            return None

        file_data: bytes
        with open(file_path, "rb") as file:
            file_data = file.read()
        
        return ResourceReader(resource, file_data, has_references)
    
    def __get_object_resource(self, object_ref_file_path: str) -> ResourceKey:
        object_ref_data: bytes
        with open(object_ref_file_path, "rb") as object_ref_file:
            object_ref_data = object_ref_file.read()
        
        reader = ResourceReader(ResourceKey(ResourceType.OBJECTREFERENCE, -1), object_ref_data, True)
        ref = reader.read_ref()
        if ref is None:
            raise Exception("No reference to object .dtp file")
        
        return ref
    