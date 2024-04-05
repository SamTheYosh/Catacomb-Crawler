# This is a simple program to allow me to view the layout of
# preset rooms defined in presetrooms.json. It helps with
# designing these preset rooms - you can see the boundaries,
# enemies, objects, chests and attach points. If you have made
# a mistake and put something in the wrong position, you can
# instantly tell.

import pygame, os

from util import *
from events import *

WIDTH, HEIGHT = 800, 800

class Viewer:
    def __init__(self, app):
        self.app = app
        
        self.origin = pygame.math.Vector2(30, HEIGHT / 2)

        self.filename = "jsondata//presetrooms.json"
        self.fileLastModifiedTime = 0

        self.load()
    
    def draw(self):
        try:
            for i in self.rooms:
                pygame.draw.circle(self.app.screen, (100, 100, 100), self.origin + i[0], i[1])
            pygame.draw.line(self.app.screen, WHITE, (0, self.origin.y), (WIDTH, self.origin.y))
            pygame.draw.line(self.app.screen, WHITE, (self.origin.x, 0), (self.origin.x, HEIGHT))
            for i in self.objects:
                pygame.draw.circle(self.app.screen, i[1], self.origin + i[0], 5)
            for i in self.attachPoints:
                pygame.draw.circle(self.app.screen, MAGENTA, self.origin + i[0], 5)
                pygame.draw.line(
                    self.app.screen,
                    MAGENTA,
                    self.origin + i[0],
                    self.origin + i[0] + pygame.math.Vector2(10, 0).rotate(i[1]),
                    3
                )
        except: pass
    
    def set_room_index(self, index):
        try:
            self.roomIndex = index % len(self.presetRooms)
            self.roomData = self.presetRooms[self.roomIndex]

            self.rooms = []
            self.objects = []
            self.attachPoints = []
            
            for i in self.roomData["boundaries"]:
                self.rooms.append((i["pos"], i["radius"]))
            for i in self.roomData["chests"]:
                self.objects.append((i["pos"], BLUE))
            for i in self.roomData["enemies"]:
                self.objects.append((i["pos"], RED))
            for i in self.roomData["objects"]:
                self.objects.append((i["pos"], GREEN))
            for i in self.roomData["attachPoints"]:
                self.attachPoints.append(i)
        except: pass
    
    def update(self):
        self.check_file()
        indexChange = (
            self.app.eventHandler.get_key_just_pressed(pygame.K_d) -
            self.app.eventHandler.get_key_just_pressed(pygame.K_a)
        )
        if indexChange != 0:
            self.set_room_index(self.roomIndex + indexChange)
    
    def load(self):
        try: self.presetRooms = read_json(self.filename)
        except:
            print("Invalid JSON")
            return
        try: self.set_room_index(self.roomIndex)
        except: self.set_room_index(-1)
    
    def check_file(self):
        fileModifiedTime = os.stat(self.filename).st_mtime
        if fileModifiedTime != self.fileLastModifiedTime:
            self.fileLastModifiedTime = fileModifiedTime
            self.load()

class App:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.eventHandler = EventHandler(self)

        self.viewer = Viewer(self)

    def run(self):
        self.running = True
        while self.running:
            self.update_time()
            self.update()
            self.draw()
        self.quit()

    def update_time(self):
        self.time = pygame.time.get_ticks() / 1000
        self.dt = self.clock.tick(FPS)
        pygame.display.set_caption(CAPTION + "   FPS: {0:.2f}".format(self.clock.get_fps()))

    def update(self):
        self.eventHandler.handle_events()

        self.viewer.update()

    def draw(self):
        self.screen.fill(BLACK)

        self.viewer.draw()

        pygame.display.flip()

    def stop(self):
        self.running = False

    def quit(self):
        pygame.quit()

app = App()
app.run()