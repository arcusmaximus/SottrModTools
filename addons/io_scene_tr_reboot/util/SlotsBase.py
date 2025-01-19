from typing import Any, ClassVar, cast
from io_scene_tr_reboot.util.Enumerable import Enumerable

class SlotsMeta(type):
    def __new__(cls, name: str, bases: tuple[type, ...], ns: dict[str, Any]) -> type:        
        annotations = cast(dict[str, Any] | None, ns.get("__annotations__"))
        if annotations is not None:
            ns["__slots__"] = Enumerable(annotations.items()).where(lambda p: not hasattr(p[1], "__origin__") or p[1].__origin__ is not ClassVar)   \
                                                             .select(lambda p: p[0])                                                                \
                                                             .to_list()
        else:
            ns["__slots__"] = ()
        
        return super().__new__(cls, name, bases, ns)

class SlotsBase(metaclass=SlotsMeta):
    pass
