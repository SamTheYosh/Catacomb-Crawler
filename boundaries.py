import random

from util import *
from circles import *

class BoundaryHandler(PositionGridUser):
    # Stores boundaries and manages boundary updating, drawing, collisions etc.
    def __init__(self, app, fillArguments):
        super().__init__(app)

        self.boundaries = []

        # These two surfaces are used to draw the boundaries to
        # the screen. The colourkey is white, meaning white areas
        # drawn to these surfaces will appear transparent when
        # blitted to the screen.
        self.lowerSurface = pygame.Surface((WIDTH, HEIGHT))
        self.lowerSurface.set_colorkey(WHITE)
        self.upperSurface = pygame.Surface((WIDTH, HEIGHT))
        self.upperSurface.set_colorkey(WHITE)

        # This code, alongside some code in self.draw_lower_layer(),
        # deals with drawing boundaries. Without this code I would have
        # to repeat a lot of self.draw_lower_layer() 3 times, with slight
        # changes for each draw.
        self.fillDestinations = [
            self.app.screen,
            self.lowerSurface,
            self.upperSurface
        ]
        # self.fillArguments is a list of colours/images to fill the different
        # layers of the boundaries with. Colours are defined as a tuple of three
        # integers, and images are specified using a string.
        self.fillArguments = []
        for i in fillArguments:
            if isinstance(i, str):
                self.fillArguments.append(pygame.image.load(f"sprites/{i}.png"))
            else:
                self.fillArguments.append(i)
    
    def add_boundary(self, boundary):
        # Adds a boundary to self.boundaries and updates
        # self.positionGrid to include this boundary.
        self.boundaries.append(boundary)
        self.update_position_grid(self.boundaries)
    
    def snap_inside_boundaries(self, obj):
        # Snap sthe given VerletObject inside of all of the
        # boundaries in self.boundaries.
        # First we find any boundaries that are nearby to the object.
        nearbyBoundaries = self.get_nearby(obj)
        
        # The VerletObject class's previousNearbyBoundaries attribute is used
        # if an object has just gone outside of all of the boundaries in self.boundaries,
        # which could happen if the object is going at a high speed.
        # In this case, we just look at the boundaries the object was near on the
        # last frame it was near some boundaries.
        # If the object was never near any boundaries to begin with, for example if
        # it was created outside of all boundaries (which shouldn't happen, but this
        # is for if it theoretically did), we find the closest boundary to the object
        # and use that instead.
        if nearbyBoundaries: obj.previousNearbyBoundaries = nearbyBoundaries
        else:
            if not obj.previousNearbyBoundaries:
                obj.previousNearbyBoundaries.append(sorted(
                    self.boundaries,
                    key = lambda x: x.pos.distance_to(obj.pos)
                )[0])
            nearbyBoundaries = obj.previousNearbyBoundaries

        # If the object is completely within any of its nearby boundaries, we do not
        # need to snap it back inside them so we can return from this method.
        # Also, if for some reason we still have an empty list of nearby boundaries, we return.
        if not nearbyBoundaries or obj.get_within_boundaries(nearbyBoundaries): return

        # Now we get all of the vectors that could move the object back inside of
        # each nearby boundary. Then we choose the shortest vector.
        snapVectors = []
        for boundary in nearbyBoundaries:
            snapVectors.append(boundary.get_snap_inside_vector(obj))
        snapVector = sorted(snapVectors, key = lambda x: x.magnitude_squared())[0]

        # Finally we move the object's position by this vector.
        # The vector is multiplied by 0.3 here to make the snap back into the boundaries
        # a bit "softer". Without this multiplication, we snap instantly back, which can
        # sometimes result in objects moving at high speeds if they get pushed against
        # a wall and suddenly get shot back out.
        obj.pos += snapVector * 0.3

    def circle_touching_boundaries(self, circle):
        # Returns whether the given circle is touching any of
        # its nearby boundaries.
        for boundary in self.get_nearby(circle):
            if boundary.get_colliding(circle): return True
        return False

    def circle_inside_boundaries(self, circle):
        # Returns whether the given circle is completely within
        # any of its nearby boundaries.
        for boundary in self.get_nearby(circle):
            if boundary.get_inside(circle): return True
        return False

    def get_bounding_box(self):
        # Calculates a bounding box for the level.
        # This box covers every boundary.
        # It is found by finding the maximum and minimum x and y values
        # of the boundaries in self.boundaries.
        top = min([i.pos.y - i.radius for i in self.boundaries])
        bottom = max([i.pos.y + i.radius for i in self.boundaries])
        left = min([i.pos.x - i.radius for i in self.boundaries])
        right = max([i.pos.x + i.radius for i in self.boundaries])

        return pygame.Rect(left, top, right - left, bottom - top)

    def draw_lower_layer(self):
        # Draws every layer of the boundaries.
        # This includes drawing the background layer to the screen.
        for i in range(len(self.fillDestinations)):
            fillDestination = self.fillDestinations[i]
            fillArgument = self.fillArguments[i]
            if isinstance(fillArgument, pygame.Surface):
                self.tile_image_across_surface(fillArgument, fillDestination)
            else:
                fillDestination.fill(fillArgument)

        for boundary in self.boundaries:
            boundary.draw_mask2(self.upperSurface)
            boundary.draw_mask1(self.lowerSurface, self.upperSurface)
        
        # Then blits the lower layer's surface to the screen.
        self.app.screen.blit(self.lowerSurface, (0, 0))

    def draw_upper_layer(self):
        # Blits the upper layer's surface to the screen.
        # Must be called after calling self.draw_lower_layer(), as that method
        # draws to the upper layer surface.
        self.app.screen.blit(self.upperSurface, (0, 0))

    def generate_nodes_and_edges(self):
        # Generates a list of nodes using the positions of each boundary
        # and connects these edges with nodes if their associated boundaries
        # are overlapping, meaning you would be able to move between them.
        nodes = []
        for boundary in self.boundaries:
            boundary.nodeIndex = len(nodes)
            nodes.append(boundary.pos)
        
        edges = []
        for boundary1 in self.boundaries:
            nearbyBoundaries = self.get_nearby(boundary1)
            for boundary2 in nearbyBoundaries:
                if boundary1 == boundary2 or not boundary1.get_colliding(boundary2): continue
                edges.append((self.boundaries.index(boundary1), self.boundaries.index(boundary2)))
        
        return nodes, edges
    
    def tile_image_across_surface(self, image, surface):
        # Repeats an image across a surface, offset by the
        # camera position.
        imageWidth, imageHeight = image.get_size()
        surfaceWidth, surfaceHeight = surface.get_size()
        origin = self.app.camera.adjust_pos((0, 0))
        origin.x %= imageWidth
        origin.y %= imageHeight
        origin.x = int(origin.x)
        origin.y = int(origin.y)
        
        for y in range(-1, surfaceHeight // imageHeight + 1):
            for x in range(-1, surfaceWidth // imageWidth + 1):
                surface.blit(image, origin + (x * imageWidth, y * imageHeight))

class Boundary(Circle):
    # Constrains objects within a circle.
    # Levels are made up of boundaries.
    def __init__(self, app, pos, radius, jaggedness=6):
        super().__init__(app, pos, radius)
        # self.drawPoints is a list of points that make up the
        # shape of this boundary on the screen. The points have
        # random offsets to make the boundaries look cave-like.
        self.drawPoints = self.generate_draw_points(jaggedness)

    def draw_mask1(self, surface1, surface2):
        # Uses self.drawPoints to draw the shape of this boundary
        # to the lower and upper surface of a BoundaryHandler.
        # It is drawn in white, which will appear transparent on the
        # surfaces they are drawn to (see BoundaryHandler for more details).
        points = []
        for point in self.drawPoints:
            points.append(point + self.app.camera.adjust_pos(self.pos))
        
        pygame.draw.polygon(surface1, WHITE, points)
        pygame.draw.polygon(surface2, WHITE, points)

    def draw_mask2(self, surface):
        # Similar to draw_mask1, but offset and scaled slightly
        # to give a pseudo-3D effect to the boundaries.
        points = []
        for point in self.drawPoints:
            magnitude = point.magnitude()
            if magnitude == 0: points.append(point)
            else: points.append(point / magnitude * (magnitude + 5))
        for point in points:
            point += self.app.camera.adjust_pos(self.pos) + (0, -10)
        
        pygame.draw.polygon(surface, WHITE, points)

    def generate_draw_points(self, jaggedness):
        # Generates points along the circumference of this
        # boundary, adding a random offset to make the boundary
        # appear more natural and cave-like.
        points = []
        numberOfPoints = math.ceil(self.radius / 3)

        angle = random.uniform(0, 360)
        radiusVector = pygame.math.Vector2(self.radius + 2, 0)
        for _ in range(1, numberOfPoints + 1):
            point = pygame.math.Vector2(-8 - random.uniform(0, jaggedness))
            point += radiusVector
            point = point.rotate(angle)
            points.append(point)
            angle += 360 / numberOfPoints
        
        return points

    def get_snap_inside_vector(self, circle):
        # Calculates a vector to snap a given circle back inside this
        # boundary.
        displacement = circle.pos - self.pos
        distance = displacement.magnitude()
        if distance == 0: return pygame.math.Vector2()

        snapInsideVectorMagnitude = (self.radius - circle.radius - distance)
        if snapInsideVectorMagnitude >= 0: return pygame.math.Vector2()

        normalisedDisplacement = displacement.normalize()
        return normalisedDisplacement * snapInsideVectorMagnitude