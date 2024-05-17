from unittest import TestCase
from pygame import locals, event

import sys
import pathlib
path = pathlib.Path('__file__')
path /= '../' # 1つ上の階層を指す
sys.path.append(str(path.resolve()))
from megaman_python import InputEvent

class Test_InputEvent(TestCase):

    def setUp(self) -> None:
        mapper = InputEvent.KeyMapper()
        mapper.AddMap(locals.K_UP, InputEvent.InputKey.Up)
        mapper.AddMap(locals.K_DOWN, InputEvent.InputKey.Down)
        mapper.AddMap(locals.K_LEFT, InputEvent.InputKey.LEFT)
        mapper.AddMap(locals.K_RIGHT, InputEvent.InputKey.RIGHT)
        mapper.AddMap(locals.K_x, InputEvent.InputKey.FIRE)
        mapper.AddMap(locals.K_z, InputEvent.InputKey.JUMP)
        self.test_mapper = mapper
        self.test_keyInput = InputEvent.KeyInput(mapper.MapKeys,
                                                 mapper.CreateKeyInputStateDictionary()
                                                 )
        return super().setUp()
    
    """
    setUpでKeyMapperに渡した値が 実際に入力したキー と ゲーム中の割当キー のペアで保存されているか
    """
    def test_Mapkeys(self):
        ans = {locals.K_UP : InputEvent.InputKey.Up,
                locals.K_DOWN : InputEvent.InputKey.Down,
                locals.K_LEFT : InputEvent.InputKey.LEFT,
                locals.K_RIGHT : InputEvent.InputKey.RIGHT,
                locals.K_x : InputEvent.InputKey.FIRE,
                locals.K_z : InputEvent.InputKey.JUMP}
        self.assertDictEqual(ans,self.test_mapper.MapKeys)
    
    """
    setUpでKeyMapperに渡した ゲーム中の割当キー と 入力状態（初期値：未入力）のペアが作成できるか
    """
    def test_CreateKeyInputStateDictionary(self):
        ans = {InputEvent.InputKey.Up : InputEvent.InputState.NoneInput,
                InputEvent.InputKey.Down : InputEvent.InputState.NoneInput,
                InputEvent.InputKey.LEFT : InputEvent.InputState.NoneInput,
                InputEvent.InputKey.RIGHT : InputEvent.InputState.NoneInput,
                InputEvent.InputKey.FIRE : InputEvent.InputState.NoneInput,
                InputEvent.InputKey.JUMP : InputEvent.InputState.NoneInput}
        self.assertDictEqual(ans, self.test_mapper.CreateKeyInputStateDictionary())
    
    """
    キー押下イベントを検知した検証対象のキーが未入力→入力開始状態に更新される
    """
    def test_InitKeyInput(self):
        params = [
            event.Event(locals.KEYDOWN, key = locals.K_UP),
            event.Event(locals.KEYDOWN, key = locals.K_DOWN),
            event.Event(locals.KEYDOWN, key = locals.K_LEFT),
            event.Event(locals.KEYDOWN, key = locals.K_RIGHT),
            event.Event(locals.KEYDOWN, key = locals.K_x),
            event.Event(locals.KEYDOWN, key = locals.K_z)
        ]
        ans = {InputEvent.InputKey.Up : InputEvent.InputState.Start,
                InputEvent.InputKey.Down : InputEvent.InputState.Start,
                InputEvent.InputKey.LEFT : InputEvent.InputState.Start,
                InputEvent.InputKey.RIGHT : InputEvent.InputState.Start,
                InputEvent.InputKey.FIRE : InputEvent.InputState.Start,
                InputEvent.InputKey.JUMP : InputEvent.InputState.Start}
        self.test_keyInput.catchInput(params)
        self.assertDictEqual(ans, self.test_keyInput.InputtedStates)