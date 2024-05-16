from __future__ import annotations
from abc import ABCMeta, abstractmethod
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

class InputEventContoller:

    def __init__(self) -> None:
        mapper = KeyMapper()
        mapper.AddMap(locals.K_UP, InputKey.Up)
        mapper.AddMap(locals.K_DOWN, InputKey.Down)
        mapper.AddMap(locals.K_LEFT, InputKey.LEFT)
        mapper.AddMap(locals.K_RIGHT, InputKey.RIGHT)
        mapper.AddMap(locals.K_x, InputKey.FIRE)
        mapper.AddMap(locals.K_z, InputKey.JUMP)
        self.KeyInput = KeyInput(mapper.MapKeys, 
                                 mapper.CreateKeyInputStateDictionary()
                                )
        self.Actions = mapper.CreateActions()

    """入力キーの検知・検知した各種イベントに応じて入力キーの状態を更新する"""
    def AggregateEvents(self, events:list[Event]) -> None:
        self.KeyInput.catchInput(events)
        """todo:プレイヤーのリアクション処理をkeyinput.catchInputの後で受け取る"""

    """AggregateEventsで検知した入力キーの状態に応じたアクションを実行する"""
    def DoActions(self) -> None:
        for k, v in self.KeyInput.InputtedStates.items():
            act = next(_ for _ in self.Actions if _.MappedKey == k)
            if v == InputState.Start : act.Start()
            elif v == InputState.Continue : act.Continue()
            elif v == InputState.Cancel : act.Cancel()

class KeyMapper:
    def __init__(self):
        """入力キーとゲーム内使用キーの値ペア Dictionary"""
        self.MapKeys:dict[int, InputKey]

    """
    第1引数と第2引数の値ペアをMapKeysに追加する
    第1引数：入力するキー
    第2引数：マップ先 ゲーム内使用キーフラグ
    """
    def AddMap(self, inputKeyValue:int, targetMapKey:InputKey):
        self.MapKeys.Add(inputKeyValue, targetMapKey)

    """
    AddMapでマップされたMapKeysのvalues()をキーに、それぞれの入力情報（初期値：未入力）の値ペア Dictionaryを返す
    """
    def CreateKeyInputStateDictionary(self):
        return ({_ : InputState.NoneInput for _ in self.MapKeys.values() })
    
    """
    AddMapでマップされたMapKeysで設定されたゲーム内キーをマップしたInputActionsクラスのリストを返す
    """
    def CreateActions(self):
        return [IInputActions(_) for _ in self.MapKeys.values()]

class KeyInput:
    """
    第1引数： 入力キー:ゲーム内のマップ先キー dictionary
    第2引数： ゲーム内のマップ先キー:入力キー状態フラグ dictionary
    """
    def __init__(self, keyMap:dict[int, InputKey], inputStateDict:dict[InputKey, InputState]) -> None:
        """
        入力キー→ゲーム内使用キー変換用dictionary
        """
        self.__Mappedkey = keyMap
        """
        ゲーム内使用キー別の入力キー状態フラグを格納する dictionary
        """
        self.InputtedStates = inputStateDict
        
        """
        ゲーム内使用キーのリスト
        """
        self.__targetKeys = set(self.InputtedStates.keys())

    """
    引数で受け取ったイベントから入力キーを検知し、入力キー別の状態フラグを更新する
    """
    def catchInput(self, events:list[Event]) -> None:
        for value in self.InputtedStates.values() :
            if value != InputState.Cancel : continue
            value = InputState.NoneInput

        for event in filter(lambda x: (x.type == locals.KEYDOWN or x.type == locals.KEYUP)
                            and (self.__Mappedkey[x.key] in self.__targetKeys), 
                            events):
            inputtedKey = self.__Mappedkey[event.key]
            if event.type == locals.KEYUP:
                self.InputtedStates[inputtedKey] = InputState.Cancel
            elif event.type == locals.KEYDOWN:
                if self.InputtedStates[inputtedKey] == InputState.Start:
                    self.InputtedStates[inputtedKey] = InputState.Continue
                else:
                    self.InputtedStates[inputtedKey] = InputState.Start
                    
"""入力開始・継続・解除別の処理を用意したインターフェース"""
class IInputActions(metaclass = ABCMeta):
    """
    引数で指定したマップ先キーの入力開始・継続・解除別のメソッドを用意したインターフェースを生成する
    第1引数：マップ先キー
    """
    def __init__(self, mapKey):
        self.MappedKey = mapKey

    """入力開始処理"""
    @abstractmethod
    def Start(self):
        pass
    
    """入力継続"""
    @abstractmethod
    def Continue(self):
        pass
    
    """入力解除"""
    @abstractmethod
    def Cancel(self):
        pass