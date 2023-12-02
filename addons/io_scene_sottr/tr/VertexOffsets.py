from mathutils import Vector
from io_scene_sottr.util.SlotsBase import SlotsBase

class VertexOffsets(SlotsBase):
    position_offset: Vector
    normal_offset: Vector
    color_offset: Vector

    def __init__(self, position_offset: Vector, normal_offset: Vector, color_offset: Vector) -> None:
        self.position_offset = position_offset
        self.normal_offset = normal_offset
        self.color_offset = color_offset
