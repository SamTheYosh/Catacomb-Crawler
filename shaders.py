import pygame, moderngl, glcontext
from array import array

from util import *

class ShaderDisplay:
    # This class creates a new OpenGL context, displayed
    # through a pygame window.
    def __init__(
            self, 
            app, 
            displaySize,
            surfaceSize,
            vertFilename,
            fragFilename
    ):
        self.app = app

        # Sets up the pygame window.
        pygame.init()
        # This is the size of the window.
        self.displaySize = displaySize
        # This is the size of the window surface, can be smaller
        # than the window and it will be scaled to fit the window.
        self.surfaceSize = surfaceSize
        # The pygame.OPENGL and pygame.DOUBLEBUF flags set up the
        # pygame window to work with OpenGL.
        pygame.display.set_mode(self.displaySize, pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption(CAPTION)

        # This creates an transparent icon to use
        # for this window, overriding the default
        # pygame logo. This code may be changed if
        # I decide to design a proper icon.
        icon = pygame.Surface((32, 32))
        icon.fill(BLACK)
        icon.set_colorkey(BLACK)
        pygame.display.set_icon(icon)

        # This is the surface that everything will be
        # drawn to before being passed to the GPU to be
        # drawn using shaders.
        self.surface = pygame.Surface(self.surfaceSize)

        # Here we set up various aspects of the OpenGL system
        # we will use.
        self.ctx = moderngl.create_context()
        # This is a rectangle that covers the whole window.
        # In OpenGL, we cannot just draw pixels, we have to
        # have some geometry to render a texture to. This
        # rectangle will have self.surface rendered to it.
        self.vbo = self.ctx.buffer(data = array("f", [
            -1.0, 1.0, 0.0, 0.0,
            1.0, 1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0, 1.0,
            1.0, -1.0, 1.0, 1.0
        ]))
        # This is an object containing the vertex and
        # fragment shaders used for rendering.
        self.program = self.ctx.program(
            vertex_shader = read_file(vertFilename),
            fragment_shader = read_file(fragFilename)
        )
        # This is an object that is used to actually draw
        # everything. The complex-looking tuple inside a list
        # defines the format of some of the data being passed
        # to the GPU. You can see the actual data above when
        # we created self.vbo - we pass 2 floats as the
        # coordinates of the rectangle's vertices, and 2 floats
        # as the texture coordinates these vertices should use,
        # then repeat until the whole rectangle is defined.
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, "2f 2f", "vert", "texcoord")]
        )

        # This is a list to keep track of any uniform variables
        # that either don't exist or have been optimised out of
        # the shader programs. We only want to warn the user about
        # these variables once, so we keep track of any that we
        # have already warned about.
        self.warnedUniforms = []

        # This variable is used to toggle the CRT effect.
        # If it is False, we bypass all of the code that causes
        # the effect.
        self.toggleEffect = True

    def update(self):
        # Here we pass the time since the program started in milliseconds
        # to the shader. This is used for generating random noise over
        # the screen that varies over time.
        self.set_uniform("time", self.app.time * 1000)
        
        # Toggle the CRT effect if tab is pressed, and send the value
        # of self.toggleEffect to the shader.
        if self.app.eventHandler.get_key_just_pressed(pygame.K_TAB):
            self.toggleEffect = not self.toggleEffect
        self.set_uniform("toggle", self.toggleEffect)

    def draw(self):
        # Send self.surface to the shader to use for
        # rendering, and make the render call.
        tex = self.surface_to_texture(self.surface)
        tex.use(0)
        self.vao.render(mode = moderngl.TRIANGLE_STRIP)
        # The pygame window uses a double buffer system -
        # one buffer isn't visible and the other is displayed
        # in the window. We draw to the buffer that isn't visible,
        # then when the drawing is finished we switch the two
        # buffers so we see what we have drawn (also known as
        # flipping the buffers).
        pygame.display.flip()
        # We created an OpenGL texture in self.surface_to_texture(),
        # so we need to release it otherwise a memory leak will occur
        # as we continue to allocate more and more memory to store
        # textures.
        tex.release()

    def surface_to_texture(self, surface):
        # First create a new OpenGL texture, with the same
        # dimensions as the pygame.Surface.
        tex = self.ctx.texture(surface.get_size(), 4)
        # Then we set some attributes that control how
        # the texture is sampled by OpenGL.
        tex.filter = moderngl.LINEAR, moderngl.LINEAR
        tex.repeat_x = False
        tex.repeat_y = False
        tex.swizzle = "BGRA"
        # Then we copy across the image data from the pygame.Surface
        # into the texture.
        tex.write(surface.get_view("1"))
        return tex

    def set_uniform(self, name, value):
        # We try to pass a value to the shader through the use
        # of uniforms. If the uniform doesn't exist, we catch the
        # resulting error and warn the user. This can happen
        # if the OpenGL compiler optimises out a uniform if it
        # isn't used within the program.
        try:
            self.program[name] = value
        except KeyError:
            if not name in self.warnedUniforms:
                print(f"Uniform {name} does not exist. It may have been optimised out.")
                self.warnedUniforms.append(name)

    def access_screen(self):
        # Returns a reference to self.surface.
        return self.surface

    def destroy(self):
        # Releases all of the OpenGL objects
        # we created, as they are not automatically
        # cleaned up by Python's garbage collection
        # system.
        self.vao.release()
        self.vbo.release()
        self.program.release()
        self.ctx.release()