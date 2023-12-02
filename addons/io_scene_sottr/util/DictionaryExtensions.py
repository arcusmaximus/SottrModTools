from typing import Callable, TypeVar

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

class DictionaryExtensions:
    @staticmethod
    def get_or_add(dictionary: dict[TKey, TValue], key: TKey, get_value: Callable[[], TValue]) -> TValue:
        value = dictionary.get(key)
        if value is None:
            value = get_value()
            dictionary[key] = value
        
        return value
