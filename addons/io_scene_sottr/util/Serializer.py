from io import StringIO
from typing import Any, Callable, ClassVar
from mathutils import Quaternion, Vector
from io_scene_sottr.util.Enumerable import Enumerable

class Serializer:
    @staticmethod
    def serialize_object(obj: object, extra_fields: dict[str, str] | None = None) -> str:
        values: dict[str, str] = {}

        if extra_fields is not None:
            values.update(extra_fields)

        for field_name, field_type in Serializer.__get_fields(obj.__class__).items():
            field_value = getattr(obj, field_name)

            if field_type == bool:
                field_value = str(field_value).lower()
            elif field_type == int or field_type == float or field_type == str:
                field_value = str(field_value)
            elif field_type == Vector or \
                field_type == Quaternion or \
                field_type == list[int] or \
                field_type == list[float]:
                field_value = ", ".join(Enumerable(field_value).select(str))
            elif field_type == list[Vector] or field_type == list[Quaternion]:
                field_value = "; ".join(Enumerable(field_value).select(lambda item: ", ".join(Enumerable(item).select(str))))
            else:
                raise Exception()
        
            values[field_name] = field_value

        return Serializer.serialize_dict(values)
    
    @staticmethod
    def serialize_dict(values: dict[Any, Any]) -> str:
        stream = StringIO()
        for key, value in values.items():
            stream.write(f"{key}: {value}\r\n")
        
        return stream.getvalue()
    
    @staticmethod
    def deserialize_object(data: str, get_type: Callable[[dict[str, str]], type]) -> object:
        values: dict[str, str] = Serializer.deserialize_dict(data)
        cls = get_type(values)
        obj = cls()
        
        for field_name, field_type in Serializer.__get_fields(cls).items():
            field_value = values.get(field_name)
            if field_value is None:
                continue

            if field_type == bool:
                if field_value == "true":
                    field_value = True
                elif field_value == "false":
                    field_value = False
                else:
                    raise Exception(f"\"{field_value}\" is not a valid bool value")
            elif field_type == int:
                field_value = int(field_value)
            elif field_type == float:
                field_value = float(field_value)
            elif field_type == Vector:
                field_value = Vector(Enumerable(field_value.split(",")).select(float).to_tuple())
            elif field_type == Quaternion:
                field_value = Quaternion(Enumerable(field_value.split(",")).select(float).to_tuple())
            elif field_type == list[int]:
                field_value = Enumerable(field_value.split(",")).select(int).to_list()
            elif field_type == list[float]:
                field_value = Enumerable(field_value.split(",")).select(float).to_list()
            elif field_type == list[Vector]:
                field_value = Enumerable(field_value.split(";")).select(lambda item: Vector(Enumerable(item.split(",")).select(float).to_tuple())).to_list()
            elif field_type == list[Quaternion]:
                field_value = Enumerable(field_value.split(";")).select(lambda item: Quaternion(Enumerable(item.split(",")).select(float).to_tuple())).to_list()
            elif field_type != str:
                raise Exception()

            setattr(obj, field_name, field_value)

        return obj
    
    @staticmethod
    def deserialize_dict(data: str) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in StringIO(data).readlines():
            key, value = line.split(":")
            values[key.strip()] = value.strip()
        
        return values

    @staticmethod
    def __get_fields(cls_: type) -> dict[str, type]:
        fields: dict[str, type] = {}
        while cls_ != object:
            for field_name, field_type in cls_.__annotations__.items():
                if hasattr(field_type, "__origin__") and getattr(field_type, "__origin__") == ClassVar:
                    continue

                fields[field_name] = field_type
            
            cls_ = cls_.__base__
        
        return fields