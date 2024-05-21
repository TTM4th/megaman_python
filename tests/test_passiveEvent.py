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
        player = Rect(128 - 8, 256 - 16 - 24, 16, 24)
        """辺が比較対象の辺と接する場合は衝突判定にはならない"""
        terrObjs:list[Rect] = []
        for x in range(1, 17):
            terrObjs.append(Rect(x * 16, 256 - 16, 16, 16))

    """MoveVerify 衝突検知：着地"""
    def test_existLandColide(self):
        player = Rect(128 - 8, 256 - 16 - 24 + 1, 16, 24)
        terrObjs:list[Rect] = []
        for x in range(1, 17):
            terrObjs.append(Rect(x * 16, 256 - 16, 16, 16))
        expect = Rect(120, 217, 16, 24)
        
    
    """MoveVerify 衝突検知：天井ぶつかり"""
    def test_existTopColide(self):
        player = Rect(128 - 8, 256 - 16 - 24, 16, 24)
        terrObjs:list[Rect] = []
        for x in range(1, 17):
            terrObjs.append(Rect(x * 16, 256 - 48, 16, 16))
        expect = Rect(120, 224, 16, 24)
        
    """右ぶつかり MoveVerify 衝突検知：あり"""
    def test_existRightColide(self):
        player = Rect(128 - 8, 256 - 16 - 24, 16, 24)
        terrObjs:list[Rect] = []
        for y in range(1, 17):
            terrObjs.append(Rect(128, y * 16, 16, 16))
        expect = Rect(112, 216, 16, 24)
    
    """左ぶつかり MoveVerify 衝突検知：あり"""
    def test_existLeftColide(self):
        player = Rect(128 - 8, 256 - 16 - 24, 16, 24)
        terrObjs:list[Rect] = []
        for y in range(1, 17):
            terrObjs.append(Rect(112, y * 16, 16, 16))
        exepct = Rect(128, 216, 16, 24)