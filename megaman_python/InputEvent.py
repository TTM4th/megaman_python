"""
コントローラーのキー を ゲーム内で使用するキーにマップし、
入力されたコントローラーのキーから、ゲーム内で使用するするキーに仮想化したキー入力状態を検知する
"""
from __future__ import annotations
from collections.abc import Iterator
from pygame import locals
from pygame.event import Event
from enum import Enum

"""
ゲーム内使用キーフラグ
"""
class InputKey(Enum):
    """上"""
    Up = 0
    """下"""
    Down = 1
    """左"""
    LEFT = 2
    """右"""
    RIGHT = 3
    """バスター発射"""
    FIRE = 4
    """ジャンプ"""
    JUMP = 5

"""
入力キーの開始・継続・キャンセル状態フラグ
"""
class InputState(Enum):
    """未入力"""
    NoneInput = 0
    """入力開始"""
    Start = 1
    """入力継続"""
    Continue = 2
    """入力解除"""
    Cancel = 3

class KeyInput:
    """
    第1引数： 入力キー:ゲーム内のマップ先キー dictionary
    第2引数： ゲーム内のマップ先キー:入力キー状態フラグ dictionary
    """
    def __init__(self, keyMap:dict[int, InputKey]) -> None:
        """入力キー→ゲーム内使用キー変換用dictionary"""
        self.__Mappedkey = keyMap

        """ゲーム内使用キー別の入力キー状態フラグを格納する dictionary"""
        self.InputtedStates = {_ : InputState.NoneInput for _ in self.__Mappedkey.values() }
        
        """ゲーム内使用キーのリスト"""
        self.__targetKeys = set(self.InputtedStates.keys())

        """キー離した場合の変換後ステータス"""
        self.__KEYUPStates = {
            InputState.Start:InputState.Cancel,
            InputState.Continue:InputState.Cancel,
            InputState.Cancel:InputState.NoneInput
            }
        
        """キー押下した場合の変換後ステータス"""
        self.__KEYDownStates = {
            InputState.Start:InputState.Continue,
            InputState.NoneInput:InputState.Start,
            InputState.Cancel:InputState.Start
        }

    """
    引数で受け取ったイベントから入力キーを検知し、入力キー別の状態フラグを更新する
    """
    def CatchInput(self, events:Iterator[Event]) -> None:
        #キー入力イベントが空の場合
        for key in self.__targetKeys:
            if self.InputtedStates[key] == InputState.Cancel:
                self.InputtedStates[key] = InputState.NoneInput
        #キー入力イベントがある場合
        for event in filter(lambda x: (self.__Mappedkey[x.key] in self.__targetKeys), 
                            events):
            inputtedKey = self.__Mappedkey[event.key]
            evalInput = self.InputtedStates[inputtedKey]
            if event.type == locals.KEYUP:
                if evalInput == InputState.NoneInput:continue
                self.InputtedStates[inputtedKey] = self.__KEYUPStates[evalInput]
            elif event.type == locals.KEYDOWN:
                if evalInput == InputState.Continue:continue
                self.InputtedStates[inputtedKey] = self.__KEYDownStates[evalInput]

class KeyMapper:
    def __init__(self):
        """入力キーとゲーム内使用キーの値ペア Dictionary"""
        self.MapKeys:dict[int, InputKey] = dict()

    """
    第1引数と第2引数の値ペアをMapKeysに追加する
    第1引数：入力するキー
    第2引数：マップ先 ゲーム内使用キーフラグ
    """
    def AddMap(self, inputKeyValue:int, targetMapKey:InputKey):
        self.MapKeys[inputKeyValue] = targetMapKey

class HolizonalCalcVelocity():
    def __init__(self) -> None:
        self.__MOVEXVELOCITY = 1

    def StartAndContinue(self) -> int:
        return self.__MOVEXVELOCITY
    
    def CancelAndNone(self) -> int:
        return 0

class ActionCounter():
    
    def __init__(self) -> None:
        self.Timer = 0

    """開始時に実行するメソッド"""
    def Start(self) -> None:
        self.Timer = 1
    
    """継続時に実行するメソッド"""
    def Continue(self) -> None:
        self.Timer += 1
    
    """キャンセル時に実行するメソッド"""
    def Cancel(self) -> None:
        self.Timer = 0

class StandCounter(ActionCounter):

    def __init__(self) -> None:
        self.__STANDMAXTIME = 180

    def Continue(self) -> None:
        super().Continue()
        if self.Timer > self.__STANDMAXTIME:
            self.Timer -= self.__STANDMAXTIME

class RunningCounter(ActionCounter):

    def __init__(self) -> None:
        self.__RUNNINGMAXTIME = 32

    def Continue(self) -> None:
        super().Continue()
        if self.Timer > self.__RUNNINGMAXTIME:
            self.Timer -= self.__RUNNINGMAXTIME

class ClimbingCounter(ActionCounter):

    def __init__(self) -> None:
        self.__CLIMBMAXFRAME = 20
    
    def Continue(self) -> None:
        super().Continue()
        if self.Timer > self.__CLIMBMAXFRAME:
            self.Timer -= self.__CLIMBMAXFRAME