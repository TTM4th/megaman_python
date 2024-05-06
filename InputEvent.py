from abc import ABCMeta, abstractmethod
from pygame import locals
from pygame.event import Event
from enum import Enum
from __future__ import annotations

class InputEventContoller:

    def __init__(self, actions: IInputActions) -> None:
        self.keyinput = KeyInput()
        self.UPActions = {InputState.Start:actions.UPKeyStart, InputState.Continue:actions.UPKeyContinue, InputState.Cancel:actions.UPKeyCancel}
        self.DOWNActions = {InputState.Start:actions.DOWNKeyStart, InputState.Continue:actions.DOWNKeyContinue, InputState.Cancel:actions.DOWNKeyCancel}
        self.LEFTActions = {InputState.Start:actions.LEFTKeyStart, InputState.Continue:actions.LEFTKeyContinue, InputState.Cancel:actions.LEFTKeyCancel}
        self.RIGHTActions = {InputState.Start:actions.RIGHTKeyStart, InputState.Continue:actions.RIGHTKeyContinue, InputState.Cancel:actions.RIGHTKeyCancel}
        self.FIREActions = {InputState.Start:actions.FIREKeyStart, InputState.Continue:actions.FIREKeyContinue, InputState.Cancel:actions.FIREKeyCancel}
        self.JUMPActions = {InputState.Start:actions.JUMPKeyStart, InputState.Continue:actions.JUMPKeyContinue, InputState.Cancel:actions.JUMPKeyCancel}

    def DoActions(self, events:list[Event]) -> None:
        self.keyinput.catchInput(events)
        for k,v in self.keyinput.__inputtedStates.items():
            actions = self.__ActionFactory(k)
            for action in actions[v]:
                action()
    
    def __ActionFactory(self, keycode:int):
        if keycode == locals.K_UP:
            return self.UPActions
        elif keycode == locals.K_DOWN:
            return self.DOWNActions
        elif keycode == locals.K_LEFT:
            return self.LEFTActions
        elif keycode == locals.K_RIGHT:
            return self.RIGHTActions
        elif keycode == locals.K_FIRE:
            return self.FIREActions
        elif keycode == locals.K_JUMP:
            return self.JUMPActions

class InputKey(Enum):
    Up = 0
    Down = 1
    LEFT = 2
    RIGHT = 3
    FIRE = 4
    JUMP = 5

class InputState(Enum):
    NoneInput = 0
    Start = 1
    Continue = 2
    Cancel = 3

class KeyInput:
    
    def __init__(self) -> None:
        self.__inputtedStates = {locals.K_UP:InputState.NoneInput,
                                locals.K_DOWN:InputState.NoneInput,
                                locals.K_LEFT:InputState.NoneInput,
                                locals.K_RIGHT:InputState.NoneInput,
                                locals.K_z:InputState.NoneInput,
                                locals.K_x:InputState.NoneInput}

    def catchInput(self, events:list[Event]) -> None:
        for key in self.__inputtedStates.keys():
            if self.__inputtedKeys[key] == InputState.Cancel:
                self.__inputtedKeys[key] = InputState.NoneInput
                
        for event in filter(lambda x: (x.type == locals.KEYDOWN or x.type == locals.KEYUP) and 
                                    (x.key in self.__inputtedStates.keys()), 
                                    events):
            if (event.key in self.__inputtedKeys):
                if event.type == locals.KEYUP:
                    self.__inputtedStates[event.key] = InputState.Cancel
                elif event.type == locals.KEYDOWN:
                    self.__inputtedStates[event.key] = InputState.Continue
            else:
                if event.type == locals.KEYDOWN:
                    self.__inputtedStates[event.Key] = InputState.Start
            
class IInputActions(metaclass = ABCMeta): 
    @abstractmethod
    def UPKeyStart(self):
        pass
    
    @abstractmethod
    def UPKeyContinue(self):
        pass

    @abstractmethod
    def UPKeyCancel(self):
        pass
    
    @abstractmethod
    def DOWNKeyStart(self):
        pass

    @abstractmethod
    def DOWNKeyContinue(self):
        pass

    @abstractmethod
    def DOWNKeyCancel(self):
        pass

    @abstractmethod
    def LEFTKeyStart(self):
        pass
    
    @abstractmethod
    def LEFTKeyContinue(self):
        pass

    @abstractmethod
    def LEFTKeyCancel(self):
        pass

    @abstractmethod
    def RIGHTKeyStart(self):
        pass
    
    @abstractmethod
    def RIGHTKeyContinue(self):
        pass

    @abstractmethod
    def RIGHTKeyCancel(self):
        pass

    @abstractmethod
    def JUMPKeyStart(self):
        pass
    
    @abstractmethod
    def JUMPKeyContinue(self):
        pass

    @abstractmethod
    def JUMPKeyCancel(self):
        pass
        
    @abstractmethod
    def FIREKeyStart(self):
        pass
    
    @abstractmethod
    def FIREKeyContinue(self):
        pass

    @abstractmethod
    def FIREKeyCancel(self):
        pass