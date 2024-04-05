import pygame, math, random

from util import *

class PerlinNoise:
    # Provides a simple interface for the Perlin noise algorithm.
    def __init__(self, app, wrap = 256):
        self.app = app
        self.wrap = wrap
        self.permutation = self.make_permutation()
        self.vector = pygame.math.Vector2(1, 0)

    def noise(self, x, y, f):
        # First we scale the given coordinates by the f argument.
        # This is used to set the scale of the noise.
        x *= f
        y *= f
        # X and Y are the integer components of the coordinates.
        X = math.floor(x)
        Y = math.floor(y)
        # xf and yf are the decimal components of the coordinates.
        xf = x - X
        yf = y - Y

        # Perlin noise works by generating pseudo-random vectors at each
        # grid point which are used to calculate the final noise value.
        # Here, we generate grid coordinates for each corner of the grid
        # space we are in.
        topRight = pygame.math.Vector2(xf - 1, yf - 1)
        topLeft = pygame.math.Vector2(xf, yf - 1)
        bottomRight = pygame.math.Vector2(xf - 1, yf)
        bottomLeft = pygame.math.Vector2(xf, yf)

        # In this code we end up with a value between -1 and 1 for each corner.
        dotTopRight = topRight.dot(self.get_constant_vector(X + 1, Y + 1))
        dotTopLeft = topLeft.dot(self.get_constant_vector(X, Y + 1))
        dotBottomRight = bottomRight.dot(self.get_constant_vector(X + 1, Y))
        dotBottomLeft = bottomLeft.dot(self.get_constant_vector(X, Y))

        # Then we smoothly blend between the corner values and return the final
        # noise value.
        u = self.fade(xf)
        v = self.fade(yf)

        return self.lerp(u, self.lerp(v, dotBottomLeft, dotTopLeft), self.lerp(v, dotBottomRight, dotTopRight))

    def make_permutation(self):
        # This method generates a list of the numbers from 0 to 255, and shuffles it.
        # It is used to generate pseudo-random numbers, where the same input always gives the
        # same pseudo-random output.
        return random.choices(range(0, self.wrap), k = self.wrap)

    def get_permutation_value(self, v):
        # This method gets a value from 0 to 255 from the list of shuffled values
        # from 0 to 255.
        return self.permutation[v % self.wrap]

    def get_constant_vector(self, X, Y):
        # For a given input, this method will always return the same vector with length
        # 1 and pseudo-random rotation.
        randomValue = self.get_permutation_value(self.get_permutation_value(X) + Y)
        return self.vector.rotate(randomValue / (self.wrap - 1) * 360)

    def fade(self, t):
        # This method allows for non-linear interpolation. It essentially smooths out
        # the generated noise. Looks more natural and rounded than linear interpolation.
        return ((6 * t - 15) * t + 10) * t * t * t

    def lerp(self, t, a1, a2):
        # Linear interpolation, allows us to interpolate
        # between calculated values.
        return a1 + t * (a2 - a1)