from ctypes import sizeof
import os
from typing import ClassVar, Iterator, Literal, NamedTuple

from mathutils import Matrix
from io_scene_sottr.tr.ResourceReference import ResourceReference
from io_scene_sottr.tr.Enumerations import ResourceType
from io_scene_sottr.tr.Hashes import Hashes
from io_scene_sottr.tr.Material import Material
from io_scene_sottr.tr.Model import Model
from io_scene_sottr.tr.ModelData import ModelData
from io_scene_sottr.tr.ResourceReader import ResourceReader
from io_scene_sottr.tr.ResourceKey import ResourceKey
from io_scene_sottr.tr.Skeleton import Skeleton
from io_scene_sottr.util.CStruct import CArray, CInt, CLong, CStruct
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
    num_external_component_types: CInt
    field_2C: CInt
    external_components_ref: ResourceReference | None
    num_internal_component_types: CInt
    field_3C: CInt
    internal_components_ref: ResourceReference | None
    int_dict_size: CInt
    field_4C: CInt
    int_dict_pairs_ref: ResourceReference | None
    model_refs: CArray[ResourceReference | None, Literal[2]]
    field_68: CLong
    field_70: CLong
    skeleton_ref: ResourceReference | None
    field_80: CInt
    field_84: CInt

assert(sizeof(_ObjectHeader) == 0x88)

class Collection(SlotsBase):
    class ResourceTypeInfo(NamedTuple):
        folder_name: str
        extensions: list[str]
    
    class ComponentArray(NamedTuple):
        position: int
        size: int
    
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
    component_arrays_by_type: dict[int, ComponentArray]
    
    root_model_resources: list[ResourceKey]

    __reader: ResourceReader

    def __init__(self, object_ref_file_path: str) -> None:
        self.folder_path = os.path.split(object_ref_file_path)[0]
        self.name = os.path.splitext(os.path.basename(object_ref_file_path))[0]
        self.component_arrays_by_type = {}
        self.root_model_resources = []

        index_resource = self.__get_object_resource(object_ref_file_path)
        reader = self.get_resource_reader(index_resource, True)
        if reader is None:
            raise Exception(f"Object resource {index_resource} does not exist")

        self.__reader = reader
        self.header = reader.read_struct(_ObjectHeader)

        if self.header.external_components_ref is not None:
            reader.seek(self.header.external_components_ref)
            self.__read_component_arrays(reader, self.header.num_external_component_types, True)

        if self.header.internal_components_ref is not None:
            reader.seek(self.header.internal_components_ref)
            self.__read_component_arrays(reader, self.header.num_internal_component_types, False)
    
    def get_model_instances(self) -> list[ModelInstance]:
        instances: list[Collection.ModelInstance] = Enumerable(self.root_model_resources).select(lambda r: Collection.ModelInstance(r, Matrix())).to_list()
        
        meshref_array = self.component_arrays_by_type.get(Hashes.meshref)
        if meshref_array is None:
            return instances
        
        for i in range(meshref_array.size):
            self.__reader.position = meshref_array.position + i*0x70
            transform = self.__reader.read_mat4x4_at(0)
            meshref_ref = self.__reader.read_ref_at(0x60)
            if meshref_ref is None:
                continue
            
            meshref_reader = self.get_resource_reader(meshref_ref, True)
            if meshref_reader is None:
                continue

            model_id = meshref_reader.read_uint32_at(0xC)
            instances.append(Collection.ModelInstance(ResourceKey(ResourceType.MODEL, model_id), transform))

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
        if self.header.skeleton_ref is None:
            return None
        
        reader = self.get_resource_reader(self.header.skeleton_ref, True)
        if reader is None:
            return None

        skeleton = Skeleton(self.header.skeleton_ref.id)
        skeleton.read(reader)
        return skeleton
    
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
    
    def __read_component_arrays(self, reader: ResourceReader, num_types: int, force_one_component: bool) -> None:
        for _ in range(num_types):
            type_name_hash = reader.read_uint32()
            num_components = reader.read_uint32()
            ref = reader.read_ref()

            if force_one_component:
                num_components = 1

            if ref is not None:
                self.component_arrays_by_type[type_name_hash] = Collection.ComponentArray(reader.resource_body_pos + ref.offset, num_components)
