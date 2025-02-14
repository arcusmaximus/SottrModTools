from io_scene_tr_reboot.tr.Enumerations import CdcGame
from io_scene_tr_reboot.tr.IFactory import IFactory
from io_scene_tr_reboot.tr.rise.RiseFactory import RiseFactory
from io_scene_tr_reboot.tr.shadow.ShadowFactory import ShadowFactory
from io_scene_tr_reboot.tr.tr2013.Tr2013Factory import Tr2013Factory

class Factories:
    @staticmethod
    def get(game: CdcGame) -> IFactory:
        match game:
            case CdcGame.TR2013:
                return Tr2013Factory()
            case CdcGame.ROTTR:
                return RiseFactory()
            case CdcGame.SOTTR:
                return ShadowFactory()
