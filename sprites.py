import pygame

from util import *

class SpritesheetManager:
    # Loads and provides access to spritesheets.
    def __init__(self, app):
        self.app = app
        self.spritesheets = {}
        self.load_many(read_json("jsondata//spritesheets.json"))

    def load(self, filename, spriteWidth, spriteHeight, colourkey = BLACK):
        self.spritesheets[filename] = Spritesheet(self.app, filename, spriteWidth, spriteHeight, colourkey)

    def load_many(self, spritesheets):
        for args in spritesheets:
            self.load(*args)

    def get(self, name):
        return self.spritesheets[name]

class Spritesheet:
    # Splits a given image up into individual sprites that can be
    # accessed and drawn to the screen.
    def __init__(self, app, filename, spriteWidth, spriteHeight, colourkey = BLACK):
        self.app = app
        self.load_image("sprites//" + filename, colourkey)

        self.spriteWidth, self.spriteHeight = spriteWidth, spriteHeight
        self.sprites = self.slice(self.image)
    
    def load_image(self, filename, colourkey = BLACK):
        # If we have already loaded the image, do not attempt
        # to load it again.
        try: return self.image
        except: pass
        # Otherwise load the image and set its colourkey (transparent
        # colour).
        self.image = pygame.image.load(filename).convert()
        self.colourkey = colourkey
        self.image.set_colorkey(colourkey)

    def slice(self, image):
        # This method takes an image and uses given sprite dimensions
        # to split it into several sprites.
        self.spritesWidth = image.get_width() // self.spriteWidth
        self.spritesHeight = image.get_height() // self.spriteHeight

        sprites = []
        for y in range(self.spritesHeight):
            for x in range(self.spritesWidth):
                # The use of the pygame.Surface.subsurface() method
                # means that the sprites will reference the original
                # image, saving memory.
                sprites.append(image.subsurface(
                    x * self.spriteWidth,
                    y * self.spriteHeight,
                    self.spriteWidth,
                    self.spriteHeight
                ))
        
        return sprites

    def get(self, x, y = 0):
        # This method provides two indexing modes:
        # If only x is provided, we just treat it as an index.
        # If x and y are provided, we treat them as coordinates
        # to access sprites as they were laid out on the original
        # image.
        return self.sprites[x + y * self.spritesWidth]

    def draw(self, surface, pos, spriteX, spriteY = None):
        # Gets a sprite using self.get() and draws it to the given
        # surface at the given position.
        surface.blit(self.get(spriteX, spriteY), pos)