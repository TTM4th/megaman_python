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
        return super().setUp()
    
    """MoveVerify 衝突検知：なし"""
    def test_noColide(self):
        act = passiveEvent.MoveVerify()
        player = Rect(128 - 8, 256 - 16 - 24, 16, 24)
        """辺が比較対象の辺と接する場合は衝突判定にはならない"""
        terrObjs:list[Rect] = []
        for x in range(1, 17):
            terrObjs.append(Rect(x * 16, 256 - 16, 16, 16))
        act.Verify(player, terrObjs)
        self.assertEqual(passiveEvent.MoveStates.Neutral, act.State)

    """着地 MoveVerify 衝突検知：あり"""
    def test_existLandColide(self):
        act = passiveEvent.MoveVerify()
        player = Rect(128 - 8, 256 - 16 - 24 + 1, 16, 24)
        terrObjs:list[Rect] = []
        for x in range(1, 17):
            terrObjs.append(Rect(x * 16, 256 - 16, 16, 16))
        act.Verify(player, terrObjs)
        print(act.PredictObject)
        self.assertEqual(passiveEvent.MoveStates.Collided, act.State)
    
    """天井ぶつかり MoveVerify 衝突検知：あり"""
    def test_existTopColide(self):
        act = passiveEvent.MoveVerify()
        player = Rect(128 - 8, 256 - 16 - 24, 16, 24)
        terrObjs:list[Rect] = []
        for x in range(1, 17):
            terrObjs.append(Rect(x * 16, 256 - 32, 16, 16))
        act.Verify(player, terrObjs)
        print(act.PredictObject)
        self.assertEqual(passiveEvent.MoveStates.Collided, act.State)
        
    """右ぶつかり MoveVerify 衝突検知：あり"""
    def test_existRightColide(self):
        act = passiveEvent.MoveVerify()
        player = Rect(128 - 8, 256 - 16 - 24, 16, 24)
        terrObjs:list[Rect] = []
        for y in range(1, 17):
            terrObjs.append(Rect(128, y * 16, 16, 16))
        act.Verify(player, terrObjs)
        print(act.PredictObject)
        self.assertEqual(passiveEvent.MoveStates.Collided, act.State)
    
    """左ぶつかり MoveVerify 衝突検知：あり"""
    def test_existLeftColide(self):
        act = passiveEvent.MoveVerify()
        player = Rect(128 - 8, 256 - 16 - 24, 16, 24)
        terrObjs:list[Rect] = []
        for y in range(1, 17):
            terrObjs.append(Rect(112, y * 16, 16, 16))
        act.Verify(player, terrObjs)
        print(act.PredictObject)
        self.assertEqual(passiveEvent.MoveStates.Collided, act.State)