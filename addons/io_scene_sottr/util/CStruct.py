from abc import abstractmethod
import ctypes
import types
import typing
from typing import Any

if typing.TYPE_CHECKING:
    CSByte  = int
    CShort  = int
    CInt    = int
    CLong   = int

    CByte   = int
    CUShort = int
    CUInt   = int
    CULong  = int

    CFloat  = float
    CDouble = float
else:
    CSByte  = ctypes.c_int8
    CShort  = ctypes.c_int16
    CInt    = ctypes.c_int32
    CLong   = ctypes.c_int64

    CByte   = ctypes.c_uint8
    CUShort = ctypes.c_uint16
    CUInt   = ctypes.c_uint32
    CULong  = ctypes.c_uint64

    CFloat  = ctypes.c_float
    CDouble = ctypes.c_double

class ICStructTypeMapping(typing.Protocol):
    mapped_type: typing.Any
    c_type: typing.Any

    def map_from_c(self, c_value: typing.Any, offset: int, context: object) -> typing.Any: ...
    def map_to_c(self, mapped_value: typing.Any, offset: int, context: object) -> typing.Any: ...

TMappedType = typing.TypeVar("TMappedType")
TCType = typing.TypeVar("TCType")
class CStructTypeMapping(typing.Generic[TMappedType, TCType]):
    mapped_type: typing.Any                                     # type: ignore
    c_type:      typing.Any                                     # type: ignore

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.mapped_type = cls.__orig_bases__[0].__args__[0]     # type: ignore
        cls.c_type      = cls.__orig_bases__[0].__args__[1]     # type: ignore

    @abstractmethod
    def map_from_c(self, c_value: TCType, offset: int, context: object) -> TMappedType:
        raise NotImplementedError()
    
    @abstractmethod
    def map_to_c(self, mapped_value: TMappedType, offset: int, context: object) -> TCType:
        raise NotImplementedError()

_type_mappings: dict[typing.Any, ICStructTypeMapping] = {}

def create_c_array_type(item_type: typing.Any, length: int) -> type:
    def populate(ns: dict[str, typing.Any]) -> None:
        ns["_type_"] = item_type
        ns["_length_"] = length
            
    return types.new_class(f"Array_{item_type.__name__}_{length}", (ctypes.Array[item_type],), None, populate)

class CArrayAlias:
    item_type: typing.Any
    length: int

    def __init__(self, item_type: typing.Any, length: int) -> None:
        self.item_type = item_type
        self.length = length

    def __call__(self) -> Any:
        return [None] * self.length
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, CArrayAlias) and other.item_type == self.item_type and other.length == self.length
    
    def __hash__(self) -> int:
        return hash((self.item_type, self.length))

TArrayItem = typing.TypeVar("TArrayItem")
TArrayLength = typing.TypeVar("TArrayLength")
class CArray(typing.Generic[TArrayItem, TArrayLength]):
    def __getitem__(self, index: int) -> TArrayItem: ...
    def __setitem__(self, index: int, value: TArrayItem) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> typing.Iterator[TArrayItem]: ...

    def __class_getitem__(cls, params: tuple[typing.Any, typing.Any]) -> typing.Any:
        item_type = params[0]
        if isinstance(item_type, typing.TypeVar):
            return super().__class_getitem__(params)        # type: ignore

        length = params[1].__args__[0]
        item_type_mapping = _type_mappings.get(item_type)
        if item_type_mapping is None:
            return create_c_array_type(item_type, length)
        
        array_alias = CArrayAlias(item_type, length)
        if array_alias not in _type_mappings:
            _type_mappings[array_alias] = CArrayTypeMapping[item_type_mapping.mapped_type, item_type_mapping.c_type, length](
                array_alias,
                item_type_mapping                           # type: ignore
            )
        
        return array_alias
            

TMappedItemType = typing.TypeVar("TMappedItemType")
TCItemType = typing.TypeVar("TCItemType")
class CArrayTypeMapping(typing.Generic[TMappedItemType, TCItemType, TArrayLength]):
    mapped_type: typing.Any
    c_type: typing.Any
    item_type_mapping: CStructTypeMapping[TMappedItemType, TCItemType]

    def __init__(self, mapped_array_type: CArrayAlias, item_type_mapping: CStructTypeMapping[TMappedItemType, TCItemType]) -> None:
        self.mapped_type = mapped_array_type
        self.c_type = create_c_array_type(item_type_mapping.c_type, mapped_array_type.length)
        self.item_type_mapping = item_type_mapping

    def map_from_c(self, c_value: CArray[TCItemType, TArrayLength], offset: int, context: object) -> CArray[TMappedItemType, TArrayLength]:
        mapped_value = self.mapped_type()
        for i in range(len(c_value)):
            mapped_value[i] = self.item_type_mapping.map_from_c(c_value[i], offset + i * ctypes.sizeof(self.item_type_mapping.c_type), context)
        
        return mapped_value

    def map_to_c(self, mapped_value: CArray[TMappedItemType, TArrayLength], offset: int, context: object) -> CArray[TCItemType, TArrayLength]:
        c_value = self.c_type()
        for i in range(len(mapped_value)):
            c_value[i] = self.item_type_mapping.map_to_c(mapped_value[i], offset + i * ctypes.sizeof(self.item_type_mapping.c_type), context)
        
        return c_value

class CStructField(typing.NamedTuple):
    offset: int
    type: type
    type_mapping: ICStructTypeMapping | None

class CStructMeta(type(ctypes.Structure)):
    def __new__(cls: type, class_name: str, bases: tuple[type, ...], namespace: dict[str, typing.Any]) -> type:
        if class_name != "CStructBase" and class_name != "CStruct":
            field_types: list[tuple[str, type]] = []
            field_infos: dict[str, CStructField] = {}
            field_offset = 0

            ignored_fields = namespace.get("_ignored_fields_")
            if ignored_fields is not None and not isinstance(ignored_fields, tuple):
                raise Exception("_ignored_fields_ must be a tuple[str]")
            
            for field_name, field_type in typing.cast(dict[str, typing.Any], namespace["__annotations__"]).items():
                if ignored_fields is not None and field_name in ignored_fields:
                    continue

                field_type_mapping = _type_mappings.get(field_type)
                field_infos[field_name] = CStructField(field_offset, field_type, field_type_mapping)

                if field_type_mapping is not None:
                    field_name = CStructMeta.get_c_field_name(field_name)
                    field_type = field_type_mapping.c_type
                elif issubclass(field_type, CStruct):                           # type: ignore
                    field_name = CStructMeta.get_c_field_name(field_name)
                
                field_types.append((field_name, field_type))
                field_offset += ctypes.sizeof(field_type)

            for field_name, field_value in namespace.items():
                if not isinstance(field_value, CFlag):
                    continue

                if field_value.flags_field_name not in field_infos:
                    raise Exception(f"Field {class_name}.{field_name} is defined as a flag in non-existent field {field_value.flags_field_name}")
            
            namespace["_pack_"] = 1
            namespace["_fields_"] = field_types
            namespace["_field_infos_"] = field_infos
        
        return typing.cast(type, super()).__new__(cls, class_name, bases, namespace)
    
    @staticmethod
    def get_c_field_name(name: str) -> str:
        return "_c_" + name
    
    @staticmethod
    def make_flag_property(flags_field_name: str, flag_value: int) -> property:
        def get(struct: CStruct) -> bool:
            return (getattr(struct, flags_field_name) & flag_value) != 0
        
        def set(struct: CStruct, enable: bool) -> None:
            flags = getattr(struct, flags_field_name)
            if enable:
                flags |= flag_value
            else:
                flags &= ~flag_value
            
            setattr(struct, flags_field_name, flags)
        
        return property(get, set)

if typing.TYPE_CHECKING:
    struct_secondary_base = typing.Protocol
    struct_metaclass = type
else:
    struct_secondary_base = object
    struct_metaclass = CStructMeta

class CStruct(ctypes.Structure, struct_secondary_base, metaclass=struct_metaclass):         # type: ignore
    _field_infos_: dict[str, CStructField] = {}
    
    @staticmethod
    def register_type_mappings(*mappings: ICStructTypeMapping) -> None:
        for mapping in mappings:
            _type_mappings[mapping.mapped_type] = mapping
    
    def map_fields_from_c(self, context: object = None, offset_in_parent: int = 0) -> None:
        for field_name, field_info in self._field_infos_.items():
            if field_info.type_mapping is not None:
                c_value = getattr(self, CStructMeta.get_c_field_name(field_name))
                mapped_value = field_info.type_mapping.map_from_c(c_value, offset_in_parent + field_info.offset, context)
                setattr(self, field_name, mapped_value)
            elif issubclass(field_info.type, CStruct):                                      # type: ignore
                struct_value = typing.cast(CStruct, getattr(self, CStructMeta.get_c_field_name(field_name)))
                struct_value.map_fields_from_c(context, offset_in_parent + field_info.offset)
                setattr(self, field_name, struct_value)
    
    def map_fields_to_c(self, context: object = None, offset_in_parent: int = 0) -> None:
        for field_name, field_info in self._field_infos_.items():
            if field_info.type_mapping is not None:
                mapped_value = getattr(self, field_name)
                c_value = field_info.type_mapping.map_to_c(mapped_value, offset_in_parent + field_info.offset, context)
                setattr(self, CStructMeta.get_c_field_name(field_name), c_value)
            elif issubclass(field_info.type, CStruct):                                      # type: ignore
                struct_value = typing.cast(CStruct, getattr(self, field_name))
                struct_value.map_fields_to_c(context, offset_in_parent + field_info.offset)
                setattr(self, CStructMeta.get_c_field_name(field_name), struct_value)

class CFlag:
    flags_field_name: str
    flag_value: int

    def __init__(self, flags_field_name: str, flag_value: int) -> None:
        self.flags_field_name = flags_field_name
        self.flag_value = flag_value
    
    def __get__(self, obj: CStruct, typ: type | None = None) -> bool:
        flags: int = getattr(obj, self.flags_field_name)
        return (flags & self.flag_value) != 0
    
    def __set__(self, obj: CStruct, enable: bool) -> None:
        flags: int = getattr(obj, self.flags_field_name)
        if enable:
            flags |= self.flag_value
        else:
            flags &= ~self.flag_value
        
        setattr(obj, self.flags_field_name, flags)
