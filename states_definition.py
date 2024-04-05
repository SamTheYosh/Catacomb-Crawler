import random, pygame

from util import *
from states import *
from objects import *
from items import *

# GENERAL PURPOSE STATES

class State_Alive(State):
    def update(self):
        if self.obj.hp <= 0:
            self.stateMachine.set_state("dead")

class State_Dead(State):
    def enter(self):
        # First we remove this entity from the world.
        self.app.levelContainer.objectHandler.remove_object(self.obj)
        # If no item drops are defined for this entity, we just end the method.
        if not self.obj.drops: return
        # Otherwise, we pick some random items to drop.
        ids = [i[0] for i in self.obj.drops]
        # Items have different weight values, which determine the probability
        # of the item being picked.
        weights = [i[1] for i in self.obj.drops]
        # Appending None to the list of items allows us to randomly pick not
        # to drop an item.
        ids.append(None)
        weights.append(1)
        # The maximum number of items that can be dropped is 3.
        for id in random.choices(ids, weights, k = 3):
            # None means don't drop an item.
            if id is None: continue
            # Here we create the item and add it to the world at the entity's last position
            # (with a slight random offset).
            item = self.app.jsonDataManager.create_item(id, self.obj.pos)
            item.pos += pygame.math.Vector2(random.uniform(5, 10), 0).rotate(random.uniform(0, 360))
            item.previousPos.update(item.pos)
            # We also apply the entity's velocity before they died to the item (if we don't do
            # this, the item appears to stop unnaturally, not conserving the momentum of the
            # entity).
            item.accelerate(self.obj.velocity)
            self.app.levelContainer.objectHandler.add_object(item)

class State_Idle(State):
    def setup(self):
        self.obj.pathfindTarget = pygame.math.Vector2()
    
    def enter(self):
        self.obj.pathfindTarget = pygame.math.Vector2()

    def update(self):
        self.obj.animationManager.set("idle")
        # If we are close enough to the player, start following them.
        if self.app.player.pos.distance_to(self.obj.pos) <= 250:
            self.stateMachine.set_state("following")

class State_Following(State):
    def update(self):
        self.obj.animationManager.set("moving")
        # If we are still close enough to the player, keep following them.
        if self.app.player.pos.distance_to(self.obj.pos) <= 250:
            self.obj.pathfindTarget = self.app.player.pos.copy()
        # Else, pathfind towards the last position the player was in where
        # we were close enough to them.
        # If we are close enough to this position, switch back to the being idle.
        if self.obj.pos.distance_to(self.obj.pathfindTarget) < 5:
            self.stateMachine.set_state("idle")
        else:
            # Pathfind towards this entity's pathfinding target position.
            pathfindingVector = self.app.aStarPathfinder.pathfind(self.obj, self.obj.pathfindTarget, self.app.player)
            self.obj.rotation = pygame.math.Vector2().angle_to(pathfindingVector)
            # Adding some random variation in the entity's movements, looks more natural.
            pathfindingVector = pathfindingVector.rotate(random.uniform(-90, 90))
            self.obj.accelerate(pathfindingVector * self.obj.speed)

class State_NotAttacking(State):
    def setup(self):
        self.obj.attackTarget = None

    def collide(self, obj):
        # If we are close enough to the player and facing towards the player,
        # attack them.
        if obj == self.app.player:
            angle = abs(self.obj.rotation - pygame.math.Vector2(1, 0).angle_to(obj.pos - self.obj.pos))
            if angle < 45:
                self.obj.attackTarget = obj
                self.stateMachine.set_state("attacking")

class State_Attacking(State):
    def enter(self):
        # Damage the attack target and sometimes apply a status effect to
        # them if one is defined.
        # The timer is used to ensure the entity cannot attack again for a
        # certain length of time after attacking once.
        self.timer = 30
        self.obj.attackTarget.change_hp(-self.obj.attackDamage, self.obj)
        if (
            self.obj.attackStatusEffect != None and
            random.random() <= self.obj.attackStatusEffectChance
        ):
            self.obj.attackTarget.add_status_effect(self.obj.attackStatusEffect)

    def update(self):
        # Wait for the timer to reach 0, if it does we can attack again.
        self.timer -= 1
        if self.timer == 0:
            self.stateMachine.set_state("notAttacking")



# ENEMY STATES

class State_Skeleton_Dead(State):
    def enter(self):
        # Set up a timer, when this timer ends the skeleton gets back up.
        self.timer = 300
        # While dead, the skeleton shouldn't do anything and shouldn't be
        # able to be attacked.
        self.obj.stateMachines["movement"].set_active(False)
        self.obj.stateMachines["attacks"].set_active(False)
        self.obj.invulnerable = True

    def update(self):
        self.obj.animationManager.set("dead")
        # If the timer reaches 0, the skeleton revives itself and gets
        # back up.
        self.timer -= 1
        if self.timer == 0:
            self.obj.invulnerable = False
            self.obj.stateMachines["movement"].set_active(True)
            self.obj.stateMachines["attacks"].set_active(True)
            self.obj.hp = self.obj.maxHp
            self.stateMachine.set_state("alive")

class State_BigSlime_Dead(State):
    def enter(self):
        # When a Big Slime dies, it spawns several smaller slimes in its place.
        import enemies
        for _ in range(random.randint(2, 4)):
            enemy = enemies.classes[3](self.app, self.obj.pos)
            enemy.pos += pygame.math.Vector2(random.uniform(5, 10), 0).rotate(random.uniform(0, 360))
            enemy.previousPos.update(enemy.pos)
            enemy.accelerate(self.obj.velocity)
            self.app.levelContainer.objectHandler.add_object(enemy)
        self.app.levelContainer.objectHandler.remove_object(self.obj)

class State_Python_Following(State):
    def update(self):
        self.obj.animationManager.set("moving")
        if self.app.player.pos.distance_to(self.obj.pos) <= 250:
            self.obj.pathfindTarget = self.app.player.pos.copy()
        if self.obj.pos.distance_to(self.obj.pathfindTarget) < 5:
            self.stateMachine.set_state("idle")
        else:
            # The Python enemy only moves on specific animation frames, making it
            # look more like it is slithering along the ground.
            if (
                self.obj.animationManager.get_frame_index() % 2 == 0 or not
                self.obj.animationManager.currentAnimationObject.justChangedFrame
            ): return
            pathfindingVector = self.app.aStarPathfinder.pathfind(self.obj, self.obj.pathfindTarget, self.app.player)
            self.obj.rotation = pygame.math.Vector2().angle_to(pathfindingVector)
            pathfindingVector = pathfindingVector.rotate(random.uniform(-20, 20))
            self.obj.accelerate(pathfindingVector * self.obj.speed)

class State_SporeCloud_Following(State):
    def update(self):
        self.obj.animationManager.set("moving")
        if self.app.player.pos.distance_to(self.obj.pos) <= 250:
            self.obj.pathfindTarget = self.app.player.pos.copy()
        if self.obj.pos.distance_to(self.obj.pathfindTarget) < 5:
            self.stateMachine.set_state("idle")
        else:
            # Spore clouds move with a lot of randomness, but they still move in the general direction
            # of the player.
            pathfindingVector = self.app.aStarPathfinder.pathfind(self.obj, self.obj.pathfindTarget, self.app.player)
            self.obj.rotation = pygame.math.Vector2().angle_to(pathfindingVector)
            pathfindingVector = pathfindingVector.rotate(random.uniform(-90, 90))
            pathfindingVector += pygame.math.Vector2(random.uniform(0, 6), 0).rotate(random.uniform(0, 360))
            self.obj.accelerate(pathfindingVector * self.obj.speed)

class State_Horseman_Following(State_Python_Following):
    def update(self):
        super().update()
        if self.app.soundPlayer.check_sound_exists(self.obj): return
        if random.random() < 0.99: return
        self.app.soundPlayer.play_preset_positional_sound(
            "horse",
            pos = self.obj.pos,
            group = self.obj
        )

class State_Scientist_Idle(State):
    def setup(self):
        self.obj.rotation = random.uniform(0, 360)

    def update(self):
        self.obj.animationManager.set("idle")
        # If we are close enough to the player, start running away from them.
        if self.app.player.pos.distance_to(self.obj.pos) <= 100:
            self.stateMachine.set_state("running")

class State_Scientist_Running(State):
    def update(self):
        self.obj.animationManager.set("moving")
        # If we are still close enough to the player, keep running away.
        if self.app.player.pos.distance_to(self.obj.pos) <= 250:
            # Pathfind towards a point in the opposite direction to the
            # player.
            pathfindTarget = self.obj.pos - (self.app.player.pos - self.obj.pos) * 10
            pathfindingVector = self.app.aStarPathfinder.pathfind(
                self.obj,
                pathfindTarget,
                self.app.player
            )
            self.obj.rotation = pygame.math.Vector2().angle_to(pathfindingVector)
            # Adding some random variation in the entity's movements, looks more natural.
            pathfindingVector = pathfindingVector.rotate(random.uniform(-90, 90))
            self.obj.accelerate(pathfindingVector * self.obj.speed)
        else:
            self.stateMachine.set_state("idle")
            


# PLAYER STATES

class State_Player_Dead(State):
    def enter(self):
        # When the player dies, we transition to the game over screen.
        self.app.set_game_state(3)

class State_Player_Movement(State):
    def update(self):
        # Moving the player character based on the player's inputs.
        movement = self.app.eventHandler.get_movement_vector_normalised()
        movement *= 0.1

        # Applies the speed multiplier values of any status effects currently active.
        for effect in self.obj.statusEffects.values():
            if effect.speedMultiplier == "mushroom":
                multiplier = math.sin(self.app.time * 2)
            else: multiplier = effect.speedMultiplier
            movement *= multiplier

        # Finally moves the player and updates self.obj.rotation,
        # which controls animations and attacking.
        self.obj.accelerate(movement)
        if movement.magnitude_squared() > 0:
            self.obj.animationManager.set("moving")
            self.obj.rotation = pygame.math.Vector2((1, 0)).angle_to(movement)
        else:
            self.obj.animationManager.set("idle")
            
        
        equippedItem = self.obj.inventory.get_equipped_item()
        # If we have an item equipped and the L button has been pressed, consume the
        # item, and depending on the item change the player's HP and remove status effects.
        # Also display a message and play a sound.
        if equippedItem != None and self.app.eventHandler.get_key_just_pressed(pygame.K_l):
            self.obj.change_hp(equippedItem.consumeHp)
            self.obj.inventory.remove_item(equippedItem)
            self.app.simpleUI.add_message(f"Consumed {equippedItem.name}.")
            for effect in equippedItem.removesStatusEffects:
                self.obj.remove_status_effect(effect)
            self.app.soundPlayer.play_preset_positional_sound(
                "gulp",
                pos = self.obj.pos
            )
        # Change the equipped item using O and P.
        if self.app.eventHandler.get_key_just_pressed(pygame.K_o):
            self.obj.inventory.change_equipped_item(-1)
        if self.app.eventHandler.get_key_just_pressed(pygame.K_p):
            self.obj.inventory.change_equipped_item(1)
        # Drop the equipped item if 0 is pressed.
        if self.app.eventHandler.get_key_just_pressed(pygame.K_0):
            self.obj.equippedObject.update_display()
            self.obj.inventory.drop_equipped_item()
            if equippedItem: self.app.simpleUI.add_message(f"Dropped {equippedItem.name}.")

    def collide(self, obj):
        # If we collide with an item and space is pressed, pick up the item.
        if isinstance(obj, Item):
            if obj in self.obj.inventory.items: return
            if self.app.eventHandler.get_key_pressed(pygame.K_SPACE):
                if self.obj.inventory.add_item(obj):
                    self.app.levelContainer.objectHandler.remove_object(obj)
                    self.obj.equippedObject.update_display()

class State_EquippedObject_NotAttacking(State):
    def setup(self):
        self.obj.attackTarget = None

    def collide(self, obj):
        # If we collide with an item and space is pressed, pick up the item.
        if isinstance(obj, Item):
            if obj in self.obj.user.inventory.items: return
            if self.app.eventHandler.get_key_pressed(pygame.K_SPACE):
                if self.obj.user.inventory.add_item(obj):
                    self.app.levelContainer.objectHandler.remove_object(obj)
                    self.obj.update_display()
        # If we collide with an entity and we are facing the entity, attack
        # the entity.
        elif isinstance(obj, Entity):
            if obj == self.obj.user: return
            equippedItem = self.obj.user.inventory.get_equipped_item()
            if equippedItem is None: return
            angle = abs(self.obj.rotation - pygame.math.Vector2(1, 0).angle_to(obj.pos - self.obj.pos))
            if angle < 45:
                self.obj.attackTarget = obj
                self.obj.attackDamage = equippedItem.attackDamage
                self.stateMachine.set_state("attacking")

class State_EquippedObject_Attacking(State):
    def enter(self):
        self.timer = 5
        # Damage the attack target.
        if self.obj.attackTarget.change_hp(-self.obj.attackDamage, self.obj.user):
            equippedItem = self.obj.user.inventory.get_equipped_item()
            # If the item uses the durability system, decrement its durability value.
            if equippedItem.durability != -1:
                equippedItem.durability -= 1
                # If the item runs out of durability, remove it from the player's
                # inventory, create a particle effect, play a sound effect and post
                # a message.
                if equippedItem.durability == 0:
                    self.obj.user.inventory.remove_item(equippedItem)
                    self.app.soundPlayer.play_preset_positional_sound(
                        "break",
                        pos = self.obj.pos
                    )
                    self.app.simpleUI.add_message(f"{equippedItem.name} broke!")
                    self.app.particleEffectsManager.create_effect(
                        0,
                        self.obj.pos,
                        6,
                        self.obj.velocity,
                        colour = equippedItem.colours
                    )

    def update(self):
        self.timer -= 1
        if self.timer == 0:
            self.stateMachine.set_state("notAttacking")



# OTHER STATES

class State_Chest_Closed(State):
    def enter(self):
        self.obj.animationManager.set("closed")

    def collide(self, obj):
        if obj == self.app.player:
            self.stateMachine.set_state("open")
            

class State_Chest_Open(State):
    def enter(self):
        # When a chest is opened, it should no longer be collidable.
        # It also spills out its contents into the level, along with
        # a sound.
        self.obj.collidable = False
        self.app.soundPlayer.play_positional_sound(
            "chest.ogg",
            self.obj.pos,
            pitch = random.uniform(0.9, 1.1)
        )
        self.obj.animationManager.set("open")
        for id in self.obj.contains:
            item = self.app.jsonDataManager.create_item(id, self.obj.pos)
            item.pos += pygame.math.Vector2(random.uniform(5, 10)).rotate(random.uniform(0, 360))
            item.previousPos.update(item.pos)
            self.app.levelContainer.objectHandler.add_object(item)



# TEST STATES

class State_Test_Idle(State):
    def setup(self):
        self.timer = 0
    
    def enter(self):
        # Wait a random amount of time before transitioning
        # to the moving state.
        self.timer = random.uniform(30, 120)
        self.obj.animationManager.set("idle")
    
    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.stateMachine.set_state("moving")

class State_Test_Moving(State):
    def setup(self):
        self.timer = 0
    
    def enter(self):
        # Wait a random amount of time before transitioning
        # back to the idle state.
        self.timer = random.uniform(30, 120)
        self.obj.animationManager.set("moving")
        self.obj.rotation = random.uniform(0, 360)
    
    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.stateMachine.set_state("idle")
        
        self.obj.rotation += random.uniform(-10, 10)
        self.obj.rotation %= 360
        self.obj.accelerate(pygame.math.Vector2(0.05, 0).rotate(self.obj.rotation))