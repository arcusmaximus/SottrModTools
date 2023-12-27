from io_scene_sottr.util.SlotsBase import SlotsBase

class BitstreamReader(SlotsBase):
    data: bytes
    position: int
    current_long: int
    bits_remaining_in_current_long: int

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.position = 0
        self.current_long = 0
        self.bits_remaining_in_current_long = 0
    
    def read(self, size: int) -> int:
        result: int = 0
        while size > 0:
            if self.bits_remaining_in_current_long == 0:
                self.current_long = (self.data[self.position + 0] << 7*8) | \
                                    (self.data[self.position + 1] << 6*8) | \
                                    (self.data[self.position + 2] << 5*8) | \
                                    (self.data[self.position + 3] << 4*8) | \
                                    (self.data[self.position + 4] << 3*8) | \
                                    (self.data[self.position + 5] << 2*8) | \
                                    (self.data[self.position + 6] << 1*8) | \
                                    (self.data[self.position + 7]       )
                self.bits_remaining_in_current_long = 64
                self.position += 8
            
            size_in_current_long = min(size, self.bits_remaining_in_current_long)
            result <<= size_in_current_long
            result |= (self.current_long >> (self.bits_remaining_in_current_long - size_in_current_long)) & ((1 << size_in_current_long) - 1)
            size -= size_in_current_long
            self.bits_remaining_in_current_long -= size_in_current_long
        
        return result

    def seek(self, position: int) -> None:
        self.position = position
        self.bits_remaining_in_current_long = 0
