import pygame, random

from util import *
from sound import *
from objects import *
from boundaries import *
from music import *
import enemies

class LevelContainer:
    # Has an ObjectHandler and a BoundaryHandler and calls their
    # update and draw methods.
    def __init__(self, app, boundaryHandler, objectHandler):
        self.app = app
        self.boundaryHandler = boundaryHandler
        self.objectHandler = objectHandler

    def update(self):
        self.objectHandler.update()

    def draw(self):
        # The order we draw these in is important.
        # Anything we draw first will appear below
        # anything drawn later.
        # Here we draw the lower layer of the boundaries,
        # then all of the objects, then the upper layer
        # of the boundaries.
        self.boundaryHandler.draw_lower_layer()
        self.objectHandler.draw()
        self.boundaryHandler.draw_upper_layer()

class LevelGenerator:
    # Generates levels!
    def __init__(self, app):
        self.app = app

        self.levelCounter = 0
        self.levelGenerationData = read_json("jsondata//levelgen.json")
        self.presetRoomsData = read_json("jsondata//presetrooms.json")
        # When we want to generate a new level, we only want to load new level
        # generation arguments if the level theme has changed. This variable
        # keeps track of whether the level theme has changed.
        self.previousLevelKey = None

    def load_level_generation_data(self):
        # Here we find which level theme to use based on the value
        # of self.levelCounter. Since there isn't a unique theme
        # for every level, we need to find the theme with the highest
        # key value that is less than self.levelCounter.
        key = "0"
        for i in self.levelGenerationData:
            if int(i) <= self.levelCounter and int(i) > int(key):
                key = i
        # If the level theme hasn't changed, we don't need to load
        # in all of its data again, so we return.
        if key == self.previousLevelKey: return
        self.previousLevelKey = key

        # Here we populate this class's attributes with the data
        # for the current level theme.
        data = self.levelGenerationData[key]

        self.levelName = data["levelName"]
        self.possibleObjects = data["possibleObjects"]
        self.possibleEnemies = data["possibleEnemies"]
        self.possibleChestItems = data["possibleChestItems"]
        self.presetRooms = [self.presetRoomsData[i] for i in data["presetRooms"]]
        self.decorationObjects = data["decorationObjects"]
        self.decorationDensity = data["decorationDensity"]
        self.fillArguments = data["fillArguments"]
        try: self.friction = data["friction"]
        except: self.friction = 0.95
        try: self.traction = data["traction"]
        except: self.traction = 1
        self.jaggedness = data["jaggedness"]

        # We also create a new RandomMusicHandler instance and stop
        # the previous RandomMusicHandler.
        self.app.randomMusicHandler.stop()
        self.app.randomMusicHandler = RandomMusicHandler(
            self.app.soundPlayer,
            data["randomMusicDirectory"],
            data["randomMusicChannels"]
        )

    def next_level(self):
        # Increments the level counter and generates a new level.
        self.levelCounter += 1
        self.load_level_generation_data()
        return self.generate_level()

    def generate_level(self):
        # This method generates a new level in the form of a LevelContainer.
        # First we create a list to store rooms in.
        rooms = []
        # We also create a list to store attach points, which are points
        # that new rooms can be created at. Attach points have a position
        # and a direction. To start with we create an attach point at (0, 0)
        # with a random direction.
        attachPoints = []
        attachPoints.append((pygame.math.Vector2(), random.uniform(0, 360)))

        # We set a random maximum number of rooms to generate, meaning
        # that levels will vary in size.
        counter = random.randint(10, 30)
        # Then we loop until this maximum is reached or we run out
        # of attach points to create new rooms at.
        while counter > 0 and attachPoints:
            # We pick a random attach point to create a new
            # room at, and remove it from the list of attach points
            # to ensure we don't try to create two rooms at the same
            # point.
            attachPoint = random.choice(attachPoints)
            attachPoints.remove(attachPoint)
            # Then we generate a new room (this can either be a simple
            # room with a single circle or a preset room with a more
            # complex structure). These rooms are stored as 
            # LevelGeneratorRooms.
            room = self.generate_room()
            # We adjust the new room's position and rotation to match
            # that of the attach point we want to create it at.
            # Some randomness is added to the rotation to allow for
            # levels to randomly wind and turn instead of being just
            # a straight line.
            room.position = attachPoint[0]
            room.rotation = attachPoint[1] + random.uniform(-60, 60)
            # This room could have some attach points of its own, so
            # we add these to the list. New rooms can generate at these
            # points.
            attachPoints += room.get_attach_points()
            # Finally we append the new room to the list of rooms
            # and decrement the counter.
            rooms.append(room)
            counter -= 1

        # Now we want to turn the LevelGeneratorRooms into
        # Boundaries and Objects which can be used in gameplay.
        # This is done using LevelGeneratorRoom's flatten() method,
        # which produces a list of all of the objects in that room
        # and a list of all of the boundaries that make up the room,
        # with their positions offset by the room's position and rotation
        # values.
        totalObjects = []
        totalBoundaries = []
        for room in rooms:
            objects, boundaries = room.flatten()
            totalObjects += objects
            totalBoundaries += boundaries

        # Now we create an ObjectHandler and add all of the Objects from the list
        # we just created to it.
        objectHandler = ObjectHandler(self.app)
        for obj in totalObjects:
            # If an object is too close to the player, we don't add it to the
            # object handler. We don't want the player to start a level and instantly
            # be hit by an enemy who spawned directly on top of them.
            if type(obj) != Exit and type(obj) != RunExit and obj.pos.distance_to((0, 0)) < 250: continue
            try: obj.previousPos.update(obj.pos)
            except: pass
            objectHandler.add_object(obj)
        # We also create a BoundaryHandler and add all of the Boundaries from the
        # list we made to it.
        boundaryHandler = BoundaryHandler(self.app, self.fillArguments)
        for boundary in totalBoundaries:
            boundaryHandler.add_boundary(boundary)
        
        # Then we add an Exit and a RunExit, to allow the player to proceed to the next
        # level or to end the current run.
        # The Exit will be in the centre of the a boundary that is far from the player's
        # starting position and was also added to the level later on, so should take longer
        # to get to.
        objectHandler.add_object(Exit(
            self.app,
            sorted(
                boundaryHandler.boundaries,
                key = lambda x:
                (boundaryHandler.boundaries.index(x) ** 0.5) *
                x.pos.magnitude()
            )[-1].pos
        ))
        # The RunExit is placed within the first boundary added to the level, meaning it
        # will be created next to the player.
        # Its position has an offset to make sure it doesn't appear directly on top
        # of the player.
        objectHandler.add_object(RunExit(
            self.app,
            boundaryHandler.boundaries[0].pos +
            pygame.math.Vector2(
                boundaryHandler.boundaries[0].radius * 0.5,
                0
            ).rotate(random.uniform(0, 360))
        ))
        
        # Next we are going to decorate the level with SimpleObjects.
        # To do this we need to find the bounding box of the level, to
        # provide upper and lower bounds to randomly generate positions
        # between.
        boundingBox = boundaryHandler.get_bounding_box()
        # We use the decoration density argument and the area of the
        # bounding box to calculate how many SimpleObjects to create.
        counter = boundingBox.width * boundingBox.height * 0.0001 * self.decorationDensity
        while counter > 0:
            # First we generate a random position inside the bounding
            # box.
            pos = pygame.math.Vector2(
                random.uniform(boundingBox.left, boundingBox.right),
                random.uniform(boundingBox.top, boundingBox.bottom)
            )

            # Then we get a Perlin noise value for this position.
            perlinValue = self.app.perlinNoise.noise(pos.x, pos.y, 0.005)
            perlinValue /= 2
            # We do not create the decoration if this value is too high.
            # This leads to natural-looking random clumps of decorations
            # across the level, thanks to using Perlin noise instead of
            # white noise.
            if 0.08 > perlinValue: continue
            
            # Then we create a new SimpleObject.
            obj = SimpleObject(
                self.app,
                pos,
                8,
                "decor.png",
                random.choice(self.decorationObjects)
            )

            # If this object isn't inside the boundaries of the level,
            # we don't add it to the level.
            obj.find_overlapping_grid_spaces()
            if not boundaryHandler.circle_inside_boundaries(obj): continue
            
            # Finally we add the SimpleObject to the level.
            objectHandler.add_object(obj)
            
            # Because we have added the object, we decrement the counter.
            # If we reached the continue keyword above, we wouldn't have
            # added the object to the level so we don't decrement the counter.
            counter -= 1

        # Now we create the graph that the AStarPathfinder class will use for
        # pathfinding, using the BoundaryHandler's generate_nodes_and_edges()
        # method.
        self.app.aStarPathfinder.setup_graph(*boundaryHandler.generate_nodes_and_edges())
        # And finally we create a new LevelContainer containing the BoundaryHandler
        # and the ObjectHandler, which is returned.
        return LevelContainer(self.app, boundaryHandler, objectHandler)

    def generate_room(self):
        # This method randomly picks between a preset room or a simple room.
        # There is a high chance of picking a preset room. If there are no preset
        # rooms defined for the current level theme, then we do not attempt to
        # generate one.
        if random.random() < 0.9 or not self.presetRooms: return self.generate_simple_room()
        else: return self.generate_preset_room()

    def generate_simple_room(self):
        # This method creates a simple room consisting of one circle, with
        # 1-2 attach points and some randomly placed objects, enemies or chests.
        radius = random.uniform(40, 150)
        # The position is (radius, 0) to ensure that the room's circumference passes
        # through (0, 0). This means that the room will pivot correctly around (0, 0)
        # when rotated and will be placed correctly at attach points.
        pos = pygame.math.Vector2(radius, 0)
        objects = []
        boundaries = []
        attachPoints = []

        # First we create a new boundary
        boundaries.append(Boundary(self.app, pos, radius, self.jaggedness))
        # Then we add 1 or 2 attach points to the boundary, allowing
        # other boundaries to attach to it.
        counter = 0
        while counter == 0 or (random.random() > 0.7 and counter < 2):
            attachPoints.append((pygame.math.Vector2(radius - 20, 0).rotate(random.uniform(-60, 60)) + (radius, 0), 0))
            counter += 1
        
        # There is a chance for up to 2 random objects to be added to
        # the room at a random position. The possible objects are defined
        # in the level theme.
        counter = 0
        while random.random() > 0.6 and counter < 2:
            obj = self.get_random_object()
            if not obj: break
            obj.pos.update(pygame.math.Vector2(random.uniform(radius * 0.5, radius - 20), 0).rotate(random.uniform(0, 360)) + (radius, 0))
            objects.append(obj)
            counter += 1
        
        # Similarly there is a random chance of adding up to 2 enemies.
        counter = 0
        while random.random() > 0.6 and counter < 2:
            enemy = self.get_random_enemy()
            if not enemy: break
            enemy.pos.update(pygame.math.Vector2(random.uniform(0, radius - 20), 0).rotate(random.uniform(0, 360)) + (radius, 0))
            enemy.previousPos.update(enemy.pos)
            objects.append(enemy)
            counter += 1
        
        # And up to 2 chests.
        counter = 0
        while random.random() > 0.8 and counter < 2:
            chest = self.get_random_chest()
            if not chest: break
            chest.pos.update(pygame.math.Vector2(random.uniform(0, radius - 20), 0).rotate(random.uniform(0, 360)) + (radius, 0))
            objects.append(chest)
            counter += 1
        
        # Finally we create a new LevelGeneratorRoom, passing in the lists
        # we have just filled.
        return LevelGeneratorRoom(self.app, objects, boundaries, attachPoints)

    def generate_preset_room(self):
        # This method reads preset room data from presetrooms.json and uses
        # it to create a LevelGeneratorRoom.
        # First we pick a random preset room to create.
        roomData = random.choice(self.presetRooms)
        objects = []
        boundaries = []
        attachPoints = []

        # Then we interpret this preset room data, adding objects, enemies, chests, boundaries
        # and attach points as it has defined.
        for objData in roomData["objects"]:
            objects.append(self.app.jsonDataManager.create_object(objData["id"], objData["pos"]))
        
        for enemyData in roomData["enemies"]:
            objects.append(enemies.classes[enemyData["id"]](self.app, enemyData["pos"]))
        
        for chestData in roomData["chests"]:
            objects.append(Chest(self.app, chestData["pos"], chestData["items"]))
        
        for boundaryData in roomData["boundaries"]:
            boundaries.append(Boundary(self.app, boundaryData["pos"], boundaryData["radius"], self.jaggedness))
        
        for attachPointData in roomData["attachPoints"]:
            attachPoints.append((pygame.math.Vector2(attachPointData[0]), attachPointData[1]))
        
        # Then we put all of this together into a LevelGeneratorRoom and return it.
        return LevelGeneratorRoom(self.app, objects, boundaries, attachPoints)

    def get_random_object(self):
        # This method returns a random object from the list
        # defined in the current level theme.
        # If no object ids are given, don't attempt to
        # randomly pick and create one.
        if not self.possibleObjects: return

        # Randomly pick an object id. Each object id has
        # an associated weight value - a higher weight means
        # an object is more likely to be picked.
        objectIds = [i[0] for i in self.possibleObjects]
        objectWeights = [i[1] for i in self.possibleObjects]
        objectId = random.choices(objectIds, objectWeights)[0]
        # Finally create the object using the object id we picked.
        return self.app.jsonDataManager.create_object(objectId)

    def get_random_chest(self):
        # This method creates a chest filled with random
        # items, defined in the current level theme.
        # If no item ids are given, don't attempt to
        # create a chest.
        if not self.possibleChestItems: return

        itemIds = [i[0] for i in self.possibleChestItems]
        itemWeights = [i[1] for i in self.possibleChestItems]

        # We create a Chest with random objects inside. Each item
        # has a weight value - a higher weight value means a higher
        # chance of being picked.
        return Chest(self.app, (0, 0), random.choices(itemIds, itemWeights, k = random.randint(1, 3)))

    def get_random_enemy(self):
        # Creates a random enemy.
        # This method works in the same way as self.get_random_object().
        if not self.possibleEnemies: return

        enemyIds = [i[0] for i in self.possibleEnemies]
        enemyWeights = [i[1] for i in self.possibleEnemies]
        enemyId = random.choices(enemyIds, enemyWeights)[0]
        return enemies.classes[enemyId](self.app, pygame.math.Vector2())

class LevelGeneratorRoom:
    # A class to temporarily store objects, boundaries and attach points
    # while a level is being generated.
    def __init__(self, app, objects, boundaries, attachPoints):
        self.app = app

        self.objects = objects
        self.boundaries = boundaries
        self.attachPoints = attachPoints

        self.position = pygame.math.Vector2()
        self.rotation = 0

    def flatten(self):
        # This method adjusts the positions of each object
        # and boundary using this room's position and rotation
        # values, before returning them.
        for obj in self.objects:
            obj.pos.rotate_ip(self.rotation)
            obj.pos += self.position
        for boundary in self.boundaries:
            boundary.pos.rotate_ip(self.rotation)
            boundary.pos += self.position
        return self.objects, self.boundaries

    def get_attach_points(self):
        # This method adjusts the position and rotation values
        # of each attach point using this room's position and
        # rotation values, before returning them.
        attachPoints = []
        for i in self.attachPoints:
            attachPoint = list(i)
            attachPoint[0] = self.position + attachPoint[0].rotate(self.rotation)
            attachPoint[1] += self.rotation
            attachPoints.append(attachPoint)
        return attachPoints

    def add_object(self, obj):
        # Adds an object to this room.
        self.objects.append(obj)