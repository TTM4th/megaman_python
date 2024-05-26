from __future__ import annotations
from enum import Enum
from pygame import Rect
from collections.abc import Iterable

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
class ReactionState(Enum):
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

class ObjectStates:
    def __init__(self) -> None:
        self.ReactionState:ReactionState
        self.Rect:Rect

    def CatchValue(self, reactionState:ReactionState, rect:Rect):
        self.ReactionState = reactionState
        self.Rect = rect

class VerifierContext:
    def __init__(self) -> None:
        self._YVerifier = YAxisVerifier()
        self._XVerifier = XAxisVerifier()
        self.DeltaX:int
        self.DeltaY:int
    
    def Verify(self, objstates:ObjectStates, deltaX:int, deltaY:int, terrRects:Iterable[Rect]) -> None:
        self.DeltaX = deltaX
        self.DeltaY = deltaY
        self._YVerifier.Verify(objstates, self.DeltaY, terrRects)
        self._XVerifier.Verify(objstates, self.DeltaX, terrRects)

    def Drive(self, objstates:ObjectStates):
        self._YVerifier.Drive(objstates, self.DeltaY)
        self._XVerifier.Drive(objstates, self.DeltaX)

"""プレイヤーの1軸の進行方向から衝突検証を行うロジッククラス"""
class OneAxisVerifier:
    def __init__(self) -> None:
        self.Obj:Rect
        self._Direction:AxisDirection
    
    """各setterで取得した値・オブジェクトから、進行方向および衝突オブジェクト（None許容）の取得を行う"""
    def Verify(self, objstates:ObjectStates, delta:int, terrRects:Iterable[Rect]):
        if delta >= 0:
            self._Direction = AxisDirection.Positive
            fnc = self._PositiveFunc
        else:
            self._Direction = AxisDirection.Negative
            fnc = self._NegativeFunc
        pred = self._PredicateRectLocation(objstates.Rect, delta)
        filtered = [_ for _ in terrRects if fnc(objstates.ReactionState, pred, _)]
        self.Obj = Funcset.TestGetColidedObject(pred, filtered)

    """self._Directionが正の場合の衝突判定対象関数"""
    def _PositiveFunc(self, reactionStatus:ReactionState , rect:Rect, terrObj:Rect) -> bool:
        pass
    
    """self._Directionが負の場合の衝突判定対象関数"""
    def _NegativeFunc(self, reactionStatus:ReactionState, rect:Rect, terrObj:Rect) -> bool:
        pass
    
    """第2引数で渡した移動値に移動したRectを返す"""
    def _PredicateRectLocation(self, orgRect:Rect, delta:int) -> Rect:
        pass
    
    """Verifyで検証した結果をもとに第2引数で渡した移動値またはオブジェクトに接触しない位置まで、第1引数の位置情報を動かす"""
    def Drive(self, objstates:ObjectStates, delta:int) -> None:
        pass

"""プレイヤーのY軸進行方向から衝突検証を行うロジッククラス"""
class YAxisVerifier(OneAxisVerifier):
    def _PositiveFunc(self, reactionStatus:ReactionState, rect:Rect, terrObj: Rect) -> bool:
        if reactionStatus == ReactionState.Land:
            return False
        else:
            return Funcset.IsBottomFillter(rect, terrObj)
    
    def _NegativeFunc(self, reactionStatus:ReactionState , rect:Rect, terrObj: Rect) -> bool:
        return Funcset.IsUpperFillter(rect, terrObj)

    def _PredicateRectLocation(self, orgRect: Rect, delta: int) -> Rect:
        return orgRect.move(0, delta)
    
    def Drive(self, objstates:ObjectStates, delta:int):
        if self.Obj is not None:
            if self._Direction == AxisDirection.Positive:
                objstates.Rect.bottom = self.Obj.top + 1
                objstates.ReactionState = ReactionState.Land
            elif self._Direction == AxisDirection.Negative:
                """空中 or ハシゴ"""
                objstates.Rect.top = self.Obj.bottom
        else:
            if objstates.ReactionState == ReactionState.InAir or objstates.ReactionState == ReactionState.GrepLadder:
                """空中 or ハシゴ"""
                objstates.Rect.y += delta
            else:
                return

"""プレイヤーのX軸進行方向から衝突検証を行うロジッククラス"""
class XAxisVerifier(OneAxisVerifier):
    def _PositiveFunc(self, reactionStatus:ReactionState, rect:Rect, terrObj: Rect) -> bool:
        if reactionStatus == ReactionState.Land:
            return Funcset.IsRightFillter(rect, terrObj) and Funcset.IsLandAdditionalFillter(rect, terrObj)
        else :
            return Funcset.IsRightFillter(rect, terrObj)
    
    def _NegativeFunc(self, reactionStatus:ReactionState, rect:Rect, terrObj: Rect) -> bool:
        if reactionStatus == ReactionState.Land:
            return Funcset.IsLeftFillter(rect, terrObj) and Funcset.IsLandAdditionalFillter(rect, terrObj)
        else :
            return Funcset.IsLeftFillter(rect, terrObj)

    def _PredicateRectLocation(self, orgRect: Rect, delta: int) -> Rect:
        return orgRect.move(delta, 0)

    def Drive(self, objstates:ObjectStates, delta:int):
        if objstates.ReactionState == ReactionState.GrepLadder:
            return
        if self.Obj is not None:
            if self._Direction == AxisDirection.Positive:
                objstates.Rect.right = self.Obj.left
            elif self._Direction == AxisDirection.Negative:
                objstates.Rect.left = self.Obj.right
        else:
            if objstates.ReactionState == ReactionState.Hit:
                objstates.Rect.x += -self._Direction
            else:
                objstates.Rect.x += delta

class Funcset:

    @staticmethod
    def IsBottomFillter(playerRect:Rect, terrObj:Rect) -> bool:
        return terrObj.top < playerRect.bottom and playerRect.bottom < terrObj.bottom

    @staticmethod
    def IsUpperFillter(playerRect:Rect, terrObj:Rect) -> bool:
        return terrObj.bottom > playerRect.top and playerRect.top > terrObj.top
    
    @staticmethod
    def IsRightFillter(playerRect:Rect, terrObj:Rect) -> bool:
        return terrObj.left < playerRect.right and playerRect.right < terrObj.right
    
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
    def TestGetColidedObject(playerRect:Rect, fillteredObjs:Iterable[Rect]):
        return next((_ for _ in fillteredObjs if playerRect.colliderect(_)), None)