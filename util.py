import json

WIDTH, HEIGHT = 400, 300
FPS = 60
CAPTION = "<CATACOMB CRAWLER>"

BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
CYAN = 0, 255, 255
MAGENTA = 255, 0, 255
YELLOW = 255, 255, 0
WHITE = 255, 255, 255

# Grid size to use for collision check
# optimisations.
GRIDSIZE = 15

SAMPLERATE = 48000

def read_file(filename):
	with open(filename, encoding = "utf-8") as f:
		return f.read()

def write_file(filename, data):
	with open(filename, "w", encoding = "utf-8") as f:
		f.write(data)

def read_json(filename):
	with open(filename, encoding = "utf-8") as f:
		return json.load(f)

def write_json(filename, data):
	with open(filename, "w", encoding = "utf-8") as f:
		json.dump(data, f)
