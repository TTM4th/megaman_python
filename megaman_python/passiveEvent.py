from __future__ import annotations
from enum import Enum
from pygame import Rect

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

"""動作時の検証フラグ"""
class MoveStates(Enum):
    """進路障害なし"""
    Neutral = 0
    """進路に衝突する障害物あり"""
    Collided = 1

"""プレイヤー移動時に衝突するオブジェクト有無の検証クラス（x, y軸の各軸に分けて検証することを想定）"""
class MoveVerify:
    def __init__(self) -> None:
        self.PredictObject:Rect
        self.State:MoveStates

    def Verify(self, playerBox:Rect, terrainObjects:list[Rect]) -> None:
        self.PredictObject = next(
            (_ for _ in terrainObjects if playerBox.colliderect(_))
            , None)
        if self.PredictObject is None:
            self.State = MoveStates.Neutral
            return
        
        self.State = MoveStates.Collided