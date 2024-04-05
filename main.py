import pygame

from util import *
from shaders import *
from events import *
from ui import *
from sound import *
from astar import *
from jsondata import *
from sprites import *
from perlin import *
from player import *
from camera import *
from levelgen import *
from boundaries import *
from animation import *
from states_definition import *

class App:
    # The main class of this project. Most other classes
    # store a reference to this class to make use of its
    # many attributes.
    def __init__(self):
        self.shaderDisplay = ShaderDisplay(
            self,
            (WIDTH*2, HEIGHT*2),
            (WIDTH, HEIGHT),
            "shaders/crt.vert",
            "shaders/crt.frag"
        )
        self.screen = self.shaderDisplay.access_screen()
        self.eventHandler = EventHandler(self)
        self.fontLibrary = FontLibrary(self)
        self.display_loading_screen()
        self.soundPlayer = SoundPlayer(self, [DelayEffect(0.1, 0.5, 0.6)])
        self.aStarPathfinder = AStarPathfinder(self)
        self.clock = pygame.time.Clock()
        self.update_time()
        self.jsonDataManager = JSONDataManager(self)
        self.spritesheetManager = SpritesheetManager(self)
        self.perlinNoise = PerlinNoise(self)
        self.titleScreen = TitleScreen(self)
        self.simpleUI = SimpleUI(self)
        self.resultsScreen = ResultsScreen(self)
        self.gameOverScreen = GameOverScreen(self)
        self.vignette = Vignette(self)
        self.randomMusicHandler = RandomMusicHandler(self.soundPlayer, "", [])
        self.particleEffectsManager = ParticleEffectsManager(self)

        self.gameState = 0

        self.set_game_state(0)
        #self.setup_game()

    def run(self):
        # This is the main game loop.
        # It runs until self.stop() is called.
        self.running = True
        while self.running:
            self.update_time()
            self.update()
            self.draw()
        self.quit()

    def setup_game(self):
        # Here we create the player, camera and level generator
        # that will be used during gameplay. This method is called
        # when gameplay starts.
        self.player = Player(self)
        self.camera = Camera(self, target = self.player)
        self.levelGenerator = LevelGenerator(self)
        self.next_level()
        self.set_game_state(1)
        #self.player.inventory.add_item(self.jsonDataManager.create_item(4))

    def update_time(self):
        # Updates the time value. pygame.time.get_ticks() returns a millisecond
        # value, so I divide it by 1000 to get seconds.
        self.time = pygame.time.get_ticks() / 1000
        # The main point of this method is the self.clock.tick(FPS).
        # This tries to maintain a constant FPS, based on how long the
        # previous frame took to execute.
        self.dt = self.clock.tick(FPS)
        # Displaying the FPS in the window's caption.
        pygame.display.set_caption(CAPTION + "   FPS: {0:.2f}".format(self.clock.get_fps()))

    def update(self):
        # All of the game's logic happens here.
        self.eventHandler.handle_events()
        match self.gameState:
            case 0: # title screen
                self.titleScreen.update()
            case 1: # gameplay
                self.randomMusicHandler.update()
                self.levelContainer.update()
                self.camera.update()
                self.simpleUI.update()
            case 2: # results screen
                self.resultsScreen.update()
            case 3: # game over
                self.gameOverScreen.update()
        self.shaderDisplay.update()
        self.soundPlayer.allowNewSounds = True

    def draw(self):
        # The screen is drawn to here.
        self.screen.fill(BLACK)
        match self.gameState:
            case 0: # title screen
                self.titleScreen.draw()
            case 1: # gameplay
                self.levelContainer.draw()
                self.vignette.draw()
                self.simpleUI.draw()
            case 2: # results screen
                self.resultsScreen.draw()
            case 3: # game over
                self.gameOverScreen.draw()
        self.shaderDisplay.draw()

    def stop(self):
        # Stops the main loop.
        self.running = False

    def quit(self):
        # Shuts down and cleans up anything that needs to.
        # The program ends after this method is called.
        pygame.quit()
        self.soundPlayer.quit()
        self.shaderDisplay.destroy()

    def next_level(self):
        # This method moves the player to the next level when called.
        # First we play the "next level" sound effect.
        self.soundPlayer.play_sound(
            "boom.ogg",
            pitch = 0.75,
            group = self.soundPlayer.alwaysAllowGroup
        )
        # Then we generate a new level.
        self.levelContainer = self.levelGenerator.next_level()
        # Then we move the player to be back at the start of the level.
        self.player.pos.update(self.levelContainer.boundaryHandler.boundaries[0].pos)
        self.player.previousPos.update(self.player.pos)
        self.player.rotation = 90
        # Then we add the player object to the level.
        self.levelContainer.objectHandler.add_object(self.player)
        # We unset this variable to tell the player object that it
        # needs to add its EquippedObject to the level.
        self.player.addedEquippedObjectToLevel = False
        # The camera's position will still be somewhere else in the
        # level. We need to snap it back to the player's position.
        self.camera.pos.update(self.player.pos)
        

    def set_game_state(self, state):
        # Updates the game state and calls any methods that need
        # to be called when each state is entered.
        self.gameState = state
        match self.gameState:
            case 0: # title screen
                self.titleScreen.start()
            case 1: # gameplay
                self.simpleUI.start()
            case 2: # results screen
                self.resultsScreen.start()
            case 3: # game over
                self.gameOverScreen.start()
    
    def display_loading_screen(self):
        # Draws a loading screen to the window.
        self.fontLibrary.draw_text(
            self.screen,
            "Loading...",
            "uncial",
            (WIDTH/2, HEIGHT/2),
            align = (0.5, 0.5)
        )
        self.shaderDisplay.draw()

# Here we instanciate the App class and call its run() method,
# causing the game to start.
app = App()
app.run()