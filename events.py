import pygame

from util import *

class EventHandler:
    # Provides a simple interface for pygame's event handling methods.
    def __init__(self, app):
        self.app = app
        self.mousePos = pygame.math.Vector2()
        self.handle_events()
    
    def handle_events(self):
        self.keysJustPressed = []
        self.mouseJustPressed = []

        # Iterates over all of the events that happened since the last call
        # to pygame.event.get() and picks out and processes any relevant ones.
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.app.stop()
                case pygame.KEYDOWN:
                    self.keysJustPressed.append(event.key)
                case pygame.MOUSEBUTTONDOWN:
                    self.mouseJustPressed.append(event.button - 1)
        
        # We can use pygame's provided methods to get which keys and
        # mouse buttons are currently pressed, the mouse's current position
        # in relation to the top left hand corner of the window.
        self.keysPressed = pygame.key.get_pressed()
        self.mousePressed = pygame.mouse.get_pressed()
        
        self.mousePos.update(pygame.mouse.get_pos())

    def get_key_just_pressed(self, key):
        # Return if a key has just been pressed.
        return key in self.keysJustPressed

    def get_key_pressed(self, key):
        # Return if a key is currently pressed.
        return self.keysPressed[key]

    def get_mouse_just_pressed(self, button):
        # Return if a mouse button has just been pressed.
        return button in self.mouseJustPressed

    def get_mouse_pressed(self, button):
        # Return if a mouse button is currently pressed.
        return self.mousePressed[button]

    def get_mouse_pos(self):
        # Return the mouse position.
        return self.mousePos.copy()

    def get_movement_vector(self):
        # Return a vector calculated based on the states of the directional keys (WASD
        # and up, down, left, right. This can be used to move an object with the
        # directional keys.
        return pygame.math.Vector2(
            (self.get_key_pressed(pygame.K_d) or self.get_key_pressed(pygame.K_RIGHT)) -
            (self.get_key_pressed(pygame.K_a) or self.get_key_pressed(pygame.K_LEFT)),
            (self.get_key_pressed(pygame.K_s) or self.get_key_pressed(pygame.K_DOWN)) -
            (self.get_key_pressed(pygame.K_w) or self.get_key_pressed(pygame.K_UP))
        )

    def get_movement_vector_normalised(self):
        # Calls self.get_movement_vector() and normalises the result.
        vector = self.get_movement_vector()
        try:
            return vector.normalize()
        except:
            return vector