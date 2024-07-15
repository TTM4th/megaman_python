from unittest import TestCase
from pygame import Rect

import sys
import pathlib
path = pathlib.Path('__file__')
path /= '../' # 1つ上の階層を指す
sys.path.append(str(path.resolve()))
from megaman_python import passiveEvent

class Test_PassiveEvent(TestCase):

    def setUp(self) -> None:
        self.status = passiveEvent.PlayerStates()
        self.context = passiveEvent.ApplyContext()
        return super().setUp()
    
    """MoveVerify 衝突検知：なし"""
    def test_noColide(self):
        self.status.ReactionState = passiveEvent.ReactionState.InAir
        self.status.Rect = Rect(128 - 8, 256 - 16 - 24, 16, 24)
        """辺が比較対象の辺と接する場合は衝突判定にはならない"""
        terrObjs:list[Rect] = []
        for x in range(1, 17):
            terrObjs.append(Rect(x * 16, 256 - 16, 16, 16))
        self.context.ApplyMotion(self.status, 0, 0, terrObjs)
        self.assertEqual(passiveEvent.ReactionState.InAir, self.status.ReactionState)
        self.assertEqual(Rect(120, 216, 16, 24), self.status.Rect)

    """MoveVerify 衝突検知：着地"""
    def test_existLandColide(self):
        self.status.ReactionState = passiveEvent.ReactionState.InAir
        self.status.Rect = Rect(128 - 8, 256 - 16 - 24, 16, 24)
        terrObjs:list[Rect] = []
        for x in range(1, 17):
            terrObjs.append(Rect(x * 16, 256 - 16, 16, 16))
        self.context.ApplyMotion(self.status, 0, 1, terrObjs)
        self.assertEqual(passiveEvent.ReactionState.Land, self.status.ReactionState)
        self.assertEqual(Rect(120, 217, 16, 24), self.status.Rect)
        
    
    """MoveVerify 衝突検知：天井ぶつかり"""
    def test_existTopColide(self):
        self.status.ReactionState = passiveEvent.ReactionState.InAir
        self.status.Rect = Rect(128 - 8, 224, 16, 24)
        terrObjs:list[Rect] = []
        for x in range(1, 17):
            terrObjs.append(Rect(x * 16, 256 - 48, 16, 16))
        self.context.ApplyMotion(self.status, 0, -1, terrObjs)
        self.assertEqual(passiveEvent.ReactionState.InAir, self.status.ReactionState)
        self.assertEqual(Rect(120, 224, 16, 24), self.status.Rect)
        
    """MoveVerify 衝突検知：空中 右ぶつかり"""
    def test_existRightColide(self):
        self.status.ReactionState = passiveEvent.ReactionState.InAir
        self.status.Rect = Rect(128 - 8, 256 - 16 - 24, 16, 24)
        terrObjs:list[Rect] = []
        for y in range(1, 17):
            terrObjs.append(Rect(128, y * 16, 16, 16))
        self.context.ApplyMotion(self.status, 1, 0, terrObjs)
        self.assertEqual(passiveEvent.ReactionState.InAir, self.status.ReactionState)
        self.assertEqual(Rect(112, 216, 16, 24), self.status.Rect)
    
    """MoveVerify 衝突検知：空中 左ぶつかり"""
    def test_existLeftColide(self):
        self.status.ReactionState = passiveEvent.ReactionState.InAir
        self.status.Rect = Rect(128 - 8, 256 - 16 - 24, 16, 24)
        terrObjs:list[Rect] = []
        for y in range(1, 17):
            terrObjs.append(Rect(112, y * 16, 16, 16))
        self.context.ApplyMotion(self.status, -1, 0, terrObjs)
        self.assertEqual(passiveEvent.ReactionState.InAir, self.status.ReactionState)
        self.assertEqual(Rect(128, 216, 16, 24), self.status.Rect)

    """MoveVerify 衝突検知：着地 右ぶつかり"""
    def test_existRightColideOnLand(self):
        self.status.ReactionState = passiveEvent.ReactionState.Land
        self.status.Rect = Rect(128 - 8, 256 - 16 - 24 + 1, 16, 24)
        terrObjs:list[Rect] = []
        for x in range(1, 17):
            terrObjs.append(Rect(x * 16, 256 - 16, 16, 16))
        for y in range(1, 17):
            terrObjs.append(Rect(128, y * 16, 16, 16))
        self.context.ApplyMotion(self.status, 1, 0, terrObjs)
        self.assertEqual(passiveEvent.ReactionState.Land, self.status.ReactionState)
        self.assertEqual(Rect(112, 217, 16, 24), self.status.Rect)

    """MoveVerify 衝突検知：着地 左ぶつかり"""
    def test_existLeftColideOnLand(self):
        self.status.ReactionState = passiveEvent.ReactionState.Land
        self.status.Rect = Rect(128 - 8, 256 - 16 - 24 + 1, 16, 24)
        terrObjs:list[Rect] = []
        for x in range(1, 17):
            terrObjs.append(Rect(x * 16, 256 - 16, 16, 16))
        for y in range(1, 17):
            terrObjs.append(Rect(112, y * 16, 16, 16))
        self.context.ApplyMotion(self.status, -1, 0, terrObjs)
        self.assertEqual(passiveEvent.ReactionState.Land, self.status.ReactionState)
        self.assertEqual(Rect(128, 217, 16, 24), self.status.Rect)

    """MoveVerify 衝突検知：着地→右移動落下"""
    def test_fallRight(self):
        self.status.ReactionState = passiveEvent.ReactionState.Land
        self.status.Rect = Rect(128 - 8, 256 - 16 - 24 + 1, 16, 24)
        terrObjs:list[Rect] = []
        terrObjs.append(Rect(120 - 16, 256 - 16, 16, 16))
        self.context.ApplyMotion(self.status, 1, 0, terrObjs)
        self.assertEqual(passiveEvent.ReactionState.InAir, self.status.ReactionState)
        self.assertEqual(Rect(121, 217, 16, 24), self.status.Rect)

    """MoveVerify 衝突検知：着地→左移動落下"""
    def test_fallLeft(self):
        self.status.ReactionState = passiveEvent.ReactionState.Land
        self.status.Rect = Rect(128 - 8, 256 - 16 - 24 + 1, 16, 24)
        terrObjs:list[Rect] = []
        terrObjs.append(Rect(136, 256 - 16, 16, 16))
        self.context.ApplyMotion(self.status, -1, 0, terrObjs)
        self.assertEqual(passiveEvent.ReactionState.InAir, self.status.ReactionState)
        self.assertEqual(Rect(119, 217, 16, 24), self.status.Rect)