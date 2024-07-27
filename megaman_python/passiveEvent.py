from __future__ import annotations
from enum import Enum
from pygame import Rect
from collections.abc import Iterable, Callable

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
        self.blocker = ObjectBlocker()

    """引数で渡したPlayerStates、x移動距離、y移動距離、画面表示されているオブジェクトのRectから接触状況に応じた結果を、PlayerStatesを反映させる"""
    def ApplyMotion(self, player:PlayerStates, deltaX:int, deltaY:int, terrRects:Iterable[Rect]):
        reciever = player.Rect.move(deltaX, deltaY)
        terrs = [sender for sender in terrRects if reciever.colliderect(sender)]

        vertical = ColideDirectionFillter.GetColidedByVerticalBlocks(reciever, terrs)
        if any(vertical[ColideDirection.Bottom]):
            player.ReactionState = ReactionState.Land
        else:
            player.ReactionState = ReactionState.InAir
        self.blocker.BlockByVertical(reciever, vertical)

        if player.ReactionState == ReactionState.Land:
            #ここLinqでいうexceptが欲しい
            for list in vertical.values():
                for val in list:terrs.remove(val)
            holizonal = ColideDirectionFillter.GetColidedByHolizonalBlocks(reciever, terrs)
        else:
            holizonal = ColideDirectionFillter.GetColidedByHolizonalBlocks(reciever, terrs)
        self.blocker.BlockByHolizonal(reciever, holizonal)
        
        player.Rect = reciever
        del(vertical)
        del(holizonal)
        del(terrs)
        del(reciever)

"""接触を受けたオブジェクトの位置を接触したオブジェクト"""
class ObjectBlocker:
    def __init__(self) -> None:
        self.__VerticalActionDictionary:dict[ColideDirection, Callable[[Rect, Rect], None]] = {
            ColideDirection.Bottom:BlockLocation.ContactBottom,
            ColideDirection.Upper:BlockLocation.ContactUpper,
        }
        self.__HolizonalActionDictionary:dict[ColideDirection, Callable[[Rect, Rect], None]] ={
            ColideDirection.Left:BlockLocation.ContactLeft,
            ColideDirection.Right:BlockLocation.ContactRight
        }

    """第1引数で受け取ったRectが"""
    """第2引数の接触対象のRect配列から接触したオブジェクトがあれば"""
    """接触したオブジェクトから受けた方向に応じて塞がれた場合の位置を第1引数のRectに反映させる"""
    def BlockByVertical(self, reciever:Rect, vertical:dict[ColideDirection, Iterable[Rect]]) -> None:
        if any(vertical.values()) : self.__ApplyBlock(reciever, vertical, self.__VerticalActionDictionary)

    """第1引数で受け取ったRectが"""
    """第2引数の接触対象のRect配列から接触したオブジェクトがあれば"""
    """接触したオブジェクトから受けた方向に応じて塞がれた場合の位置を第1引数のRectに反映させる"""
    def BlockByHolizonal(self, reciever:Rect, holizonal:dict[ColideDirection, Iterable[Rect]]) -> None:
        if any(holizonal.values()) : self.__ApplyBlock(reciever, holizonal, self.__HolizonalActionDictionary)

    def __ApplyBlock(self, reciever:Rect, senders:dict[ColideDirection, Iterable[Rect]], actions:dict[ColideDirection, Callable[[Rect, Rect], None]]):
        for key, value in senders.items():
            if not(any(value)) : continue
            obj = next(value, None)
            if obj == None : continue
            else:
                actions[key](reciever, obj)
                break
        

"""第1引数のRectが第2引数のRectからふさがれた方向に応じた位置座標に更新する"""
class BlockLocation:

    """下方向"""
    @staticmethod
    def ContactBottom(reciever:Rect, sender:Rect) -> None:
        reciever.bottom = sender.top + 1 

    """上方向"""
    @staticmethod
    def ContactUpper(recievier:Rect, sender:Rect) -> None:
        recievier.top = sender.bottom

    """右方向"""
    @staticmethod
    def ContactRight(reciever:Rect, sender:Rect) -> None:
        reciever.right = sender.left
    
    """左方向"""
    @staticmethod
    def ContactLeft(reciever:Rect, sender:Rect) -> None:
        reciever.left = sender.right

class ColideDirection(Enum):
    Upper = 1
    Bottom = 2
    Left = 3
    Right = 4

"""検知用接触オブジェクトを上下左右に絞るための関数セット"""
class ColideDirectionFillter:

    @staticmethod
    def GetColidedByHolizonalBlocks(reciever:Rect, colidedSenders:Iterable[Rect]):
        lefts = ColideDirectionFillter.GetColideObjcts(reciever, colidedSenders, ColideDirectionFillter.IsLeftFillter)
        rights = ColideDirectionFillter.GetColideObjcts(reciever, colidedSenders, ColideDirectionFillter.IsRightFillter)
        return {ColideDirection.Left:lefts, ColideDirection.Right:rights}

    @staticmethod
    def GetColidedByVerticalBlocks(reciever:Rect, colidedSenders:Iterable[Rect]):
        uppers = ColideDirectionFillter.GetColideObjcts(reciever, colidedSenders, ColideDirectionFillter.IsUpperFillter)
        bottoms = ColideDirectionFillter.GetColideObjcts(reciever, colidedSenders, ColideDirectionFillter.IsBottomFillter)
        return {ColideDirection.Upper:uppers, ColideDirection.Bottom:bottoms}

    """下方向：範囲"""
    @staticmethod
    def IsBottomFillter(reciever:Rect, sender:Rect) -> bool:
        return sender.top < reciever.bottom and reciever.bottom < sender.bottom

    """上方向：範囲"""
    @staticmethod
    def IsUpperFillter(reciever:Rect, sender:Rect) -> bool:
        return sender.bottom > reciever.top and reciever.top > sender.top
    
    """右方向：範囲"""
    @staticmethod
    def IsRightFillter(reciever:Rect, sender:Rect) -> bool:
        return sender.left < reciever.right and reciever.right < sender.right
    
    """左方向：範囲"""
    @staticmethod
    def IsLeftFillter(reciever:Rect, sender:Rect) -> bool:
        return sender.right > reciever.left and reciever.left > sender.left

    """playerがLandの場合にfilter処理で追加する条件関数"""
    @staticmethod
    def IsLandAdditionalFillter(playerRect:Rect, terrObj:Rect) -> bool:
        """オブジェクトの底がプレイヤーの頭から足の間にあれば、接地時のX軸接触オブジェクト検知の対象とする"""
        return terrObj.bottom > playerRect.top and playerRect.bottom > terrObj.bottom

    """第1引数で指定したrecieverが"""
    """第2引数で指定したsendersの中から"""
    """第3引数で指定したpred関数を通じてtrueだったRectオブジェクトを引っ張り出す"""
    @staticmethod
    def GetColideObjcts(reciever:Rect, senders:Iterable[Rect], pred:Callable[[Rect, Rect], bool]):
        return (sender for sender in senders if pred(reciever, sender))
