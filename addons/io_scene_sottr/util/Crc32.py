from typing import ClassVar

class Crc32:
    _table: ClassVar[list[int]] = []

    @staticmethod
    def initialize() -> None:
        for i in range(256):
            value = i << 0x18
            for _ in range(8):
                if value & 0x80000000:
                    value = (value * 2) ^ 0x4C11DB7
                else:
                    value = value * 2
                
                value &= 0xFFFFFFFF
            
            Crc32._table.append(value)

    @staticmethod
    def calculate(input: bytes) -> int:
        hash = 0xFFFFFFFF
        for b in input:
            hash = (Crc32._table[(hash >> 0x18) ^ b] ^ (hash << 8)) & 0xFFFFFFFF
        
        return hash ^ 0xFFFFFFFF

Crc32.initialize()
