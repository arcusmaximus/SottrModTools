from io import BufferedIOBase

class BitStreamWriter:
    stream: BufferedIOBase
    current_long: int
    bits_remaining_in_current_long: int

    def __init__(self, stream: BufferedIOBase) -> None:
        self.stream = stream
        self.current_long = 0
        self.bits_remaining_in_current_long = 64
    
    def write(self, value: int, size: int) -> None:
        size_in_current_long = min(self.bits_remaining_in_current_long, size)
        self.bits_remaining_in_current_long -= size
        self.current_long |= ((value >> (size - size_in_current_long)) & ((1 << size_in_current_long) - 1)) << self.bits_remaining_in_current_long
        if self.bits_remaining_in_current_long == 0:
            self.flush()

    def flush(self) -> None:
        if self.bits_remaining_in_current_long == 64:
            return
        
        self.stream.write(self.current_long.to_bytes(8, "big"))
        self.current_long = 0
        self.bits_remaining_in_current_long = 64
