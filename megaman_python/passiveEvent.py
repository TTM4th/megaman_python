from __future__ import annotations
from enum import Enum
from pygame import Rect
from collections.abc import Iterator

"""
イベントの開始・継続・キャンセル状態フラグ
"""
class EventState(Enum):
    """未発生"""
    NotRaised = 0
    """イベント開始"""
    Start = 1
    """イベント継続"""
    Continue = 2
    """イベント解除"""
    Cancel = 3

"""プレイヤー姿勢種別"""
class Postudes(Enum):
    """直立"""
    Stand = 0
    """空中"""
    InAir = 1
    """走行"""
    Running = 3
    """梯子掴み"""
    GrepLadder = 4
    """梯子這い上がり"""
    CrawLing = 5
    """のけぞり"""
    BendBack = 6

"""Posutudesと同時に混在させられる姿勢"""
class AdditionalPostudes(Enum):
    """構えなし"""
    Neutral = 0
    """バスター構え"""
    Fire = 1
    """抱え込み"""
    Hold = 2
    """投げ"""
    Throw = 3

"""周りから受けたことによるプレイヤーのリアクション状態"""
class ReactionStateEvents(Enum):
    """着地"""
    Land = 0
    """空中"""
    InAir = 1
    """梯子掴み"""
    GrepLadder = 2
    """被弾"""
    Hit = 3

"""プレイヤーの表示効果"""
class PrintEffects(Enum):
    """何もなし"""
    Neutral = 0
    """被弾"""
    Hit = 1
    """点滅"""
    Blink = 2

"""1軸の進行方向"""
class AxisDirection(Enum):
    """負"""
    Negative = -1
    """正"""
    Positive = 1

class VerifierContext:
    def __init__(self) -> None:
        self._YVerifier = YAxisVerifier()
        self._XVerifier = XAxisVerifier()
        self.State = self._YVerifier.State

    def updateYVerifier(self, vy, playerRect, state, terrRects):
        self._YVerifier.Delta = vy
        self._YVerifier.PlayerRect = playerRect
        self._YVerifier.State = state
        self._YVerifier.TerrRects = terrRects

    def UpdateXVerifier(self, vx, playerRect, state, terrRects):
        self._XVerifier.Delta = vx
        self._XVerifier.PlayerRect = playerRect
        self._XVerifier.State = state
        self._XVerifier.TerrRects = terrRects
    
    def YVerify(self) -> None:
        if self._YVerifier.Obj is not None:
            if self._YVerifier.Direction == AxisDirection.Positive:
                self._YVerifier.PlayerRect.bottom = self._YVerifier.Obj.top + 1
                self.State = ReactionStateEvents.Land
            elif self._YVerifier.Direction == AxisDirection.Negative:
                self._YVerifier.PlayerRect.top = self._YVerifier.Obj.bottom
                """空中 or ハシゴ"""
        else:
            if self.State == ReactionStateEvents.InAir or self.State == ReactionStateEvents.GrepLadder:
                """空中 or ハシゴ"""
                self._YVerifier.PlayerRect.y = self._YVerifier.Delta
            else:
                return

    def XVerify(self) -> None:
        if self._XVerifier.State == ReactionStateEvents.GrepLadder:
            return
        if self._XVerifier.Obj is not None:
            if self._XVerifier.Direction == AxisDirection.Positive:
                self._XVerifier.PlayerRect.right = self._XVerifier.Obj.left
            elif self._XVerifier.Direction == AxisDirection.Negative:
                self._XVerifier.PlayerRect.left = self._XVerifier.Obj.right
        else:
            if self._XVerifier.State == ReactionStateEvents.Hit:
                if self._XVerifier.Direction == AxisDirection.Positive:
                    self._XVerifier.PlayerRect.x -= 1
                elif self._XVerifier.Direction == AxisDirection.Negative:
                    self._XVerifier.PlayerRect.x += 1
            else:
                self._XVerifier.PlayerRect.x = self._XVerifier.Delta

"""プレイヤーの1軸の進行方向から衝突検証を行うロジッククラス"""
class OneAxisVerifier:
    def __init__(self) -> None:
        self.Delta:int
        self.PlayerRect:Rect
        self._TerrRects:Rect
        self.State:ReactionStateEvents = ReactionStateEvents.InAir
        self.Direction:AxisDirection = AxisDirection.Positive
        self.Obj:Rect

    """画面上地形オブジェクトのsetter"""
    @TerrRects.setter
    def TerrRects(self, terrRects:Iterator[Rect]):
        self._TerrRects = terrRects
    
    """各setterで取得した値・オブジェクトから、進行方向および衝突オブジェクト（None許容）の取得を行う"""
    def Verify(self):
        if self.Delta >= 0:
            self.Direction = AxisDirection.Positive
            fnc = self.__PositiveFunc
        else:
            self.Direction = AxisDirection.Negative
            fnc = self.__NegativeFunc
        filtered = (_ for _ in self._TerrRects if fnc(self.PlayerRect, _))
        self.Obj = Funcset.TestGetColidedObject(self.PlayerRect, filtered)

    """self.Directionが正の場合の衝突判定対象関数"""
    def __PositiveFunc(self, playerRect:Rect, terrObj:Rect) -> bool:
        return False
    
    """self.Directionが負の場合の衝突判定対象関数"""
    def __NegativeFunc(self, playerRect:Rect, terrObj:Rect) -> bool:
        return False

"""プレイヤーのY軸進行方向から衝突検証を行うロジッククラス"""
class YAxisVerifier(OneAxisVerifier):
    def __PositiveFunc(self, playerRect: Rect, terrObj: Rect) -> bool:
        if self.State == ReactionStateEvents.Land:
            return False
        else:
            return Funcset.IsBottomFillter(playerRect, terrObj)
    
    def __NegativeFunc(self, playerRect: Rect, terrObj: Rect) -> bool:
        return Funcset.IsUpperFillter(playerRect, terrObj)

"""プレイヤーのX軸進行方向から衝突検証を行うロジッククラス"""
class XAxisVerifier(OneAxisVerifier):
    def __PositiveFunc(self, playerRect: Rect, terrObj: Rect) -> bool:
        if self.State == ReactionStateEvents.Land:
            return Funcset.IsRightFillter(playerRect, terrObj) and Funcset.IsLandAdditionalFillter(playerRect, terrObj)
        else :
            return Funcset.IsRightFillter(playerRect, terrObj)
    
    def __NegativeFunc(self, playerRect: Rect, terrObj: Rect) -> bool:
        if self.State == ReactionStateEvents.Land:
            return Funcset.IsLeftFillter(playerRect, terrObj) and Funcset.IsLandAdditionalFillter(playerRect, terrObj)
        else :
            return Funcset.IsLeftFillter(playerRect, terrObj)
        
class Funcset:

    @staticmethod
    def IsBottomFillter(playerRect:Rect, terrObj:Rect) -> bool:
        return terrObj.top < playerRect.bottom and playerRect.bottom < terrObj.bottom

    @staticmethod
    def IsUpperFillter(playerRect:Rect, terrObj:Rect) -> bool:
        return terrObj.bottom > playerRect.top and playerRect.top > terrObj.top
    
    @staticmethod
    def IsRightFillter(playerRect:Rect, terrObj:Rect) -> bool:
        return terrObj.left < playerRect.right and playerRect.right < terrObj.left
    
    @staticmethod
    def IsLeftFillter(playerRect:Rect, terrObj:Rect) -> bool:
        return terrObj.right > playerRect.left and playerRect.left > terrObj.left

    """playerがLandの場合にfilter処理で追加する条件関数"""
    @staticmethod
    def IsLandAdditionalFillter(playerRect:Rect, terrObj:Rect) -> bool:
        return playerRect.bottom > terrObj.bottom > playerRect.top
    
    """第1引数で渡したプレイヤーBoxが"""
    """第2引数で渡したオブジェクトに接触したオブジェクトが存在するか試しにとる"""
    """存在しない場合はNoneを返す"""
    @staticmethod
    def TestGetColidedObject(playerRect:Rect, fillteredObjs:Iterator[Rect]):
        return next((_ for _ in fillteredObjs if playerRect.colliderect(_)), None)