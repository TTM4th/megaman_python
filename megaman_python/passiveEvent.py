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

"""衝突有無"""
class CollideState(Enum):
    """接触無"""
    NoCollide = 0
    """正方向に接触"""
    IsCollidePositive = 1
    """負方向に接触"""
    IsCollideNegative = 2

"""Playerの状態を一元管理するクラス"""    
class PlayerStates:
    def __init__(self) -> None:
        self.Postude:Postudes
        self.ReactionState:ReactionState
        self.Rect:Rect

"""X,Y2軸の動きを反映させるためのロジックをまとめたクラス"""
class ApplyContext:
    def __init__(self) -> None:
        self._XApplier = XAxisApplier()
        self._YApplier = YAxisApplier()

    """引数で渡したPlayerStates、x移動距離、y移動距離、画面表示されているオブジェクトのRectから接触状況に応じた結果を、PlayerStatesを反映させる"""
    def ApplyMotion(self, player:PlayerStates, deltaX:int, deltaY:int, terrRects:Iterable[Rect]):
        self._XApplier.ApplyMove(player, deltaX, terrRects)
        self._YApplier.ApplyMove(player, deltaY, terrRects)
        if self._YApplier.ColideState == CollideState.IsCollidePositive:
            player.ReactionState = ReactionState.Land
        elif self._YApplier.ColideState == CollideState.NoCollide:
            player.ReactionState = ReactionState.InAir
            #player.Postude = Postudes.InAir

"""単軸の動きをPlayerStatesに反映させるためのロジッククラス"""
class OneAxisApplier:
    def __init__(self) -> None:
        self.Verifier:OneAxisVerifier
        self.ColideState:CollideState

    """引数で渡したPlayerStates、移動距離、画面表示されているオブジェクトのRectから接触状況に応じた単軸の移動結果を、PlayerStatesに反映させる"""
    def ApplyMove(self, player:PlayerStates, delta:int, terrRects:Iterable[Rect]):
        collideObj = self.Verifier.GetFirstCollideObject(player, delta, terrRects)
        if collideObj is None:
            self._NoCollideMove(player, delta)
        else:
            self._IsCollideMove(player, delta, collideObj)

    """接触オブジェクトがない場合の移動"""
    def _NoCollideMove(self, player:PlayerStates, delta:int):
        pass

    """接触オブジェクトがある場合の移動"""
    def _IsCollideMove(self, player:PlayerStates, delta:int, terrObj:Rect):
        pass

"""Y軸の動きをPlayerStatesに反映させるためのロジッククラス"""
class YAxisApplier(OneAxisApplier):
    def __init__(self) -> None:
        self.Verifier = YAxisVerifier()

    """引数で渡したPlayerStates、移動距離、画面表示されているオブジェクトのRectから接触状況に応じたY軸の移動結果を、PlayerStatesに反映させる"""
    def ApplyMove(self, player: PlayerStates, delta: int, terrRects: Iterable[Rect]):
        super().ApplyMove(player, delta, terrRects)
    
    """接触オブジェクトがない場合の移動（「接触：なし」として記録する）"""
    def _NoCollideMove(self, player: PlayerStates, delta: int):
        self.ColideState = CollideState.NoCollide
        if player.ReactionState == ReactionState.InAir or player.ReactionState == ReactionState.GrepLadder:
            """空中 or ハシゴ"""
            player.Rect.y += delta
        else:
            """地上・梯子這い上がり"""
            return
        
    """接触オブジェクトがある場合の移動（負の方向なら「接触：負の方向あり」、正の方向なら「接触：正の方向あり」として記録する）"""
    def _IsCollideMove(self, player: PlayerStates, delta: int, terrObj: Rect):
        if delta >= 0:
            self.ColideState = CollideState.IsCollidePositive
            player.Rect.bottom = terrObj.top + 1
        elif delta < 0:
            """空中 or ハシゴ"""
            self.ColideState = CollideState.IsCollideNegative
            player.Rect.top = terrObj.bottom
        else:
            return

"""X軸の動きをPlayerStatesに反映させるためのロジッククラス"""
class XAxisApplier(OneAxisApplier):
    def __init__(self) -> None:
        self.Verifier = XAxisVerifier()
    
    """引数で渡したPlayerStates、移動距離、画面表示されているオブジェクトのRectから接触状況に応じたX軸の移動結果を、PlayerStatesに反映させる"""
    def ApplyMove(self, player: PlayerStates, delta: int, terrRects: Iterable[Rect]):
        if player.ReactionState == ReactionState.GrepLadder :
            self.ColideState = CollideState.NoCollide
            return
        super().ApplyMove(player, delta, terrRects)
    
    """接触オブジェクトがない場合の移動（「接触：なし」として記録する）"""
    def _NoCollideMove(self, player: PlayerStates, delta: int):
        self.ColideState = CollideState.NoCollide
        player.Rect.x += delta

    """接触オブジェクトがある場合の移動（負の方向なら「接触：負の方向あり」、正の方向なら「接触：正の方向あり」として記録する）"""
    def _IsCollideMove(self, player: PlayerStates, delta:int, terrObj: Rect):
        if delta > 0:
            self.ColideState = CollideState.IsCollidePositive
            player.Rect.right = terrObj.left
        elif delta < 0:
            self.ColideState = CollideState.IsCollideNegative
            player.Rect.left = terrObj.right
        else:
            return

"""プレイヤーの1軸の進行方向から衝突検証を行うロジッククラス"""
class OneAxisVerifier:

    """接触した最初のオブジェクトを取得する"""
    def GetFirstCollideObject(self, player:PlayerStates, delta:int, terrRects:Iterable[Rect]):
        if delta < 0 : fnc = self._NegativeFunc
        else : fnc = self._PositiveFunc
        pred = self._PredicateRectLocation(player.Rect, delta)
        filtered = (_ for _ in terrRects if fnc(player.ReactionState, pred, _))
        return Funcset.TestGetColidedObject(pred, filtered)

    """deltaが正の場合の衝突判定対象関数"""
    def _PositiveFunc(self, reactionStatus:ReactionState , rect:Rect, terrObj:Rect) -> bool:
        pass

    """deltaが負の場合の衝突判定対象関数"""
    def _NegativeFunc(self, reactionStatus:ReactionState, rect:Rect, terrObj:Rect) -> bool:
        pass

    """第2引数で渡した移動値に移動したRectを返す"""
    def _PredicateRectLocation(self, orgRect:Rect, delta:int) -> Rect:
        pass

"""プレイヤーのY軸進行方向から衝突検証を行うロジッククラス"""
class YAxisVerifier(OneAxisVerifier):

    def _PositiveFunc(self, reactionStatus:ReactionState, rect:Rect, terrObj: Rect) -> bool:
        return Funcset.IsBottomFillter(rect, terrObj)
    
    def _NegativeFunc(self, reactionStatus:ReactionState , rect:Rect, terrObj: Rect) -> bool:
        return Funcset.IsUpperFillter(rect, terrObj)

    def _PredicateRectLocation(self, orgRect: Rect, delta: int) -> Rect:
        return orgRect.move(0, delta)

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

"""検知用接触オブジェクトを上下左右に絞るための関数セット"""
class Funcset:

    """下方向"""
    @staticmethod
    def IsBottomFillter(playerRect:Rect, terrObj:Rect) -> bool:
        return terrObj.top < playerRect.bottom and playerRect.bottom < terrObj.bottom

    """上方向"""
    @staticmethod
    def IsUpperFillter(playerRect:Rect, terrObj:Rect) -> bool:
        return terrObj.bottom > playerRect.top and playerRect.top > terrObj.top
    
    """右方向"""
    @staticmethod
    def IsRightFillter(playerRect:Rect, terrObj:Rect) -> bool:
        return terrObj.left < playerRect.right and playerRect.right < terrObj.right
    
    """左方向"""
    @staticmethod
    def IsLeftFillter(playerRect:Rect, terrObj:Rect) -> bool:
        return terrObj.right > playerRect.left and playerRect.left > terrObj.left

    """playerがLandの場合にfilter処理で追加する条件関数"""
    @staticmethod
    def IsLandAdditionalFillter(playerRect:Rect, terrObj:Rect) -> bool:
        """オブジェクトの底がプレイヤーの頭から足の間にあれば、接地時のX軸接触オブジェクト検知の対象とする"""
        return terrObj.bottom > playerRect.top and playerRect.bottom > terrObj.bottom
    
    """第1引数で渡したプレイヤーBoxが"""
    """第2引数で渡したオブジェクトに接触したオブジェクトが存在するか試しにとる"""
    """存在しない場合はNoneを返す"""
    @staticmethod
    def TestGetColidedObject(playerRect:Rect, fillteredObjs:Iterable[Rect]):
        return next((_ for _ in fillteredObjs if playerRect.colliderect(_)), None)