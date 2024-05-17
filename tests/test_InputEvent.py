from unittest import TestCase
from megaman_python import InputEvent
from pygame import locals
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
        return super().setUp()
    
    def test_createKeyInputStateDictionary(self):
        ans = {locals.K_UP : InputEvent.InputKey.Up,
                locals.K_DOWN : InputEvent.InputKey.Down,
                locals.K_LEFT : InputEvent.InputKey.LEFT,
                locals.K_RIGHT : InputEvent.InputKey.RIGHT,
                locals.K_x : InputEvent.InputKey.FIRE,
                locals.K_z : InputEvent.InputKey.JUMP}
        self.assertDictEqual(ans,self.test_mapper.MapKeys)
    