from io_scene_tr_reboot.tr.Skeleton import ISkeleton
from io_scene_tr_reboot.tr.rise.RiseCollision import RiseCollision

class ShadowCollision(RiseCollision):
    @classmethod
    def _convert_dtp_bone_id_to_global(cls, dtp_bone_id: int, skeleton: ISkeleton) -> int:
        return dtp_bone_id
