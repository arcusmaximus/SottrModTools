from io_scene_tr_reboot.tr.rise.RiseMaterial import RiseMaterial

class ShadowMaterial(RiseMaterial):
    @property
    def num_passes(self) -> int:
        return 9
