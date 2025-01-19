from typing import Literal, cast
from mathutils import Matrix
from io_scene_tr_reboot.tr.Cloth import Cloth
from io_scene_tr_reboot.tr.Collection import Collection
from io_scene_tr_reboot.tr.Collision import Collision
from io_scene_tr_reboot.tr.Enumerations import CdcGame
from io_scene_tr_reboot.tr.Material import Material
from io_scene_tr_reboot.tr.Model import IModel
from io_scene_tr_reboot.tr.ResourceKey import ResourceKey
from io_scene_tr_reboot.tr.ResourceReference import ResourceReference
from io_scene_tr_reboot.tr.Skeleton import ISkeleton
from io_scene_tr_reboot.tr.tr2013.Tr2013Cloth import Tr2013Cloth
from io_scene_tr_reboot.tr.tr2013.Tr2013LegacyModel import Tr2013LegacyModel
from io_scene_tr_reboot.tr.tr2013.Tr2013Material import Tr2013Material
from io_scene_tr_reboot.tr.tr2013.Tr2013Model import Tr2013Model
from io_scene_tr_reboot.tr.tr2013.Tr2013Skeleton import Tr2013Skeleton
from io_scene_tr_reboot.util.CStruct import CArray, CByte, CInt, CStruct32
from io_scene_tr_reboot.util.Enumerable import Enumerable

class Tr2013ObjectHeader(CStruct32):
    padding_1: CArray[CByte, Literal[0x80]]
    cloth_tune_ref: ResourceReference | None
    padding_2: CArray[CByte, Literal[0x5C]]
    num_models: CInt
    model_refs_ref: ResourceReference | None

class Tr2013Collection(Collection):
    game = CdcGame.TR2013

    __model_refs: list[ResourceReference]
    __cloth_tune_ref: ResourceReference | None
    __models: dict[ResourceKey, Tr2013Model]

    def __init__(self, object_ref_file_path: str) -> None:
        super().__init__(object_ref_file_path)

        object_reader = self.get_resource_reader(self.object_ref, True)
        if object_reader is None:
            raise Exception("Object file does not exist")

        object_header = object_reader.read_struct(Tr2013ObjectHeader)

        if object_header.model_refs_ref is not None:
            object_reader.seek(object_header.model_refs_ref)
            model_refs = object_reader.read_ref_list(object_header.num_models)
            self.__model_refs = Enumerable(model_refs).of_type(ResourceReference).to_list()
        else:
            self.__model_refs = []

        self.__cloth_tune_ref = object_header.cloth_tune_ref
        self.__models = {}

    def get_model_instances(self) -> list[Collection.ModelInstance]:
        return Enumerable(self.__model_refs).select(lambda r: Collection.ModelInstance(r, Matrix())).to_list()

    def get_model(self, resource: ResourceKey) -> IModel | None:
        if resource.__class__ != ResourceKey:
            resource = ResourceKey(resource.type, resource.id)

        model = self.__models.get(resource)
        if model is not None:
            return model

        legacy_model = self.get_legacy_model(resource)
        if legacy_model is None or legacy_model.new_model_ref is None:
            return None

        reader = self.get_resource_reader(legacy_model.new_model_ref, True)
        if reader is None:
            return None

        model = Tr2013Model(resource.id, legacy_model.new_model_ref.id)
        model.read(reader)
        self.__models[resource] = model
        return model

    def _create_material(self) -> Material:
        return Tr2013Material()

    def get_skeleton(self) -> ISkeleton | None:
        for legacy_model_ref in self.__model_refs:
            legacy_model = self.get_legacy_model(legacy_model_ref)
            if legacy_model is None or legacy_model.bones_ref is None or legacy_model.bone_id_map_ref is None:
                continue

            bones_reader = self.get_resource_reader(legacy_model.bones_ref, True)
            id_mappings_reader = self.get_resource_reader(legacy_model.bone_id_map_ref, True)
            if bones_reader is None or id_mappings_reader is None:
                continue

            skeleton = Tr2013Skeleton(legacy_model.bones_ref.id)
            skeleton.read_bones(bones_reader)
            skeleton.read_id_mappings(id_mappings_reader)
            return skeleton

        return None

    def get_collisions(self) -> list[Collision]:
        return []

    @property
    def cloth_definition_ref(self) -> ResourceReference | None:
        for model_ref in self.__model_refs:
            model = cast(Tr2013Model | None, self.get_model(model_ref))
            if model is not None and model.refs.cloth_definition_ref is not None:
                return model.refs.cloth_definition_ref

        return None

    @property
    def cloth_tune_ref(self) -> ResourceReference | None:
        return self.__cloth_tune_ref

    def get_cloth(self) -> Cloth | None:
        cloth_definition_ref = self.cloth_definition_ref
        cloth_tune_ref = self.cloth_tune_ref
        if cloth_definition_ref is None or cloth_tune_ref is None:
            return None

        definition_reader = self.get_resource_reader(cloth_definition_ref, True)
        tune_reader = self.get_resource_reader(self.object_ref, True)
        if definition_reader is None or tune_reader is None:
            return None

        definition_reader.seek(cloth_definition_ref)
        tune_reader.seek(cloth_tune_ref)

        cloth = Tr2013Cloth(cloth_definition_ref.id, cloth_tune_ref.id)
        cloth.read(definition_reader, tune_reader, [])
        return cloth

    def get_legacy_model(self, resource: ResourceKey) -> Tr2013LegacyModel | None:
        reader = self.get_resource_reader(resource, False)
        if reader is None:
            return None

        return Tr2013LegacyModel(reader.data)
