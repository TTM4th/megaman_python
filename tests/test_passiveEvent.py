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
        self.status = passiveEvent.ObjectStates()
        self.context = passiveEvent.VerifierContext()
        return super().setUp()
    
    """MoveVerify 衝突検知：なし"""
    def test_noColide(self):
        self.status.CatchValue(passiveEvent.ReactionStateEvents.InAir, Rect(128 - 8, 256 - 16 - 24, 16, 24))
        """辺が比較対象の辺と接する場合は衝突判定にはならない"""
        terrObjs:list[Rect] = []
        for x in range(1, 17):
            terrObjs.append(Rect(x * 16, 256 - 16, 16, 16))
        self.context.Verify(self.status, 0, 0, terrObjs)
        self.context.Drive(self.status)
        self.assertEqual(passiveEvent.ReactionStateEvents.InAir, self.status.State)
        self.assertEqual(Rect(120, 216, 16, 24),self.status.Rect)

    """MoveVerify 衝突検知：着地"""
    def test_existLandColide(self):
        self.status.CatchValue(passiveEvent.ReactionStateEvents.InAir, Rect(128 - 8, 256 - 16 - 24, 16, 24))
        terrObjs:list[Rect] = []
        for x in range(1, 17):
            terrObjs.append(Rect(x * 16, 256 - 16, 16, 16))
        self.context.Verify(self.status, 0, 1, terrObjs)
        self.context.Drive(self.status)
        self.assertEqual(passiveEvent.ReactionStateEvents.Land, self.status.State)
        self.assertEqual(Rect(120, 217, 16, 24), self.status.Rect)
        
    
    """MoveVerify 衝突検知：天井ぶつかり"""
    def test_existTopColide(self):
        self.status.CatchValue(passiveEvent.ReactionStateEvents.InAir, Rect(128 - 8, 224, 16, 24))
        terrObjs:list[Rect] = []
        for x in range(1, 17):
            terrObjs.append(Rect(x * 16, 256 - 48, 16, 16))
        self.context.Verify(self.status, 0, -1, terrObjs)
        self.context.Drive(self.status)
        self.assertEqual(passiveEvent.ReactionStateEvents.InAir, self.status.State)
        self.assertEqual(Rect(120, 224, 16, 24), self.status.Rect)
        
    """右ぶつかり MoveVerify 衝突検知：あり"""
    def test_existRightColide(self):
        self.status.CatchValue(passiveEvent.ReactionStateEvents.InAir, Rect(128 - 8, 256 - 16 - 24, 16, 24))
        terrObjs:list[Rect] = []
        for y in range(1, 17):
            terrObjs.append(Rect(128, y * 16, 16, 16))
        self.context.Verify(self.status, 0, 0, terrObjs)
        self.context.Drive(self.status)
        self.assertEqual(passiveEvent.ReactionStateEvents.InAir, self.status.State)
        self.assertEqual(Rect(112, 216, 16, 24), self.status.Rect)
    
    """左ぶつかり MoveVerify 衝突検知：あり"""
    def test_existLeftColide(self):
        self.status.CatchValue(passiveEvent.ReactionStateEvents.InAir, Rect(128 - 8, 256 - 16 - 24, 16, 24))
        terrObjs:list[Rect] = []
        for y in range(1, 17):
            terrObjs.append(Rect(112, y * 16, 16, 16))
        self.context.Verify(self.status, -1, 0, terrObjs)
        self.context.Drive(self.status)
        self.assertEqual(passiveEvent.ReactionStateEvents.InAir, self.status.State)
        self.assertEqual(Rect(128, 216, 16, 24), self.status.Rect)