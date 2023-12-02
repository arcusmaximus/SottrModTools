from typing import TypeVar

T = TypeVar("T")
U = TypeVar("U")

def coalesce(value1: T | None, value2: U) -> T | U:
    if value1 is not None:
        return value1
    else:
        return value2
