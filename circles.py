import pygame, math

from util import *

class Circle:
    def __init__(self, app, pos, radius):
        self.app = app

        self.pos = pygame.math.Vector2(pos)
        self.radius = radius
        # self.overlappingGridSpaces is a list of grid spaces that
        # this circle is overlapping with. Its use is explained in
        # the PositionGridUser class.
        self.overlappingGridSpaces = []

    def get_overlap_vector(self, circle):
        # This method calculates the overlap vector between two circles.
        displacement = circle.pos - self.pos
        if displacement.magnitude_squared() == 0:
            return pygame.math.Vector2()
        direction = displacement.normalize()
        return direction * (circle.radius + self.radius) - displacement

    def get_colliding(self, circle):
        # Returns whether a circle is touching another circle.
        return (circle.pos - self.pos).magnitude() < (self.radius + circle.radius)

    def get_inside(self, circle):
        # Returns whether a circle is fully inside another circle.
        return (circle.pos - self.pos).magnitude() < (self.radius - circle.radius)

    def find_overlapping_grid_spaces(self):
        # Using the bounding box of this circle, calculates which
        # grid spaces this circle is within. Used in PositionGridUser.
        gridspaces = []
        for y in range(math.floor((self.pos.y - self.radius) / GRIDSIZE), math.ceil((self.pos.y + self.radius) / GRIDSIZE) + 1):
            for x in range(math.floor((self.pos.x - self.radius) / GRIDSIZE), math.ceil((self.pos.x + self.radius) / GRIDSIZE) + 1):
                gridspaces.append((x, y))
        self.overlappingGridSpaces = gridspaces
        return gridspaces

class PositionGridUser:
    def __init__(self, app):
        self.app = app
        # self.positionGrid is a dictionary. Its keys are grid coordinates,
        # and its values are lists of objects that lie within the grid coordinates.
        # This is used as part of an optimisation technique called spatial partitioning,
        # where you only check collisions with nearby objects. This massively cuts down
        # on collision checks, hugely helping performance.
        self.positionGrid = {}

    def update_position_grid(self, circles):
        # Populates self.positionGrid with the provided circles.
        self.positionGrid = {}
        for circle in circles:
            for gridspace in circle.find_overlapping_grid_spaces():
                if not gridspace in self.positionGrid:
                    self.positionGrid[gridspace] = []
                self.positionGrid[gridspace].append(circle)

    def iterate_pairs(self):
        # Creates a generator using the yield keyword, that iterates
        # over each pair of circles that share a grid space.
        # yieldedPairs keeps track of which pairs have already been yielded
        # to prevent duplicates.
        yieldedPairs = []
        for i in self.positionGrid.values():
            for a in range(len(i)):
                for b in range(a+1, len(i)):
                    circle1 = i[a]
                    circle2 = i[b]
                    # Checking for duplicates.
                    if (circle1, circle2) in yieldedPairs or (circle2, circle1) in yieldedPairs: continue
                    yieldedPairs.append((circle1, circle2))
                    yield circle1, circle2

    def get_nearby(self, circle):
        # Gets a list of circles that share a grid space with
        # the given circle.
        nearby = []
        for gridspace in circle.find_overlapping_grid_spaces():
            if not gridspace in self.positionGrid: continue
            for i in self.positionGrid[gridspace]:
                if i != circle and not i in nearby:
                    nearby.append(i)
        return nearby