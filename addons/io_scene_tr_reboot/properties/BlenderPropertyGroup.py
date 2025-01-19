from enum import Enum
import bpy
from typing import Any, Callable, ClassVar, Generic, Iterator, NamedTuple, Protocol, TypeGuard, TypeVar, cast
from io_scene_tr_reboot.util.Enumerable import Enumerable

class PropSubType(Enum):
    NONE = 0
    PIXEL = 1
    UNSIGNED = 2
    PERCENTAGE = 3
    FACTOR = 4
    ANGLE = 5
    TIME = 6
    TIME_ABSOLUTE = 7
    DISTANCE = 8
    DISTANCE_CAMERA = 9
    POWER = 10
    TEMPERATURE = 11
    FILE_PATH = 12

class PropOption(Enum):
    HIDDEN = 0
    SKIP_SAVE = 1
    ANIMATABLE = 2
    LIBRARY_EDITABLE = 3
    PROPORTIONAL = 4
    TEXTEDIT_UPDATE = 5
    OUTPUT_PATH = 6

class Prop(NamedTuple):
    name: str
    description: str | None = None
    default: Any = None
    min: float | None = None
    max: float | None = None
    search: Callable[["BlenderPropertyGroup", bpy.types.Context, str], list[str]] | None = None
    options: set[PropOption] | None = None
    subtype: PropSubType | None = None
    get: Callable[[bpy.types.Property], Any] | None = None
    set: Callable[[bpy.types.Property, Any], None] | None = None

class EnumItem(NamedTuple):
    identifier: str
    name: str
    description: str
    icon: str | None = None
    value: int | None = None

class EnumProp(NamedTuple):
    name: str
    items: list[EnumItem] | Callable[["BlenderPropertyGroup", bpy.types.Context | None], list[EnumItem]]
    default: str | None = None

class FactoryFunction(Protocol):
    def __call__(self, **kwds: Any) -> Any: ...

TPropertyGroup = TypeVar("TPropertyGroup", bound = "BlenderPropertyGroup", covariant = True)

class BlenderPropertyGroupCollection(Generic[TPropertyGroup], Protocol):
    def add(self) -> TPropertyGroup: ...
    def remove(self, index: int) -> None: ...
    def clear(self) -> None: ...
    def __iter__(self) -> Iterator[TPropertyGroup]: ...
    def __len__(self) -> int: ...

class BlenderPropertyGroup(Protocol):
    property_factory_funcs: ClassVar[dict[type, FactoryFunction]] = {
        bool:  bpy.props.BoolProperty,          # type: ignore
        float: bpy.props.FloatProperty,
        int:   bpy.props.IntProperty,
        str:   bpy.props.StringProperty
    }

    bl_class: ClassVar[type[bpy.types.PropertyGroup] | None] = None

    @classmethod
    def register(cls) -> None:
        metaclass: type = type(bpy.types.PropertyGroup)
        cls.bl_class = metaclass.__new__(
            metaclass,
            cls.__name__,
            (bpy.types.PropertyGroup,),
            {
                "__annotations__": BlenderPropertyGroup.convert_annotations(cls.__name__, cls.__annotations__)
            }
        )
        bpy.utils.register_class(cls.bl_class)

        if BlenderPropertyGroup.is_attached_property_group(cls):
            bl_type: type = getattr(cls, "__orig_bases__")[0].__args__[0]
            setattr(bl_type, cls.property_name, bpy.props.PointerProperty(type = cls.bl_class))

    @classmethod
    def unregister(cls) -> None:
        if BlenderPropertyGroup.is_attached_property_group(cls):
            bl_type: type = getattr(cls, "__orig_bases__")[0].__args__[0]
            delattr(bl_type, cls.property_name)

        bpy.utils.unregister_class(cast(Any, cls.bl_class))
        cls.bl_class = None

    @staticmethod
    def convert_annotations(class_name: str, orig_annotations: dict[str, Any]) -> dict[str, Any]:
        annotations: dict[str, Any] = {}

        for property_name, annotation in orig_annotations.items():
            property_type = annotation.__origin__
            property_metadata = annotation.__metadata__[0]

            if isinstance(property_metadata, Prop):
                if BlenderPropertyGroup.is_property_group_collection(property_type):
                    item_type = property_type.__args__[0]
                    if BlenderPropertyGroup.is_property_group(item_type):
                        annotations[property_name] = bpy.props.CollectionProperty(name = property_metadata.name, type = item_type.bl_class)
                    else:
                        raise Exception(f"Collection property {property_name} in class {class_name} must have a property group as its item type")
                elif BlenderPropertyGroup.is_property_group(property_type):
                    annotations[property_name] = bpy.props.PointerProperty(name = property_metadata.name, type = property_type.bl_class)
                else:
                    metadata_dict = BlenderPropertyGroup.get_metadata_dict(property_metadata)
                    annotations[property_name] = BlenderPropertyGroup.property_factory_funcs[property_type](**metadata_dict)
            elif isinstance(property_metadata, EnumProp):
                metadata_dict = BlenderPropertyGroup.get_metadata_dict(property_metadata)
                annotations[property_name] = bpy.props.EnumProperty(**metadata_dict)
            else:
                raise Exception(f"Property {property_name} in class {class_name} doesn't have a correct annotation")

        return annotations

    @staticmethod
    def get_metadata_dict(prop: NamedTuple) -> dict[str, Any]:
        result: dict[str, Any] = prop._asdict()
        for key, value in result.items():
            if isinstance(value, Enum):
                result[key] = value.name
            elif isinstance(value, set):
                result[key] = Enumerable(cast(set[Enum], value)).select(lambda v: v.name).to_set()

        for empty_key in Enumerable(result.items()).where(lambda p: p[1] is None).select(lambda p: p[0]).to_list():
            del result[empty_key]

        return result

    @staticmethod
    def is_property_group(type: type) -> TypeGuard[type["BlenderPropertyGroup"]]:
        return type.__base__ == BlenderPropertyGroup

    @staticmethod
    def is_property_group_collection(type: Any) -> bool:
        return hasattr(type, "__origin__") and getattr(type, "__origin__") == BlenderPropertyGroupCollection

    @staticmethod
    def is_attached_property_group(type: type) -> TypeGuard[type["BlenderAttachedPropertyGroup"]]:          # type: ignore
        return type.__base__ == BlenderAttachedPropertyGroup

TPropertyGroup = TypeVar("TPropertyGroup", bound = "BlenderAttachedPropertyGroup")                          # pyright: ignore[reportMissingTypeArgument]
TBlenderId = TypeVar("TBlenderId", contravariant = True)

class BlenderAttachedPropertyGroup(Generic[TBlenderId], BlenderPropertyGroup, Protocol):
    property_name: ClassVar[str]

    @classmethod
    def get_instance(cls: type[TPropertyGroup], bl_item: TBlenderId) -> TPropertyGroup:
        return getattr(bl_item, cls.property_name)
