import random

from util import *
from circles import *

class ParticleEffectsManager:
    # Provides a simple interface for creating particle effects.
    def __init__(self, app):
        self.app = app

        self.presets = read_json("jsondata//particles.json")
    
    def create_effect(self, index, pos, count, vel = (0, 0), colour = None):
        # First we get the particle effect data at the given index.
        preset = self.presets[index]
        # By default, we use the colour defined in the preset.
        # We can override this default colour by providing one
        # as an argument.
        if colour is None: colour = preset["colour"]
        # Create the given number of particle effects
        for _ in range(count):
            # We can provide a list of colours or just a single colour.
            # If a list is provided, we need to pick a random colour
            # from this list.
            if hasattr(colour[0], "__iter__"):
                finalColour = random.choice(colour)
            else:
                finalColour = colour
            # Finally we create the particle using data from the preset
            # and add it to the level.
            self.app.levelContainer.objectHandler.add_object(Particle(
                self.app,
                pos,
                finalColour,
                8,
                pygame.math.Vector2(
                    random.uniform(*preset["velocity"])
                ).rotate(random.uniform(0, 360)) + vel,
                random.uniform(*preset["zVelocity"]),
                random.uniform(*preset["radius"])
            ))

class Particle(Circle):
    # A single particle, moves until it hits the ground.
    def __init__(self, app, pos, colour, z, velocity = (0, 0), zVelocity = 0, radius = 1):
        super().__init__(app, pos, radius)

        self.colour = colour
        self.velocity = pygame.math.Vector2(velocity)
        # Particles have a z position. They can, for example, fly into the air
        # and fall towards the ground (used for blood).
        self.z = z
        self.zVelocity = zVelocity

    def update(self):
        # If the particle's z position is 0,
        # we can think of it as being on the ground
        # so we don't want to update its position
        # any more.
        if self.z <= 0:
            self.z = 0
            self.zVelocity = 0
            self.velocity.update()
            return
        # If the particle isn't on the ground, we
        # update its position.
        self.zVelocity -= 0.1
        self.z += self.zVelocity
        self.pos += self.velocity

    def draw(self):
        # Drawing the particle to the screen.
        pos = self.app.camera.adjust_pos(self.pos) - (0, self.z)
        # pygame's circle drawing code can only draw circles with
        # a minimum radius of 2. If we want to draw a circle with
        # a radius of 1, we just have to draw a single pixel manually.
        if self.radius <= 1:
            self.app.screen.set_at(
                [int(i) for i in pos],
                self.colour
            )
        else:
            pygame.draw.circle(
                self.app.screen,
                self.colour,
                pos,
                self.radius
            )

    def get_camera_target_pos(self):
        return self.pos

    def collide(self, obj): ...