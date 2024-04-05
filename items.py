from util import *
from objects import *
from animation import *

class Item(VerletObject):
    # Can be found in the level or stored in the player's inventory and used by the player.
    def __init__(self, app, pos, name, cost, attackDamage, consumeHp, animation, durability, removesStatusEffects=[]):
        # Items use an empty state machine and a simple animation manager with only one animation.
        super().__init__(
            app,
            pos,
            8,
            {},
            AnimationManager(app, "items.png", [("main", animation)]),
            flipped = random.random() > 0.5
        )

        self.name = name
        self.cost = cost
        self.attackDamage = attackDamage
        self.consumeHp = consumeHp
        self.durability = durability
        # This is a list of all of the status effects that this item can remove when it
        # is consumed. Used, for example, in the antidote item which cures poison when
        # eaten.
        self.removesStatusEffects = removesStatusEffects

        # This is a list of all of the pixel colours in each frame of the item's animation.
        # The particle colours when this item breaks are randomly picked from this list.
        self.colours = self.get_sprite_colours()
    
    def get_sprite_colours(self):
        # This method iterates through each frame in the item's animation and adds each pixel
        # colour to a list.
        sprites = [self.animationManager.spritesheet.get(i) for i in self.animationManager.animations["main"].sprites]
        pixels = []

        for sprite in sprites:
            # Iterating over each pixel in the sprite. This quite slow so isn't feasible
            # to do for every item every frame, but we are only calling this method once
            # when the item is instanciated so it is fine.
            for y in range(sprite.get_height()):
                for x in range(sprite.get_width()):
                    colour = sprite.get_at((x, y))
                    # We do not want to include the colourkey as it is meant to be transparent.
                    if colour != pygame.Color(self.animationManager.spritesheet.colourkey):
                        pixels.append(colour)
        
        return pixels