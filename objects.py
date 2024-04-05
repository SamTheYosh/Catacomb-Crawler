import random

from util import *
from circles import *
from states import *
from animation import *
from particles import *

class ObjectHandler(PositionGridUser):
    # Handles objects and their collisions.
    def __init__(self, app):
        super().__init__(app)
        self.objects = []

    def update(self):
        # Calls the update method of all objects in self.objects
        # that aren't SimpleObjects. There will be lots of SimpleObjects
        # in the level (used for decoration) so not calling their update
        # methods improves performance.
        for obj in [i for i in self.objects if not isinstance(i, SimpleObject)]:
            obj.update()
        # After this, we process object collisions.
        self.handle_collisions()

    def draw(self):
        # Draws each object in self.objects.
        # Objects with a lower y position (higher on screen)
        # will be drawn first, so objects appear in the correct
        # order.
        for obj in sorted(self.objects, key = lambda x: x.pos.y):
            obj.draw()

    def add_object(self, obj):
        # Adds an object to this ObjectHandler.
        self.objects.append(obj)

    def remove_object(self, obj):
        # Removes an object from this ObjectHandler.
        if obj in self.objects:
            self.objects.remove(obj)

    def handle_collisions(self):
        # In this method, we check which objects are overlapping with each other and
        # process collision responses between those that do.
        # First we update self.positionGrid, which lets us easily see which objects
        # are close to each other so should have a collision check performed between
        # them. We don't add SimpleObjects or Particles to this grid as this would
        # we bad for performance - we would be doing unnecessary checks as these classes
        # are never collidable.
        self.update_position_grid([i for i in self.objects if not isinstance(i, (SimpleObject, Particle))])
        # Then we iterate over each pair of nearby objects.
        for a, b in self.iterate_pairs():
            # If either of the objects isn't collidable, continue
            # to the next pair because a collision response
            # shouldn't occur.
            if not a.collidable or not b.collidable:
                continue
            # Now we actually check if the objects are overlapping.
            # If they aren't, continue to the next pair.
            if not a.get_colliding(b): continue
            # By this point we know that the objects are colliding
            # with each other, so we should call their collide()
            # methods.
            a.collide(b)
            b.collide(a)
            # This check is made to ensure that we don't try to perform
            # collision checks when we have just progressed to the next
            # level. If we do, it can lead to unwanted behaviour.
            if self.app.levelContainer.objectHandler != self: return
            # Finally we attempt to move the two objects apart.
            self.collision_response(a, b)

    def collision_response(self, a, b):
        # This method moves two overlapping objects apart.
        # We decide whether to move an object based on whether
        # it and the object it is colliding with are VerletObjects
        # or not. These variables are used for this.
        aVerletObject = isinstance(a, VerletObject)
        bVerletObject = isinstance(b, VerletObject)

        # This is the vector that describes how the
        # two objects are overlapping. It will be used
        # to move them apart by the correct amount.
        overlapVector = a.get_overlap_vector(b)

        # If both objects are VerletObjects, we should
        # move them both because they are both affected
        # by physics.
        # If both objects are not VerletObjects, we should
        # still move them both because this will prevent
        # objects from being stuck inside each other if they
        # are randomly placed inside each other.
        if (
            (aVerletObject and bVerletObject) or
            (not aVerletObject and not bVerletObject)
        ): ratio = (a.radius ** 2) / (a.radius ** 2 + b.radius ** 2)
        # If only one of the objects is a VerletObject, we shouldn't
        # allow the non-VerletObject to be moved. This would mean that
        # the player and enemies would be able to push around rocks,
        # torches, campfires etc. that are placed around the level.
        # We still need to move the VerletObject though, otherwise it
        # would be able to pass straight through objects.
        elif aVerletObject: ratio = 0
        elif bVerletObject: ratio = 1
        
        # Finally we make the adjustments to the objects' positions.
        a.pos += overlapVector * (ratio - 1) * 0.1
        b.pos += overlapVector * ratio * 0.1

class Object(Circle):
    # An object in the world - has animations and state machines.
    def __init__(
            self, 
            app, 
            pos, 
            radius, 
            states, 
            animationManager, 
            collidable = True,
            flipped = False,
            sound = None
    ):
        super().__init__(app, pos, radius)
        
        self.animationManager = animationManager
        self.animationManager.set_user(self)

        self.collidable = collidable
        self.rotation = 0

        self.flipped = flipped

        # Objects can play a looping sound - this can be used,
        # for example, to give a campfire a fire sound effect.
        self.sound = sound

        # The object will be tinted this colour when drawn
        # to the screen.
        self.tint = WHITE

        # This is a dictionary of state machines that this object
        # will use. We create StateMachine instances for each value
        # in the states dictionary we passed in as an argument.
        self.stateMachines = {}
        for key, value in states.items():
            self.stateMachines[key] = StateMachine(self.app, self, value)

    def update(self):
        # First we update all of the state machines in
        # self.stateMachines, and self.animationManager.
        for stateMachine in self.stateMachines:
            self.stateMachines[stateMachine].update()
        self.animationManager.update()

        # Then, if this object has a sound defined:
        if self.sound != None:
            # If we are close to the camera position (meaning the sound will
            # be audible), play the sound if it isn't playing already.
            if self.app.camera.pos.distance_to(self.pos) < (WIDTH + HEIGHT) / 2:
                if not self.app.soundPlayer.check_sound_exists(self):
                    self.app.soundPlayer.play_preset_positional_sound(self.sound, self.pos, loop = True, group = self)
            # If we aren't close to the camera position, so playing a sound would
            # be useless and bad for performance because you wouldn't be able to
            # hear it, attempt to stop the sound if it is still playing.
            else:
                self.app.soundPlayer.stop_group(self)

    def draw(self):
        # Here we get the current animation frame, flip it if self.flipped,
        # tint it, and draw it to the screen.
        sprite = self.animationManager.get_frame()
        if self.flipped: sprite = pygame.transform.flip(sprite, self.flipped, False)
        sprite = self.tint_surface(sprite, self.tint)
        self.app.camera.blit(
            sprite,
            self.pos - (
                self.animationManager.spritesheet.spriteWidth * 0.5,
                max(
                    self.animationManager.spritesheet.spriteHeight * 0.8,
                    self.animationManager.spritesheet.spriteHeight - 2
                )
            )
        )

    def get_camera_target_pos(self):
        # Provides a position for the camera to target
        # if the camera's target object is this object.
        return self.pos

    def collide(self, obj):
        # This method is called when this object collides
        # with another object.
        # We call the collide method of every state machine
        # in self.stateMachines.
        for stateMachine in self.stateMachines:
            self.stateMachines[stateMachine].collide(obj)
    
    def tint_surface(self, surface, colour):
        # This method tints this object's sprite a certain
        # colour. The main complexity of this method is excluding
        # the parts of the sprite that are meant to be transparent
        # because they are the same colour as the colourkey.
        # If these parts of the sprite have their colour changed,
        # they will no longer match the colourkey so will no longer
        # be transparent.
        if pygame.Color(colour) == pygame.Color(WHITE): return surface
        tintedSurface = surface.copy()
        tintMask = surface.copy()
        pygame.transform.threshold(
            tintMask,
            tintMask,
            search_color = self.animationManager.spritesheet.colourkey,
            set_color = colour
        )
        tintedSurface.blit(tintMask, (0, 0), special_flags = pygame.BLEND_RGBA_MULT)
        return tintedSurface

class SimpleObject(Circle):
    # A simpler version of the Object class with reduced functionality,
    # meaning many can be in the level at once without much of a performance
    # decrease. Used for decorating the level.
    def __init__(self, app, pos, radius, spritesheet, spriteIndex):
        super().__init__(app, pos, radius)

        self.spritesheet = self.app.spritesheetManager.get(spritesheet)
        self.spriteIndex = spriteIndex

        self.flipped = random.randint(0, 1)

    def update(self): ...

    def draw(self):
        # Similar to Object.draw - we get this object's sprite, flip
        # it if self.flipped, then draw it to the screen.
        sprite = self.spritesheet.get(self.spriteIndex)
        if self.flipped: sprite = pygame.transform.flip(sprite, self.flipped, False)
        self.app.camera.blit(
            sprite,
            self.pos - (
                self.spritesheet.spriteWidth * 0.5,
                max(
                    self.spritesheet.spriteHeight * 0.8,
                    self.spritesheet.spriteHeight - 2
                )
            )
        )

    def get_camera_target_pos(self):
        # Provides a position for the camera to target
        # if the camera's target object is this object.
        return self.pos

    def collide(self, obj): ...

class VerletObject(Object):
    # An object that uses the Verlet integration physics system.
    def __init__(
            self,
            app,
            pos,
            radius,
            states,
            animationManager,
            acceleration = (0, 0),
            collidable = True,
            flipped = False
    ):
        super().__init__(app, pos, radius, states, animationManager, collidable, flipped)

        self.velocity = pygame.math.Vector2()
        self.acceleration = pygame.math.Vector2(acceleration)
        # self.previousPos is this object's position on the previous frame.
        # The vector between the previous position and the current position
        # is the object's velocity. This is the main principle behind Verlet
        # integration.
        self.previousPos = pygame.math.Vector2(pos)

        # This is a list of any boundaries that this object
        # was nearby on the previous frame. It is used if the
        # object moves outside of all boundaries - it gets snapped
        # back inside the closest one it was previously nearby.
        self.previousNearbyBoundaries = []

    def update(self):
        # First, we calcualate the object's velocity.
        # This is the vector between the position on the last frame
        # and the current position. We also add on the object's
        # acceleration.
        self.velocity = self.pos - self.previousPos
        self.velocity += self.acceleration * self.app.levelGenerator.traction
        # Here we apply some friction.
        self.velocity *= self.app.levelGenerator.friction
        # We have applied the object's acceleration, so we need to reset
        # it to zero so the same acceleration isn't applied on the next
        # frame.
        self.acceleration.update()
        # Before we update the object's position, we need to store it
        # in self.previousPos.
        self.previousPos.update(self.pos)
        # Then we apply the object's velocity.
        self.pos += self.velocity
        super().update()
        # Finally we snap the object back inside the boundaries of the level.
        self.app.levelContainer.boundaryHandler.snap_inside_boundaries(self)

    def accelerate(self, by):
        # Acclerates the object by the given vector.
        self.acceleration += by

    def get_within_boundaries(self, nearbyBoundaries):
        # This method returns whether this object is inside
        # the boundaries of the level or not.
        # It is more complicated than you would think
        # because of a certain edge case when an object
        # isn't fully inside any boundaries but overall
        # is still inside them (explained better with a
        # diagram in the document).

        # The main idea of this method is to check a series
        # of points along the circle's circumference to see
        # if they are inside the boundaries of the level.
        # We know that a part of the circle lies outside the
        # boundaries if any of these points are outside of
        # the boundaries.

        # The "vector" variable is a vector in the direction
        # of the player's velocity. We only need to check points
        # on the half of the circumference in the direction the
        # object is moving - the boundaries cannot move into
        # the object from behind.
        if self.velocity.magnitude_squared() == 0:
            vector = pygame.math.Vector2(1, 0)
        else:
            vector = self.velocity.normalize()
        # We are checking points between -90 and 90 degrees, with
        # 0 degrees being the direction of the object's velocity.
        # We will start at -90, so we need to rotate the vector
        # by -90.
        vector = vector.rotate(-90)

        # The larger the circle's radius, the more points we
        # should check because it will be more obvious for
        # larger circles that we are only checking certain
        # points along the circumference.
        pointsToCheck = max(3, int(self.radius / 2))
        # This variable is the angle between successive points.
        angle = 180 / (pointsToCheck - 1)
        # We apply some slight randomness to the velocity vector
        # to get rid of cases where a thin sliver of wall could
        # sneak in between two points.
        vector = vector.rotate(random.uniform(-0.5, 0.5) * angle)
        # Then we check if each point is within the boundaries.
        # If any of the points are outside the boundaries, we
        # return False. We only return True if all of the points
        # are inside the boundaries.
        for i in range(pointsToCheck):
            point = self.pos + vector.rotate(i * angle)
            pointInsideBoundaries = False
            for boundary in nearbyBoundaries:
                if (boundary.pos - point).magnitude() < boundary.radius - self.radius:
                    pointInsideBoundaries = True
                    break
            if not pointInsideBoundaries: return False
        return True

class Entity(VerletObject):
    # Used for enemies and the player, has common methods and attributes
    # for these use cases.
    def __init__(
            self,
            app,
            maxHp,
            speed,
            drops,
            attackDamage,
            pos,
            radius,
            states,
            animationManager,
            bloodColour = (138, 0, 39),
            attackStatusEffect = None,
            attackStatusEffectChance = 1,
            invulnerable = False
    ):
        super().__init__(app, pos, radius, states, animationManager)

        self.hp = maxHp
        self.maxHp = maxHp
        self.speed = speed
        # This is a list of item ids with associated weights that
        # could be dropped when this entity dies.
        self.drops = drops
        self.attackDamage = attackDamage
        self.invulnerable = invulnerable
        self.bloodColour = bloodColour
        self.attackStatusEffect = attackStatusEffect
        self.attackStatusEffectChance = attackStatusEffectChance

    def change_hp(self, by, attacker = None):
        # First we check if this entity is invulnerable.
        # If it is, we shouldn't attempt to change its HP.
        # The return value of this method is a Boolean
        # representing whether this entity's HP has changed
        # or not.
        if self.invulnerable: return False
        # Then we change the HP.
        self.hp = min(self.maxHp, max(0, self.hp + by))
        # If the entity's HP decreased, we should display
        # all of the damage effects in self.damage().
        if by < 0: return self.damage(-by, attacker)
        # Finally we return True because the entity's HP
        # has changed.
        return True

    def damage(self, by, attacker):
        # The "vector" variable is a vector that defines the
        # knockback acceleration to be applied to this entity.
        # We calculate it using the vector between the entity
        # and the attacker (the entity that damaged this entity).
        # If there was no attacker, we just use a vector of length
        # 0.
        if attacker is None: vector = pygame.math.Vector2(0, 0)
        else: vector = self.pos - attacker.pos
        if vector.magnitude_squared() != 0:
            vector = vector.normalize()
        # The "factor" variable is used to determine how much
        # screen shake should be applied, how much blood to
        # create, the magnitude of the knockback and the volume
        # of the damage sound effect.
        factor = 10 - 10 ** (1 - by / 25)
        # Scaling the knockback vector by factor and
        # applying the knockback.
        vector *= factor
        self.accelerate(vector)
        # Applying the camera shake.
        self.app.camera.shake(factor * 10)
        # Playing a damage sound effect.
        self.app.soundPlayer.play_preset_positional_sound(
            "hit",
            pos = self.pos,
            volume = factor * 0.15 + random.uniform(-0.1, 0.1)
        )
        # Creating a blood effect if a blood colour is defined.
        if self.bloodColour != None:
            bloodCount = factor * 2
            if self.hp == 0: bloodCount *= 2
            self.app.particleEffectsManager.create_effect(
                0,
                self.pos,
                int(bloodCount),
                self.velocity + vector,
                colour = self.bloodColour
            )
        return True

class Chest(Object): 
    # Contains items, and spills out these
    # items into the level when opened.
    def __init__(self, app, pos, contains):
        # I really don't like this import here, but we
        # have to do it otherwise there will be a circular
        # import.
        import states_definition
        super().__init__(
            app,
            pos,
            10,
            {
                "main" : {
                    "closed" : states_definition.State_Chest_Closed,
                    "open" : states_definition.State_Chest_Open
                }
            },
            AnimationManager(
                app,
                "misc.png",
                [
                    ("open", Animation(app, 0, 1)),
                    ("closed", Animation(app, 0, 0))
                ]
            )
        )
        self.contains = contains

class Exit(Object):
    # When the player interacts with this object, we
    # progress to the next level.
    def __init__(self, app, pos):
        super().__init__(
            app,
            pos,
            8,
            {},
            AnimationManager(
                app,
                "misc.png",
                [("main", Animation(app, 0, 2))]
            )
        )

    def collide(self, obj):
        # If the player is colliding with this object and the enter key
        # is pressed, progress to the next level.
        if obj == self.app.player and self.app.eventHandler.get_key_pressed(pygame.K_RETURN):
            self.app.next_level()

class RunExit(Object):
    # When the player interacts with this object, we
    # end the run and transition to the results screen.
    def __init__(self, app, pos):
        super().__init__(
            app,
            pos,
            8,
            {},
            AnimationManager(
                app,
                "misc.png",
                [("main", Animation(app, 0.3, 3, 4))]
            )
        )

    def collide(self, obj):
        # If the player is colliding with this object and the enter key
        # is pressed, transition to the results screen.
        if obj == self.app.player and self.app.eventHandler.get_key_pressed(pygame.K_RETURN):
            self.app.set_game_state(2)