from util import *
from animation import *
from items import *

class JSONDataManager:
    # Allows items and objects to be easily created using presets
    # defined in external .json files.
    def __init__(self, app):
        self.app = app
        self.itemData = read_json("jsondata//items.json")
        self.objectData = read_json("jsondata//objects.json")

    def create_item(self, id, pos = (0, 0)):
        # Creates a new Item using data from items.json with the given id.
        data = self.itemData[id]
        animation = Animation(self.app, data["animationSpeed"], *data["animationSprites"])
        return Item(
            self.app,
            pos,
            data["name"],
            data["cost"],
            data["attackDamage"],
            data["consumeHp"],
            animation,
            data["durability"],
            data["removesStatusEffects"]
        )

    def create_object(self, id, pos = (0, 0)):
        # Creates a new Object using data from objects.json with the given id.
        data = self.objectData[id]
        return Object(
            self.app,
            pos,
            data["radius"],
            {},
            AnimationManager(
                self.app,
                data["spritesheet"],
                [("main", Animation(self.app, data["animationSpeed"], *data["animationSprites"]))]
            ),
            sound = data["sound"],
            # The object's sprite has a chance of being flipped horizontally to add some
            # variation to it.
            flipped = random.random() > 0.5
        )