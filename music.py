import random, soundfile, os

from util import *

class RandomMusicHandler:
    # Manages RandomMusicChannels.
    def __init__(self, soundPlayer, folder, channelNames):
        self.soundPlayer = soundPlayer
        self.folder = folder
        # We need to play sounds using a sound group
        # to allow us to manually stop them.
        self.soundGroup = self.soundPlayer.alwaysAllowGroup + "music"

        # Here we create RandomMusicChannels for each channel
        # in channelNames.
        self.channels = []
        for name in channelNames:
            self.channels.append(RandomMusicChannel(
                self.soundPlayer,
                self.folder,
                name,
                self.soundGroup
            ))
        
        # Here we attempt to start a looping background sound.
        # It will always have the filename bg.ogg.
        # The error catching is for if the file doesn't exist -
        # in that case we just don't play any background audio.
        try:
            self.soundPlayer.play_sound(
                "..//music//" + self.folder + "//bg.ogg",
                loop = True,
                group = self.soundGroup,
                priority = 5
            )
        except soundfile.LibsndfileError: pass

    def update(self):
        # Updates every channel.
        for channel in self.channels:
            channel.update()

    def stop(self):
        # Stops every channel and stops the background audio.
        for channel in self.channels:
            channel.stop()
        self.soundPlayer.stop_group(self.soundGroup)

class RandomMusicChannel:
    # Plays music snippets randomly.
    def __init__(self, soundPlayer, path, name, soundGroup):
        self.soundPlayer = soundPlayer

        self.path = path + "//" + name + "//"
        # We need to use a unique sound group to allow this class
        # to check if a sound it started is still playing.
        self.soundGroup = soundGroup + "_" + name

        self.sounds = self.get_soundfiles()
        self.nextSound = None
        self.waitTimer = 0

        # We need to call self.new_sound() here to start the
        # wait timer and pick a sound to play when that timer
        # reaches 0.
        self.new_sound()

    def update(self):
        # If there aren't any sounds in the folder for this channel,
        # we don't attempt to play one.
        if not self.sounds: return
        
        # If the previous sound we played is still playing, don't
        # attempt to play another one as it would overlap.
        if self.soundPlayer.check_sound_exists(self.soundGroup): return
        
        self.waitTimer -= 1
        # If we have waited long enough, we can play the sound chosen
        # by self.new_sound().
        if self.waitTimer <= 0:
            self.soundPlayer.play_sound(
                "..//music//" + self.path + self.nextSound,
                group = self.soundGroup,
                pan = random.uniform(-0.75, 0.75),
                priority = 5
            )
            # We then choose another sound to play.
            self.new_sound()

    def new_sound(self):
        # This method sets the wait timer and picks
        # a sound to play when the timer reaches 0.
        if not self.sounds: return
        # Here we pick a random sound until it is either
        # different to the previous sound played (to prevent
        # the same sound from playing twice in a row) or the
        # length of the list of sounds is 1 (in which case we
        # can't avoid playing the same sound twice in a row).
        while True:
            choice = random.choice(self.sounds)
            if len(self.sounds) == 1 or self.nextSound != choice:
                break
        self.nextSound = choice
        self.waitTimer = random.randint(0, 1000)

    def stop(self):
        # Stops any sounds currently being played by this channel.
        self.soundPlayer.stop_group(self.soundGroup)
    
    def get_soundfiles(self):
        # Looks in this channel's folder, finds all of the
        # sounds and adds their filenames to a list.
        sounds = []
        filesAndFolders = os.listdir("music//" + self.path)
        for i in filesAndFolders:
            # Only adds .ogg files to the list.
            if i[-4:] == ".ogg":
                sounds.append(i)
        return sounds