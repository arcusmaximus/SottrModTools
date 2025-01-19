from io_scene_tr_reboot.tr.ResourceBuilder import ResourceBuilder
from io_scene_tr_reboot.tr.tr2013.Tr2013ModelReferences import Tr2013ModelReferences

class RiseModelReferences(Tr2013ModelReferences):
    def write(self, writer: ResourceBuilder) -> None:
        self.cloth_definition_ref = self.model_data_resource
        return super().write(writer)
