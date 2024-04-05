from util import *

class StateMachine:
    # Stores multiple states that can be transitioned between.
    def __init__(self, app, obj, states):
        self.app = app
        self.obj = obj
        # If self.active is False, this state machine shouldn't do
        # anything until self.active is set back to True.
        self.active = True

        # Creates States using the states dictionary.
        self.states = states
        for i in self.states:
            self.states[i] = self.states[i](self.app, self, self.obj)
        
        # We default to the first state in the dictionary.
        self.currentState = list(self.states.keys())[0]

    def update(self):
        if not self.active: return
        self.states[self.currentState].update()

    def collide(self, obj):
        if not self.active: return
        self.states[self.currentState].collide(obj)

    def set_state(self, name):
        # Transitions to the given state.
        if not self.active: return
        self.currentState = name
        self.states[self.currentState].enter()

    def set_active(self, active):
        self.active = active

class State:
    # Stored in StateMachines - is inherited from and its
    # methods are overridden to define behaviour.
    def __init__(self, app, stateMachine, obj):
        self.app = app
        self.stateMachine = stateMachine
        self.obj = obj
        self.setup()

    def setup(self): ...

    def enter(self): ...

    def update(self): ...

    def collide(self, obj): ...