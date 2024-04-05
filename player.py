from util import *
from objects import *
from states_definition import *
from animation import *

class Inventory:
    # Items can be added to and removed from the inventory.
    def __init__(self, app, player, capacity):
        self.app = app
        self.player = player

        self.items = []
        self.capacity = capacity
        self.equippedItem = 0

    def add_item(self, item):
        # First we check if the inventory is full - if it is
        # don't attempt to add the item.
        # The return value of this method is a Boolean representing
        # whether the item has been added to the inventory or not.
        if len(self.items) == self.capacity: return False
        # Add the item to the inventory.
        self.items.append(item)
        # Display a message and play a sound to make the fact that
        # an item has been picked up obvious.
        self.app.simpleUI.add_message(f"Found {item.name}.")
        self.app.soundPlayer.stop_group("pickup")
        self.app.soundPlayer.play_preset_positional_sound(
            "pickup",
            pos = self.player.pos,
            group = "pickup"
        )
        return True
    
    def remove_item(self, item):
        # Removes the item from the inventory.
        self.items.remove(item)
        # Calling this method ensures that if we
        # removed the last item in the list, we 
        # wrap back around to the start.
        self.change_equipped_item(0)

    def drop_item(self, item):
        # First we remove the item from the inventory.
        self.remove_item(item)
        # Then we place the item in front of the player.
        item.pos.update(self.player.pos)
        item.pos += pygame.math.Vector2(self.player.radius + item.radius, 0).rotate(self.player.rotation)
        # If the player is already holding an item, we move the item further forward.
        if self.items:
            item.pos += pygame.math.Vector2(item.radius * 2, 0).rotate(self.player.rotation + random.uniform(-90, 90))
        item.previousPos.update(item.pos)
        # Then we actually add the item to the level.
        self.app.levelContainer.objectHandler.add_object(item)
        # We also play a sound when the item is dropped.
        self.app.soundPlayer.play_preset_positional_sound(
            "drop",
            pos = self.player.pos
        )

    def get_equipped_item(self):
        # If the inventory is empty, we just return None.
        if not self.items: return
        # Else return the currently equipped item.
        return self.items[self.equippedItem]

    def change_equipped_item(self, by):
        # Changes the currently equipped item.
        if not self.items:
            self.equippedItem = 0
            return
        self.equippedItem += by
        # If the new equipped item index is greater
        # than the length of the list we wrap back around
        # to the start, or back to the end if the index
        # is less than 0.
        self.equippedItem %= len(self.items)

    def drop_equipped_item(self):
        # Drops the currently equipped item if one is equipped.
        equippedItem = self.get_equipped_item()
        if not equippedItem == None: self.drop_item(equippedItem)

    def calculate_total_value(self):
        # Adds all of the cost values of the items
        # in the inventory and returns the total.
        total = 0
        for item in self.items:
            total += item.cost
        return total

class EquippedObject(VerletObject):
    # This object is displayed in front of the player when an item is equipped. Enemies that collide
    # with this object at a certain angle are damaged if the item has a positive damage value.
    def __init__(self, app, user):
        # This AnimationManager with a single empty animation is used when the player isn't holding
        # anything.
        self.emptyAnimationManager = AnimationManager(app, "items.png", [("empty", Animation(app, 0, 0))])

        super().__init__(
            app,
            (0, 0),
            0,
            {
                "main" : {
                    "notAttacking" : State_EquippedObject_NotAttacking,
                    "attacking" : State_EquippedObject_Attacking
                }
            },
            self.emptyAnimationManager,
            collidable = False
        )

        self.user = user

        # This will be set to the player's rotation. We smoothly
        # rotate towards this value. The player only has 8 possible
        # rotation values, which looks quite stiff - smoothing it
        # out looks more natural.
        self.targetRotation = 0
    
    def update_display(self):
        equippedItem = self.user.inventory.get_equipped_item()
        # If the player hasn't equipped anything, use the empty
        # animation and make this object not collidable. This object
        # will still exist in the world, even when it isn't visible, so
        # we need to set it to not collide with anything.
        if equippedItem == None:
            self.animationManager = self.emptyAnimationManager
            self.collidable = False
        # If the player has something equipped:
        else:
            # We smoothly rotate to match the player's rotation.
            self.targetRotation = self.user.rotation
            angle1 = (self.targetRotation - self.rotation) % 360
            angle2 = angle1 - 360
            if angle1 < -angle2: angle = angle1
            else: angle = angle2
            self.rotation += angle * 0.25
            self.rotation = (self.rotation + 180) % 360 - 180

            # This object should be collidable when it is visible.
            # We give it an animation to match the equipped item.
            self.collidable = True
            self.radius = equippedItem.radius
            self.animationManager = equippedItem.animationManager
            self.pos.update(self.user.pos + pygame.math.Vector2(
                self.user.radius + self.radius, 0
            ).rotate(self.rotation))
            self.previousPos.update(self.pos)
            # We also flip it horizontally if this object is on the
            # left of the player.
            if self.pos.x < self.user.pos.x: self.flipped = True
            elif self.pos.x > self.user.pos.x: self.flipped = False
    
    def update(self):
        self.update_display()
        super().update()

class Player(Entity):
    # The user controls the movement of this class.
    # When its health reaches 0, the run ends.
    def __init__(self, app):
        super().__init__(
            app,
            maxHp = 50,
            speed = 1,
            drops = [],
            attackDamage = 0,
            pos = (0, 0),
            radius = 8,
            states = {
                "main" : {
                    "alive" : State_Alive,
                    "dead" : State_Player_Dead,
                },
                "movement" : {
                    "moving" : State_Player_Movement
                }
            },
            animationManager = AnimationManager(
                app,
                "player.png",
                [
                    ("idle", RotationalAnimation(
                        app,
                        0,
                        *framePresets["idle"],
                        sounds = {
                            0 : "step"
                        }
                    )),
                    ("moving", RotationalAnimation(
                        app,
                        0.2,
                        *framePresets["moving"],
                        sounds = {
                            1 : "step",
                            3 : "step"
                        }
                    ))
                ]
            )
        )
        self.inventory = Inventory(self.app, self, 10)

        self.equippedObject = EquippedObject(self.app, self)
        # If this Boolean is True, we need to add self.equippedObject to the
        # level. This is only the case when we have first entered a new level.
        self.addedEquippedObjectToLevel = False

        self.statusEffectPresets = read_json("jsondata//statuseffects.json")
        self.statusEffects = {}
    
    def update(self):
        super().update()

        # Add self.equippedObject to the level if we haven't already.
        if not self.addedEquippedObjectToLevel:
            self.app.levelContainer.objectHandler.add_object(self.equippedObject)
            self.addedEquippedObjectToLevel = True
        
        # Calculate a tint colour based on the average colour of all
        # of the current status effects (or just white if there aren't
        # any active).
        colour = None
        for effect in list(self.statusEffects.values()):
            effect.update()
            if colour is None: colour = effect.get_flash_colour()
            else: colour = colour.lerp(effect.get_flash_colour(), 0.5)
        if colour is None: colour = WHITE
        self.tint = colour
    
    def damage(self, by, attacker):
        if super().damage(by, attacker):
            # When the player gets damaged, play an extra
            # sound.
            self.app.soundPlayer.stop_group("playerHurt")
            self.app.soundPlayer.play_preset_positional_sound(
                "hurt",
                pos = self.pos,
                group = "playerHurt",
                volume = min(0.4, max(0.15, by / 10))
            )
            return True
        return False
    
    def add_status_effect(self, id):
        # Apply the status effect with the given id.
        # We create a new StatusEffect instance to store in
        # the self.statusEffects dictionary. This will
        # overwrite a previous instance of the same status
        # effect, meaning we cannot have two "poison" status
        # effects active at once, we just replace the first
        # with the second.
        self.statusEffects[id] = StatusEffect(self.app, id, **self.statusEffectPresets[id])

    def remove_status_effect(self, id):
        # Attempt to remove the status effect with the given
        # id. If this is done successfully, post a message.
        if not id in self.statusEffects: return
        self.statusEffects[id].remove()
        del self.statusEffects[id]
    
    def get_camera_target_pos(self):
        # If the player isn't moving, this returns the player's position.
        # If the player is moving, this returns a position just in front
        # of the player. This prevents the camera from lagging behind the
        # player, instead it shows slightly more of the level in the
        # direction the player is moving.
        return self.pos + self.velocity * 15

class StatusEffect:
    # Represents a status effect that can be applied
    # to the player.
    def __init__(
            self,
            app,
            id,
            activeTimer,
            damage = 0,
            damageTimer = 0,
            speedMultiplier = 1,
            text = "",
            colour = RED,
            screenShake = 0,
            flashRate = 5,
            sound = None
        ):
        self.app = app
        
        self.id = id

        # self.activeTimer is the length of time this status
        # effect should last.
        self.activeTimer = activeTimer
        # self.damage is the amount of damage that should be
        # applied every self.maxDamageTimer frames.
        self.damage = damage
        self.maxDamageTimer = damageTimer
        self.damageTimer = self.maxDamageTimer
        # The player's speed will be multiplied by this value
        # when this status effect is applied.
        self.speedMultiplier = speedMultiplier
        # This is the name of this status effect, displayed
        # in a message when it is first applied and when it
        # ends.
        self.text = text
        # This is the colour that the player is tinted when
        # this status effect is applied.
        self.colour = pygame.Color(colour)
        # If this value is anything other than 0, the screen
        # will shake while this status effect is active.
        self.screenShake = screenShake
        # This is the rate that the player flashes with the
        # colour defined in self.colour.
        self.flashRate = flashRate
        # A sound that should be played while this status
        # effect is active.
        self.sound = sound
        self.soundGroup = "status_" + self.text
        
        self.app.simpleUI.add_message(self.text)
    
    def update(self):
        # Decrement self.activeTimer and remove this status
        # effect from the player if the timer reaches 0 (or
        # do nothing if self.activeTimer == None, meaning
        # the status effect should be active forever).
        if not self.activeTimer is None:
            self.activeTimer -= 1
            if self.activeTimer <= 0:
                self.app.player.remove_status_effect(self.id)
        
        self.app.camera.shake(self.screenShake)
        
        # Decrement self.damageTimer and damage the player
        # when this status effect reaches 0.
        self.damageTimer -= 1
        if self.damageTimer <= 0:
            self.damageTimer = self.maxDamageTimer
            self.app.player.change_hp(-self.damage)

        # Play this status effect's sound if it isn't already playing.
        if not self.sound is None and not self.app.soundPlayer.check_sound_exists(self.soundGroup):
            self.app.soundPlayer.play_preset_sound(
                self.sound,
                group = self.soundGroup,
                loop = True
            )
    
    def get_flash_colour(self):
        # We use sin here to cause the player to flash over time.
        return self.colour.lerp(WHITE, abs(math.sin(self.app.time * self.flashRate)) * 0.8)
    
    def remove(self):
        self.app.soundPlayer.stop_group(self.soundGroup)
        self.app.simpleUI.add_message(f"No longer {self.text}")