import os, random, math
import numpy as np

from util import *
from sprites import *

class Font(Spritesheet):
    # A special spritesheet that has methods for easily accessing characters and drawing
    # strings to the screen.
    def __init__(self, app, filename, fontLibrary):
        self.load_image("fonts//" + filename)
        self.fontLibrary = fontLibrary
        super().__init__(
            app,
            filename,
            *self.get_dimensions(self.fontLibrary.charsWidth, self.fontLibrary.charsHeight)
        )
    
    def get_dimensions(self, charsWidth, charsHeight):
        # Calculates the sprite dimensions based on the dimensions
        # of the image. We already know how many sprites should be in
        # the spritesheet from charmap.txt, loaded in FontLibrary.
        spriteWidth = int(self.image.get_width() / charsWidth)
        spriteHeight = int(self.image.get_height() / charsHeight)
        return spriteWidth, spriteHeight

    def draw_text(
            self,
            surface,
            string,
            pos,
            colour = WHITE,
            align = (0, 0)
    ):
        # First we split the given text into a list of lines.
        lines = string.split("\n")
        # This is the total height in pixels of the text.
        height = len(lines) * (self.spriteHeight + 1)
        
        # Draws each character of each line of text to the screen,
        # offsetted using the align argument.
        pos = pygame.math.Vector2(pos)
        pos.y -= height * align[1]
        offset = pygame.math.Vector2()
        for line in lines:
            width = len(line) * self.spriteWidth
            offset.x -= width * align[0]
            for char in line:
                self.draw_char(surface, char, pos + offset, colour)
                offset.x += self.spriteWidth
            offset.x = 0
            offset.y += self.spriteHeight + 1

    def draw_char(
            self,
            surface,
            char,
            pos,
            colour = WHITE
    ):
        # Gets the sprite corresponding to the given character.
        charSprite = self.get(self.fontLibrary.get_char_index(char))

        # Sets the character's colour.
        colourSurface = pygame.Surface((self.spriteWidth, self.spriteHeight))
        colourSurface.fill(colour)
        charSprite.set_colorkey(WHITE)
        colourSurface.blit(charSprite, (0, 0))
        colourSurface.set_colorkey(BLACK)

        # Draws the character to the screen.
        surface.blit(colourSurface, pos)
    
    def draw_text_with_drop_shadow(
            self,
            surface,
            string,
            pos,
            colour = WHITE,
            shadowColour = (1, 1, 1),
            align = (0, 0),
            shadowOffset = (1, 1)
    ):
        # Draws text with a drop shadow.
        self.draw_text(surface, string, pygame.math.Vector2(pos) + shadowOffset, shadowColour, align)
        self.draw_text(surface, string, pos, colour, align)
    
    def draw_text_with_outline(
            self,
            surface,
            string,
            pos,
            colour = WHITE,
            outlineColour = (1, 1, 1),
            align = (0, 0)
    ):
        # Draws text with a 1 pixel outline.
        for y in range(-1, 2):
            for x in range(-1, 2):
                if (x, y) != (0, 0):
                    self.draw_text(surface, string, pygame.math.Vector2(pos) + (x, y), outlineColour, align)
        self.draw_text(surface, string, pos, colour, align)

class FontLibrary:
    # Stores Fonts and provides a simple inferface for drawing text to
    # the screen.
    def __init__(self, app):
        self.app = app
        self.fonts = {}
        self.charmap, self.charsWidth, self.charsHeight = self.load_charmap()
        self.load_fonts()

    def load_fonts(self):
        # Loads all of the font images in the fonts folder and creates
        # new Font instances for each.
        filesAndFolders = os.listdir("fonts")
        for i in filesAndFolders:
            if i[-4:] == ".png":
                self.fonts[i[:-4]] = Font(self.app, i, self)

    def draw_text(
            self,
            surface,
            string,
            font,
            pos,
            colour = WHITE,
            align = (0, 0)
    ):
        self.fonts[font].draw_text(surface, string, pos, colour, align)
    
    def draw_text_with_drop_shadow(
            self,
            surface,
            string,
            font,
            pos,
            colour = WHITE,
            shadowColour = (1, 1, 1),
            align = (0, 0),
            shadowOffset = (1, 1)
    ):
        self.fonts[font].draw_text_with_drop_shadow(surface, string, pos, colour, shadowColour, align, shadowOffset)
    
    def draw_text_with_outline(
            self,
            surface,
            string,
            font,
            pos,
            colour = WHITE,
            outlineColour = (1, 1, 1),
            align = (0, 0)
    ):
        self.fonts[font].draw_text_with_outline(surface, string, pos, colour, outlineColour, align)

    def load_charmap(self):
        # Loads the charmap file and gets the dimensions (in characters) and
        # a dictionary used to turn a character into a corresponding sprite
        # index in self.get_char_index().
        # 
        # An example of a charmap file could be:
        # 
        #  !"#$%&'()*+,-./0123456789:;<=>?
        # @ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_
        # £abcdefghijklmnopqrstuvwxyz{|}~©

        charmapTextFile = read_file("fonts//charmap.txt")
        charmap2DList = [list(line) for line in charmapTextFile.split("\n")]
        charsWidth = len(charmap2DList[0])
        charsHeight = len(charmap2DList)
        charmap1D = [a for b in charmap2DList for a in b]

        charmap = {}
        for index, char in enumerate(charmap1D):
            charmap[char] = index
        
        return charmap, charsWidth, charsHeight

    def get_char_index(self, char):
        # Returns the sprite index of a given character.
        if char in self.charmap:
            return self.charmap[char]
        return 0

class UIScreen:
    # A screen that has a fade in and fade out transition.
    def __init__(self, app, fadeInTime, fadeOutTime, nextGameState):
        self.app = app

        self.fadeInTime = fadeInTime
        self.fadeOutTime = fadeOutTime
        self.nextGameState = nextGameState

        # A surface that covers the whole screen, will be drawn
        # to the screen with different transparency values based
        # on the progress of the fade transition.
        self.fadeSurface = pygame.Surface((WIDTH, HEIGHT))
        self.fadeSurface.fill(BLACK)

        self.fadeTimer = 0

        # Determines what self.update() should do.
        self.mode = 0

        # When self.preventContinue is False, the user
        # cannot transition to the next screen.
        self.preventContinue = False
    
    def start(self):
        self.mode = 0
        self.fadeTimer = 0
        self.app.soundPlayer.stop_all()
    
    def update(self):
        match self.mode:
            case 0: # Fade in
                if self.fadeInTime == 0: self.fadeTimer = 1
                else: self.fadeTimer += 1 / self.fadeInTime
                if self.fadeTimer >= 1:
                    self.fadeTimer = 1
                    self.mode = 1
            case 1: # Main
                if not self.preventContinue and self.app.eventHandler.get_key_just_pressed(pygame.K_RETURN):
                    self.mode = 2
            case 2: # Fade out
                if self.fadeOutTime == 0: self.fadeTimer = 0
                else: self.fadeTimer -= 1 / self.fadeOutTime
                if self.fadeTimer <= 0:
                    self.fadeTimer = 0
                    self.mode = 3
            case 3: # Transition to next screen
                self.app.soundPlayer.stop_all()
                if self.nextGameState == 1: self.app.setup_game()
                else: self.app.set_game_state(self.nextGameState)

    def draw(self):
        # Essentially dims the screen based on self.fadeTimer's value.
        self.fadeSurface.set_alpha((1 - self.fadeTimer) * 255)
        self.app.screen.blit(self.fadeSurface, (0, 0))

class TitleScreen(UIScreen):
    # The title screen.
    def __init__(self, app):
        super().__init__(app, 240, 60, 1)
        
        # The logo to be drawn to the middle of the title screen.
        self.titleGraphic = pygame.image.load("sprites//title.png").convert()
        self.titleGraphic.set_colorkey(BLACK)
        self.titleGraphicRect = self.titleGraphic.get_rect()
        self.titleGraphicRect.center = WIDTH/2, HEIGHT/2 - 20

        self.bgColour = pygame.Color(20, 5, 15)

        # A list of particles that will move across the screen.
        # Particles are represented by tuples in this format:
        # (position, velocity, acceleration, colour)
        self.particles = []
        for _ in range(300):
            self.particles.append((
                pygame.math.Vector2(
                    random.uniform(0, WIDTH),
                    random.uniform(0, HEIGHT)
                ),
                pygame.math.Vector2(),
                pygame.math.Vector2(0, 0.02),
                pygame.Color(
                    random.randint(20, 200),
                    random.randint(8, 80),
                    random.randint(13, 50)
                )
            ))
        # Particles start with 0 velocity, which looks odd, so we update
        # them all a few times before the title screen starts to prevent
        # this.
        for _ in range(1000): self.update()
    
    def start(self):
        super().start()
        self.app.soundPlayer.play_sound(
            "title.ogg",
            loop = True,
            pitch = 0.75,
            group = self.app.soundPlayer.alwaysAllowGroup
        )

    def update(self):
        # Update each particles' positions.
        for pos, vel, acc, col in self.particles:
            acc.xy = acc.rotate(random.uniform(-5, 5))
            vel += acc
            # The particles' velocities should vary using a sine
            # curve, simulates slowly blowing wind.
            vel += (
                math.sin(self.app.time / 1) * 0.01 +
                math.sin(self.app.time / 2.303) * 0.01,
                -0.03
            )
            pos += vel
            vel *= 0.9
            # Wrapping the particles around the screen.
            pos.x %= WIDTH
            pos.y %= HEIGHT
        
        super().update()

    def draw(self):
        self.app.screen.fill(self.bgColour)
        # Draw each particle to the screen.
        for pos, vel, acc, col in self.particles:
            pygame.draw.rect(self.app.screen, col, (*pos, 1, 1))
        self.app.vignette.draw()
        self.app.screen.blit(self.titleGraphic, self.titleGraphicRect)
        self.app.fontLibrary.draw_text_with_outline(
            self.app.screen,
            "Press ENTER to start!",
            "envious serif",
            (WIDTH/2, HEIGHT/2 + 40),
            align = (0.5, 0.5),
            outlineColour = (1, 1, 1)
        )

        super().draw()

class SimpleUI:
    # The UI that is shown during gameplay.
    def __init__(self, app):
        self.app = app

        # All UI elements are drawn leaving a margin
        # of 30 pixels around the edge of the screen.
        self.margin = 30

    def start(self):
        self.messages = []

    def draw(self):
        # Setting up strings to be used to draw the player's attributes
        # to the screen.
        # If the player's health has a decimal component, display this
        # component rounded to 1 d.p.
        hpString = f"{self.app.player.hp:.1f}"
        # Otherwise display it rounded to 0 d.p.
        if hpString[-1] == "0": hpString = f"{self.app.player.hp:.0f}"
        # Adding this string to the UI.
        string = f"HP: {hpString}/{self.app.player.maxHp}"
        # We then add a string to show inventory capacity and the number
        # of items currently being carried to the UI.
        string += f"\nInventory: {len(self.app.player.inventory.items)}/{self.app.player.inventory.capacity}"
        # If we have an item equipped, we add its name to the UI.
        equippedItem = self.app.player.inventory.get_equipped_item()
        if equippedItem != None:
            string += f"\n\n{equippedItem.name}\n£{equippedItem.cost:.2f}"
            # If the item uses durability, we add its current durability
            # to the UI as well.
            if equippedItem.durability != -1:
                string += f"\nDurability: {equippedItem.durability}"
        # If the player has any status effects applied, we display
        # their names and the time left in seconds.
        string += "\n"
        for effect in self.app.player.statusEffects.values():
            string += f"\n{effect.text}"
            if not effect.activeTimer is None:
                string += f" {math.ceil(effect.activeTimer/60)}"
        # Finally we draw all of this to the screen.
        self.app.fontLibrary.draw_text_with_outline(
            self.app.screen,
            string,
            "envious serif",
            (self.margin, self.margin),
            outlineColour = (1, 1, 1)
        )

        # Drawing all of the messages in self.messages to the screen.
        self.app.fontLibrary.draw_text_with_outline(
            self.app.screen,
            "\n".join([i[0] for i in self.messages]),
            "envious serif",
            (WIDTH - self.margin, self.margin),
            align = (1, 0),
            outlineColour = (1, 1, 1)
        )

        # Drawing the level number and name to the screen.
        self.app.fontLibrary.draw_text_with_outline(
            self.app.screen,
            f"Level {self.app.levelGenerator.levelCounter}\n{self.app.levelGenerator.levelName}",
            "uncial",
            (self.margin, HEIGHT - self.margin),
            align = (0, 1),
            outlineColour = (1, 1, 1)
        )
    
    def add_message(self, message):
        # Adds a message to be displayed to the screen.
        self.messages.insert(0, [message, 200])
    
    def update(self):
        # Each message has a timer value. We decrement
        # each message's timer here, and if a message's
        # timer reaches 0, we remove it from the list.
        for i in list(self.messages):
            i[1] -= 1
            if i[1] == 0: self.messages.remove(i)

class ResultsScreen(UIScreen):
    # A screen that display's the total value of the player's
    # inventory.
    def __init__(self, app):
        super().__init__(app, 240, 20, 0)

        # We count up to the player's inventory's value from 0,
        # and these variables are used to do this.
        self.valueCounter = 0
        self.valueTarget = 0
    
    def start(self):
        super().start()

        self.valueCounter = 0
        self.valueTarget = self.app.player.inventory.calculate_total_value()

        # If the player's inventory has a total value of 0, do not attempt
        # to count up to it.
        if self.valueTarget == 0: self.stopped = True
        else:
            # Otherwise, play a drumroll sound if it isn't already playing.
            self.stopped = False
            self.app.soundPlayer.play_sound(
                "drumroll.ogg",
                loop = True,
                group = self.app.soundPlayer.alwaysAllowGroup + " drumroll",
                volume = 0.4
            )
            # Also prevent the user from continuing to the next screen
            # while we are counting up.
            self.preventContinue = True
        
        # Stop any music currently playing.
        self.app.randomMusicHandler.stop()

        self.app.soundPlayer.play_sound(
            "boom.ogg",
            pitch = 0.75,
            group = self.app.soundPlayer.alwaysAllowGroup
        )
        self.app.soundPlayer.play_sound(
            "wind.ogg",
            group = self.app.soundPlayer.alwaysAllowGroup,
            loop = True,
            pitch = 0.75,
            volume = 0.2
        )
    
    def update(self):
        super().update()

        # If we haven't reached the target value, count up
        # to it. The further away from the value we are, the
        # more we should count up by.
        if self.valueCounter < self.valueTarget:
            self.valueCounter += (self.valueTarget - self.valueCounter) / 40 + 0.001
            # If we have gone past the target value, go back
            # to the target value.
            if self.valueCounter > self.valueTarget:
                self.valueCounter = self.valueTarget
        # If we have reached the target value, stop the drumroll sound,
        # play another sound effect, and let the user continue to the
        # next screen.
        elif not self.stopped:
            self.stopped = True
            self.app.soundPlayer.stop_group(self.app.soundPlayer.alwaysAllowGroup + " drumroll")
            self.app.soundPlayer.play_sound("cash.ogg")
            self.preventContinue = False


    def draw(self):
        self.app.fontLibrary.draw_text(
            self.app.screen,
            f"The total value of your treasure\nis £{self.valueCounter:.2f}!",
            "uncial",
            (WIDTH/2, HEIGHT/2 - 10),
            align = (0.5, 0.5)
        )
        self.app.fontLibrary.draw_text(
            self.app.screen,
            "Press ENTER to continue.",
            "envious serif",
            (WIDTH/2, HEIGHT/2 + 10),
            align = (0.5, 0.5)
        )

        super().draw()

class GameOverScreen(UIScreen):
    # Shown when the player dies.
    def __init__(self, app):
        super().__init__(app, 240, 20, 0)
    
    def start(self):
        super().start()
        self.app.randomMusicHandler.stop()

        self.app.soundPlayer.play_sound(
            "boom.ogg",
            pitch = 0.75,
            group = self.app.soundPlayer.alwaysAllowGroup
        )
        self.app.soundPlayer.play_sound(
            "wind.ogg",
            group = self.app.soundPlayer.alwaysAllowGroup,
            loop = True,
            pitch = 0.75,
            volume = 0.2
        )

    def draw(self):
        self.app.fontLibrary.draw_text(
            self.app.screen,
            "GAME OVER!",
            "uncial",
            (WIDTH/2, HEIGHT/2 - 10),
            align = (0.5, 0.5),
            colour = (255, 50, 100)
        )
        self.app.fontLibrary.draw_text(
            self.app.screen,
            "Press ENTER to continue.",
            "envious serif",
            (WIDTH/2, HEIGHT/2 + 10),
            align = (0.5, 0.5)
        )

        super().draw()

class Vignette:
    def __init__(self, app):
        self.app = app

        self.surface = self.generate_vignette_surface()

    def draw(self):
        self.app.screen.blit(self.surface, (0, 0))
    
    def generate_vignette_surface(self):
        # This method generates a black surface that gets more transparent
        # the closer to the middle you get.
        # First we create a black surface with the dimensions of the screen
        # surface. The pygame.SRCALPHA flag means that each pixel has its
        # own alpha value - by default pygame surfaces have a single alpha
        # value for all pixels, which would not work here.
        surface = pygame.Surface((WIDTH, HEIGHT), flags = pygame.SRCALPHA)
        surface.fill(BLACK)
        # Then get an array that references the alpha values of the surface.
        surfarray = pygame.surfarray.pixels_alpha(surface)
        # Calculating the new alpha values using pixel coordinates.
        x = np.repeat(np.square(np.concatenate(
            (np.arange(WIDTH/2, 0, -1, dtype=np.float32), np.arange(0, WIDTH/2, dtype=np.float32))
        ))[:, np.newaxis], HEIGHT, axis = 1)
        y = np.repeat(np.square(np.concatenate(
            (np.arange(HEIGHT/2, 0, -1, dtype=np.float32), np.arange(0, HEIGHT/2, dtype=np.float32))
        ))[np.newaxis, :], WIDTH, axis = 0)
        distance = np.sqrt(x + y)
        # A small amount of randomness is added to the alpha values to reduce colour banding.
        alpha = np.clip(distance / ((WIDTH * HEIGHT) ** 0.49) + np.random.uniform(-0.02, 0.02, (WIDTH, HEIGHT)), 0, 1) * 255
        # Copying these values into the array that references the surface's
        # alpha values, which means that the alpha values of the surface
        # will be updated.
        # All of this is done using numpy arrays to be as efficient as possible.
        surfarray[:] = alpha.astype(np.uint8)
        # When we first got the alpha value array, the surface was locked,
        # meaning it could not be drawn to or blitted.
        # We need to unlock it to be able to blit it to the screen.
        surface.unlock()
        return surface