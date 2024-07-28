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
    """ワープ"""
    Warp = 7

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

"""接触方向フラグ"""
class ColideDirection(Enum):
    """上"""
    Upper = 1
    """下"""
    Bottom = 2
    """左"""
    Left = 3
    """右"""
    Right = 4

"""Playerの状態を一元管理するクラス"""    
class PlayerStates:
    def __init__(self) -> None:
        """プレイヤーの姿勢（外観向け：走行、空中、梯子掴み）"""
        self.Postude:Postudes
        """プレイヤーの姿勢と付加可能な姿勢（外観向け：バスター構えなど）"""
        self.AdditionalPostude:AdditionalPostudes
        """プレイヤーのリアクション状態（内部的に識別する際に使う）"""
        self.ReactionState:ReactionState
        """プレイヤーの当たり判定ボックス"""
        self.HitBox:Rect

"""X,Y2軸の動きを反映させるためのロジックをまとめたクラス"""
class ApplyContext:
    def __init__(self) -> None:
        self.blocker = ObjectBlocker()

    """引数で渡したPlayerStates、画面表示されているオブジェクトのRectから接触状況に応じた結果を、PlayerStatesを反映させる"""
    def ApplyCollide(self, player:PlayerStates, terrRects:Iterable[Rect]):
        terrs = [sender for sender in terrRects if player.HitBox.colliderect(sender)]

        vertical = ColideDirectionFillter.GetColidedByVerticalBlocks(player.HitBox, terrs)
        player.ReactionState = ReactionState.Land if any(vertical[ColideDirection.Bottom]) else ReactionState.InAir
        self.blocker.BlockByVertical(player.HitBox, vertical)

        if player.ReactionState == ReactionState.Land:
            #上下接触したオブジェクトを除外したいんだけど、ここLinqでいうexceptが欲しい
            flatten = [terr for exterrObjs in vertical.values() for terr in exterrObjs]
            terrs = [terr for terr in terrs if terr not in flatten]
            holizonal = ColideDirectionFillter.GetColidedByHolizonalBlocks(player.HitBox,terrs)
            del(flatten)
        else:
            holizonal = ColideDirectionFillter.GetColidedByHolizonalBlocks(player.HitBox, terrs)
        self.blocker.BlockByHolizonal(player.HitBox, holizonal)
        
        del(vertical)
        del(holizonal)
        del(terrs)

"""接触を受けたオブジェクトの位置を接触したオブジェクト"""
class ObjectBlocker:
    def __init__(self) -> None:
        """[Key:垂直方向（上下） Value:方向に応じた実行したいメソッド]をマップするDictionary"""
        self.__MappedVerticalAction:dict[ColideDirection, Callable[[Rect, Rect], None]] = {
            ColideDirection.Bottom:BlockLocation.ContactBottom,
            ColideDirection.Upper:BlockLocation.ContactUpper,
        }
        """[Key:水平方向（左右） Value:方向に応じて実行したいメソッド]をマップするDictionary"""
        self.__MappedHolizonalAction:dict[ColideDirection, Callable[[Rect, Rect], None]] ={
            ColideDirection.Left:BlockLocation.ContactLeft,
            ColideDirection.Right:BlockLocation.ContactRight
        }

    """第1引数で受け取ったRectが"""
    """第2引数の接触対象のRect配列から垂直方向に接触したオブジェクトがあれば"""
    """接触したオブジェクトから受けた方向に応じて垂直方向に塞がれた場合の位置を第1引数のRectに反映させる"""
    def BlockByVertical(self, reciever:Rect, vertical:dict[ColideDirection, Iterable[Rect]]) -> None:
        if any(vertical.values()) : self.__ExecuteActions(reciever, vertical, self.__MappedVerticalAction)

    """第1引数で受け取ったRectが"""
    """第2引数の接触対象のRect配列から水平方向に接触したオブジェクトがあれば"""
    """接触したオブジェクトから受けた方向に応じて水平方向に塞がれた場合の位置を第1引数のRectに反映させる"""
    def BlockByHolizonal(self, reciever:Rect, holizonal:dict[ColideDirection, Iterable[Rect]]) -> None:
        if any(holizonal.values()) : self.__ExecuteActions(reciever, holizonal, self.__MappedHolizonalAction)

    """第1引数で受け取ったRectが"""
    """第2引数の接触対象のRect配列から接触したオブジェクトがあれば"""
    """第3引数で渡した接触方向に応じてマッピングしたメソッドを実行する"""
    def __ExecuteActions(self, reciever:Rect, senders:dict[ColideDirection, Iterable[Rect]], actions:dict[ColideDirection, Callable[[Rect, Rect], None]]) -> None:
        for key, value in senders.items():
            if not(any(value)) : continue
            obj = next(value, None)
            if obj == None : continue
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

"""検知用接触オブジェクトを上下左右に絞るための関数セット"""
class ColideDirectionFillter:

    """引数で受け取った接触オブジェクトを水平方向で接触したものに絞り込む"""
    @staticmethod
    def GetColidedByHolizonalBlocks(reciever:Rect, colidedSenders:Iterable[Rect]):
        return {
            ColideDirection.Left:ColideDirectionFillter.GetColideObjcts(reciever, colidedSenders, ColideDirectionFillter.IsLeftFillter), 
            ColideDirection.Right:ColideDirectionFillter.GetColideObjcts(reciever, colidedSenders, ColideDirectionFillter.IsRightFillter)
            }

    """引数で受け取った接触オブジェクトを垂直方向で接触したものに絞り込む"""
    @staticmethod
    def GetColidedByVerticalBlocks(reciever:Rect, colidedSenders:Iterable[Rect]):
        return {
            ColideDirection.Upper:ColideDirectionFillter.GetColideObjcts(reciever, colidedSenders, ColideDirectionFillter.IsUpperFillter), 
            ColideDirection.Bottom:ColideDirectionFillter.GetColideObjcts(reciever, colidedSenders, ColideDirectionFillter.IsBottomFillter)
            }

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

    """第1引数で指定したrecieverが"""
    """第2引数で指定したsendersの中から"""
    """第3引数で指定したpred関数を通じてtrueだったRectオブジェクトを引っ張り出す"""
    @staticmethod
    def GetColideObjcts(reciever:Rect, senders:Iterable[Rect], pred:Callable[[Rect, Rect], bool]):
        return (sender for sender in senders if pred(reciever, sender))

    """（参考）playerがLandの場合にfilter処理で追加する条件関数"""
    @staticmethod
    def IsLandAdditionalFillter(playerRect:Rect, terrObj:Rect) -> bool:
        """オブジェクトの底がプレイヤーの頭から足の間にあれば、接地時のX軸接触オブジェクト検知の対象とする"""
        return terrObj.bottom > playerRect.top and playerRect.bottom > terrObj.bottom
