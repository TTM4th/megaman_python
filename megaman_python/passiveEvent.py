from __future__ import annotations
from enum import Enum
from pygame import Rect
from collections.abc import Iterable, Callable

"""
イベントの開始・継続・キャンセル状態フラグ
"""
class EventState(Enum):
    NotRaised = 0
    """未発生"""
    
    Start = 1
    """イベント開始"""
    
    Continue = 2
    """イベント継続"""
    
    Cancel = 3
    """イベント解除"""

class PlayerParameter(Enum):
    Health = 28
    """初期体力"""

class PlayerStatusTimeFrame(Enum):
    HitKnockBack = 60
    """被弾のけぞりフレーム"""
    
    Invisible = 120
    """無敵時間フレーム"""
    
    Crawling = 6
    """梯子這い上がり時間フレーム"""
    
    Step = 6
    """直立→走り出しの踏み込み時間フレーム"""
    
    Fire= 15
    """発射姿勢をとるフレーム"""
    
    Jumping = 20
    """ジャンプ有効時間フレーム"""

class PlayerAnimeTimeFrame(Enum):
    StandingAnime = 180
    """直立まばたき1ループ時間フレーム"""
    
    RunAnime = 32
    """走行アニメ１ループ時間フレーム"""
    
    ClimbAnime = 20
    """梯子登り １ループ時間フレーム"""

"""プレイヤー姿勢種別"""
class Postudes(Enum):
    Stand = 0
    """直立"""
    
    InAir = 1
    """空中"""
    
    Stepping = 2
    """踏み込み"""
    
    Running = 3
    """走行"""
    
    GrepLadder = 4
    """梯子掴み"""
    
    CrawLing = 5
    """梯子這い上がり"""
    
    BendBack = 6
    """のけぞり"""
    
    Warp = 7
    """ワープ"""

"""Posutudesと同時に混在させられる姿勢"""
class AdditionalPostudes(Enum):
    Neutral = 0
    """構えなし"""
    Fire = 1
    """バスター構え"""
    Hold = 2
    """抱え込み"""
    Throw = 3
    """投げ"""

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
    Neutral = 0
    """何もなし"""
    
    Hit = 1
    """被弾"""

    Blink = 2
    """点滅"""

"""接触方向フラグ"""
class ColideDirection(Enum):
    Upper = 1
    """上"""

    Bottom = 2
    """下"""
    
    Left = 3
    """左"""

    Right = 4
    """右"""

"""Playerの状態を一元管理するクラス"""    
class PlayerStates:
    def __init__(self) -> None:
        self.Postude:Postudes
        """プレイヤーの姿勢（外観向け：走行、空中、梯子掴み）"""

        self.AdditionalPostude:AdditionalPostudes
        """プレイヤーの姿勢と付加可能な姿勢（外観向け：バスター構えなど）"""

        self.ReactionState:ReactionState
        """プレイヤーのリアクション状態（内部的に識別する際に使う）"""

        self.HitBox:Rect
        """プレイヤーの当たり判定ボックス"""
        
        self.PrintEffect = PrintEffects.Neutral
        """表示効果"""

        self.Health = PlayerParameter.Health
        """プレイヤー体力"""

"""X,Y2軸の動きを反映させるためのロジックをまとめたクラス"""
class ApplyContext:
    def __init__(self) -> None:
        self.blocker = ObjectBlocker()

    def ApplyCollide(self, player:PlayerStates, terrRects:Iterable[Rect]):
        """引数で渡したPlayerStates、画面表示されているオブジェクトのRectから接触状況に応じた結果を、PlayerStatesを反映させる"""
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

    """"""
    def ApplyHit(self, player:PlayerStates, enemyRects:Iterable[Rect], enemyAttack:int):
        enemies = next((sender for sender in enemyRects if player.HitBox.collidedict(sender)), None)
        if enemies == None or player.ReactionState == ReactionState.Hit : pass
        player.ReactionState = ReactionState.Hit
        player.Health -= enemyAttack
        player.Postude = Postudes.BendBack
        player.PrintEffect = PrintEffects.Hit

"""接触を受けたオブジェクトの位置を接触したオブジェクト"""
class ObjectBlocker:
    def __init__(self) -> None:
        self.__MappedVerticalAction:dict[ColideDirection, Callable[[Rect, Rect], None]] = {
            ColideDirection.Bottom:BlockLocation.ContactBottom,
            ColideDirection.Upper:BlockLocation.ContactUpper,
        }
        """[Key:垂直方向（上下） Value:方向に応じた実行したいメソッド]をマップするDictionary"""
        self.__MappedHolizonalAction:dict[ColideDirection, Callable[[Rect, Rect], None]] ={
            ColideDirection.Left:BlockLocation.ContactLeft,
            ColideDirection.Right:BlockLocation.ContactRight
        }
        """[Key:水平方向（左右） Value:方向に応じて実行したいメソッド]をマップするDictionary"""

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
        
class BlockLocation:
    """第1引数のRectが第2引数のRectからふさがれた方向に応じた位置座標に更新する"""

    @staticmethod
    def ContactBottom(reciever:Rect, sender:Rect) -> None:
        """下方向"""
        reciever.bottom = sender.top + 1 

    @staticmethod
    def ContactUpper(recievier:Rect, sender:Rect) -> None:
        """上方向"""
        recievier.top = sender.bottom

    @staticmethod
    def ContactRight(reciever:Rect, sender:Rect) -> None:
        """右方向"""
        reciever.right = sender.left
    
    @staticmethod
    def ContactLeft(reciever:Rect, sender:Rect) -> None:
        """左方向"""
        reciever.left = sender.right

class ColideDirectionFillter:
    """検知用接触オブジェクトを上下左右に絞るための関数セット"""

    @staticmethod
    def GetColidedByHolizonalBlocks(reciever:Rect, colidedSenders:Iterable[Rect]):
        """引数で受け取った接触オブジェクトを水平方向で接触したものに絞り込む"""
        return {
            ColideDirection.Left:ColideDirectionFillter.GetColideObjcts(reciever, colidedSenders, ColideDirectionFillter.IsLeftFillter), 
            ColideDirection.Right:ColideDirectionFillter.GetColideObjcts(reciever, colidedSenders, ColideDirectionFillter.IsRightFillter)
            }

    @staticmethod
    def GetColidedByVerticalBlocks(reciever:Rect, colidedSenders:Iterable[Rect]):
        """引数で受け取った接触オブジェクトを垂直方向で接触したものに絞り込む"""
        return {
            ColideDirection.Upper:ColideDirectionFillter.GetColideObjcts(reciever, colidedSenders, ColideDirectionFillter.IsUpperFillter), 
            ColideDirection.Bottom:ColideDirectionFillter.GetColideObjcts(reciever, colidedSenders, ColideDirectionFillter.IsBottomFillter)
            }

    @staticmethod
    def IsBottomFillter(reciever:Rect, sender:Rect) -> bool:
        """下方向：範囲"""
        return sender.top < reciever.bottom and reciever.bottom < sender.bottom

    @staticmethod
    def IsUpperFillter(reciever:Rect, sender:Rect) -> bool:
        """上方向：範囲"""
        return sender.bottom > reciever.top and reciever.top > sender.top
    
    @staticmethod
    def IsRightFillter(reciever:Rect, sender:Rect) -> bool:
        """右方向：範囲"""
        return sender.left < reciever.right and reciever.right < sender.right
    
    @staticmethod
    def IsLeftFillter(reciever:Rect, sender:Rect) -> bool:
        """左方向：範囲"""
        return sender.right > reciever.left and reciever.left > sender.left

    """第1引数で指定したrecieverが"""
    """第2引数で指定したsendersの中から"""
    """第3引数で指定したpred関数を通じてtrueだったRectオブジェクトを引っ張り出す"""
    @staticmethod
    def GetColideObjcts(reciever:Rect, senders:Iterable[Rect], pred:Callable[[Rect, Rect], bool]):
        return (sender for sender in senders if pred(reciever, sender))
