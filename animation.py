import math, random

from util import *

class AnimationManager:
    # Stores animations that can be switched between.
    def __init__(self, app, spritesheet, animations):
        self.app = app
        # This is a reference to the Object using this AnimationManager.
        # The main use of this is getting an Object's rotation attribute
        # to update RotationalAnimations.
        self.user = None
        
        self.spritesheet = self.app.spritesheetManager.get(spritesheet)
        self.animations = {}
        # The animations argument is a list of tuples.
        # The first element of the tuple is the name of
        # the animation, and the second is an Animation
        # object.
        for animationData in animations:
            self.add_animation(*animationData)
        # Defaults to the last animation in self.animations.
        self.currentAnimation = list(self.animations.keys())[-1]

        # self.currentAnimation is a key, this is just a reference
        # to the object at that key in self.animations.
        self.currentAnimationObject = self.animations[self.currentAnimation]

    def set(self, name, time=0):
        # Set which animation to play.
        previousAnimation = self.currentAnimation
        self.currentAnimation = name
        
        # If we are already playing the animation,
        # return as we don't need to do any of the
        # code below.
        if previousAnimation == self.currentAnimation: return
        currentAnimation = self.animations[self.currentAnimation]
        # The time argument is the value that the animation's
        # timer should take when it is entered.
        if time is None:
            # Pick a random value for the animation's timer.
            # This is to provide a random offset for enemy
            # animations, so they don't all animate in sync.
            currentAnimation.timer = random.uniform(0, len(currentAnimation.sprites))
        else:
            currentAnimation.timer = time
        # Animation's previousFrame attribute is explained
        # within the Animation class.
        currentAnimation.previousFrame = -1

    def update(self):
        # Calls the update method of the current animation.
        self.currentAnimationObject = self.animations[self.currentAnimation]
        self.currentAnimationObject.update(self.user)

    def get_frame(self):
        # Returns a surface - the current animation frame.
        return self.spritesheet.get(self.get_frame_index())
    
    def get_frame_index(self):
        # Returns the current animation's index.
        return self.animations[self.currentAnimation].get_frame()
    
    def add_animation(self, name, animation):
        # Adds an animation to self.animations.
        self.animations[name] = animation
    
    def set_user(self, user):
        # Updates self.user (explained in __init__()).
        self.user = user

class Animation:
    # Stores sprites and sounds to be played back.
    def __init__(self, app, speed, *sprites, sounds = {}):
        self.app = app
        self.sprites = sprites
        self.timer = 0
        # Each frame, self.timer is increased by self.speed.
        self.speed = speed
        # A dictionary of sounds to be played on certain frames.
        self.sounds = sounds
        # These two attributes are used to ensure that sounds are not
        # played each time the update method is called and we are on
        # its associated animation frame, only the first time.
        self.previousFrame = -1
        self.justChangedFrame = False

    def update(self, user):
        # Increases the timer by self.speed
        # and wraps the timer back around to
        # the start of the animation if we
        # reach the end.
        self.timer += self.speed
        self.timer %= len(self.sprites)

        self.justChangedFrame = False

        # The following code plays a sound if we have
        # just switched to a frame with an associated
        # sound, defined in self.sounds.
        currentFrame = self.get_frame_index()
        if self.previousFrame != currentFrame:
            self.justChangedFrame = True
            if currentFrame in self.sounds:
                args = self.sounds[currentFrame]
                while True:
                    if isinstance(args, int):
                        # I can use an integer to point to another
                        # frame's sound data, so I don't have to
                        # repeat myself if I want to play the same
                        # sound on multiple frames.
                        args = self.sounds[args]
                    elif isinstance(args, str):
                        # A string means I want to make use of a preset
                        # from sounds.json.
                        self.app.soundPlayer.play_preset_positional_sound(
                            args,
                            pos = user.pos
                        )
                        break
                    else:
                        # Anything else means I have provided a dictionary
                        # of arguments, this is passed to SoundPlayer.process_sound_arguments
                        # to do things like generate random volume and pitch values. The values
                        # produced by this method are then used to play a sound.
                        self.app.soundPlayer.play_positional_sound(
                            **self.app.soundPlayer.process_sound_arguments(args),
                            pos = user.pos
                        )
                        break
        self.previousFrame = currentFrame
    
    def get_frame_index(self):
        # Calculates a frame index using the current timer value.
        return math.floor(self.timer)

    def get_frame(self):
        # Gets the current animation frame using the current frame index.
        return self.sprites[self.get_frame_index()]

class RotationalAnimation(Animation):
    # An animation with different frames based the rotation of its user.
    def __init__(self, app, speed, *spritesForEachDirection, rotationOffset = 0, sounds = {}):
        # We store all of the sprite indices in a 2D array.
        # We can then pick the correct list of sprites based on the
        # rotation of this animation's user. This list is stored in
        # the sprites attribute, so all of the code inherited from
        # the Animation class will work properly.
        self.spritesForEachDirection = spritesForEachDirection
        super().__init__(app, speed, *self.spritesForEachDirection[0], sounds = sounds)
        self.rotationOffset = rotationOffset

    def update(self, user):
        # Here we calculate which set of frames to use based on the
        # user's rotation value.
        rotation = user.rotation
        rotation += 360 / (len(self.spritesForEachDirection) * 2)
        rotationIndex = int((((rotation + self.rotationOffset) / 360) % 1) * len(self.spritesForEachDirection))
        # Then we update self.sprites with the correct set of frames,
        # to be processed by the rest of the code from the Animation class
        self.sprites = self.spritesForEachDirection[rotationIndex]
        super().update(user)

# This is a helpful .json file containing frame indices for commonly used animation
# types, to save me from having to write them out every time I want to use them.
# It is used by other files importing this file.
framePresets = read_json("jsondata//animations.json")