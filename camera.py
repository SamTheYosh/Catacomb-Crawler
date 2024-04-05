import pygame, random

from util import *

class Camera:
    # Everything is drawn relative to the camera, so the camera's position
    # is at (WIDTH/2, HEIGHT/2) on the screen.
    def __init__(self, app, targetPos = (0, 0), target = None):
        self.app = app
        # This is the position that the camera will smoothly track
        # towards.
        self.targetPos = pygame.math.Vector2(targetPos)
        # This is the camera's actual position. Other positions will be
        # offset using this position.
        self.pos = pygame.math.Vector2(self.targetPos)
        # An object for the camera to track can be provided here. If an
        # object is provided, self.targetPos will be updated with the object's
        # position each frame.
        self.target = target
        # Each frame, the camera's position will be offset by a random vector
        # with a length defined using this variable, to give a shaking effect.
        # If the shake factor is 0, there will be no camera shake.
        self.shakeFactor = 0

    def update(self):
        # If we have assigned an object for the camera to target,
        # we update the target position with this object's position.
        if not self.target is None:
            self.targetPos.update(self.target.get_camera_target_pos())
        # Camera shake is applied here.
        targetPos = self.targetPos + pygame.math.Vector2(self.shakeFactor, 0).rotate(random.uniform(0, 360))
        # Now we smoothly move the camera towards the target position.
        # Lerp is short for linear interpolation. In this case, we
        # move the camera 10% of the distance towards the target position
        # each frame, which results in a smooth movement.
        self.pos.update(self.pos.lerp(targetPos, 0.1))
        # The shake factor decays exponentially over time.
        self.shakeFactor *= 0.9

    def set_target(self, obj):
        # Setting the target object
        self.target = obj

    def set_target_pos(self, pos):
        # Setting a target position.
        self.targetPos.update(pos)
        # We don't want to target an object any more
        # if we have just set a specific position to
        # target.
        self.target = None

    def adjust_pos(self, pos):
        # This method is used to calculate where on the screen
        # a given position should appear if everything is offset
        # by the camera's position.
        return pos - self.pos + (WIDTH/2, HEIGHT/2)

    def blit(self, surface, pos):
        # This method blits a surface to the screen, offset by
        # the camera's position.
        self.app.screen.blit(surface, self.adjust_pos(pos))
    
    def shake(self, factor):
        # This method is used to apply camera shake.
        self.shakeFactor += factor