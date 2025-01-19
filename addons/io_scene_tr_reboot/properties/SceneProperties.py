import base64
from typing import Annotated
import bpy
from io_scene_tr_reboot.properties.BlenderPropertyGroup import BlenderAttachedPropertyGroup, BlenderPropertyGroup, BlenderPropertyGroupCollection, Prop
from io_scene_tr_reboot.util.Enumerable import Enumerable

class SceneFileProperties(BlenderPropertyGroup):
    id: Annotated[int, Prop("File ID")]
    data: Annotated[str, Prop("File data")]

class SceneProperties(BlenderAttachedPropertyGroup[bpy.types.Scene]):
    property_name = "tr11_properties"

    files: Annotated[BlenderPropertyGroupCollection[SceneFileProperties], Prop("Files")]

    @staticmethod
    def get_file(props: "SceneProperties", id: int) -> bytes | None:
        file = Enumerable(props.files).first_or_none(lambda f: f.id == id)
        if file is None:
            return None

        return base64.b64decode(file.data)

    @staticmethod
    def set_file(props: "SceneProperties", id: int, data: memoryview | bytes) -> None:
        file = Enumerable(props.files).first_or_none(lambda f: f.id == id)
        if file is None:
            file = props.files.add()
            file.id = id

        file.data = base64.b64encode(data).decode()
