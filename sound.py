import pyaudio, soundfile, math, random, _thread, glob
import numpy as np

from util import *

class SoundPlayer:
    # A class that uses the pyaudio library for sound playback.
    def __init__(self, app, effects = None):
        self.app = app

        # pyaudio works by calling a callback function each
        # time the audio stream wants some more audio data.
        # This happens asynchronously. The callback function
        # accesses some of this class's attributes which are
        # also accessed within this class's other methods,
        # meaning they could end up attempting to access them
        # at the same time (this can cause issues).
        # To prevent this we use a lock. Only one thread, either
        # the main one or the one used by the callback function,
        # can use the lock at a time.
        self.lock = _thread.allocate_lock()

        # self.soundLibrary is used to create new SoundInstances.
        self.soundLibrary = SoundLibrary(self.app)
        # This is a list of all of the SoundInstances currently
        # playing.
        self.currentSounds = []

        # This is a dictionary of sound presets, so we can play
        # sounds using arguments defined outside of the program.
        self.soundPresets = read_json("jsondata//sounds.json")

        # This is a list of effects to be applied to the
        # audio output.
        self.effects = []
        if not effects is None: self.effects += effects

        # If this is False, do not allow new sounds to be
        # played.
        self.allowNewSounds = True
        self.alwaysAllowGroup = "alwaysAllow"

        # First we need to initialise pyaudio and open
        # an audio stream to send audio data to.
        self.pyaudio = pyaudio.PyAudio()
        self.stream = self.open_stream()
    
    def open_stream(self):
        # Here we attempt to open a new audio stream.
        # It may fail, if for example the device we
        # are using doesn't have any sound hardware or
        # another program is hogging the audio output.
        # We can catch this error, so if we can't open
        # the audio stream we handle it gracefully and
        # the user can't tell.
        try:
            return self.pyaudio.open(
                format = pyaudio.paFloat32,
                channels = 2,
                rate = SAMPLERATE,
                output = True,
                stream_callback = self.callback
            )
        except OSError:
            return

    def quit(self):
        # Closes the audio stream and stops pyaudio.
        if self.stream != None: self.stream.close()
        self.pyaudio.terminate()

    def mix(self, data, toMix):
        # Mixes two arrays of audio data together.
        # Essentially just adds them together and clips
        # them (ensures their values do not exceed -1 or 1).
        data += np.clip(toMix, -1 - data, 1 - data)

    def callback(self, inData, frameCount, timeInfo, status):
        # This method is called every time the audio stream wants more
        # audio data.
        # We create an empty array to store this audio data in, with the
        # length specified by the audio stream.
        # If we don't send an array of the specified length, the audio
        # stream will close.
        data = np.zeros((frameCount, 2), dtype = "float32")
        with self.lock:
            # To improve performance, we limit the number of sounds that
            # can be playing at once. Some sounds have higher priority than
            # others.
            self.currentSounds = sorted(self.currentSounds, key = lambda x: x.priority, reverse = True)[:10]
            # We get sound data from each sound in self.currentSounds.
            for sound in list(self.currentSounds):
                self.mix(data, sound.get_frames(frameCount))
            # Then we apply each effect in self.effects to the audio output.
            for effect in self.effects: effect.apply(self, data, frameCount)
        self.check_sounds()
        # Then we return the audio data, alongside a pyaudio status code. We need
        # to keep sending the paContinue code to keep the audio stream open.
        return data, pyaudio.paContinue

    def play_sound(
            self,
            filename,
            volume = 1,
            pitch = 1,
            pan = 0,
            group = None,
            loop = False,
            priority = 1
    ):
        # Uses self.soundLibrary to create a new SoundInstance
        # with the given arguments. Then adds this SoundInstance
        # to self.currentSounds.
        if not self.allowNewSounds and (group == None or group[:len(self.alwaysAllowGroup)] != self.alwaysAllowGroup): return
        with self.lock:
            self.currentSounds.append(
                self.soundLibrary.generate_sound(
                    filename,
                    volume,
                    pitch,
                    pan,
                    group,
                    loop,
                    priority
                )
            )

    def play_positional_sound(
            self,
            filename,
            pos,
            volume = 1,
            pitch = 1,
            group = None,
            loop = False,
            priority = 1
    ):
        # Similar to self.play_sound(), just creates a
        # PositionalSoundInstance instead.
        if not self.allowNewSounds and (group == None or group[:len(self.alwaysAllowGroup)] != self.alwaysAllowGroup): return
        with self.lock:
            self.currentSounds.append(
                self.soundLibrary.generate_positional_sound(
                    filename,
                    pos,
                    volume,
                    pitch,
                    group,
                    loop,
                    priority
                )
            )
    
    def play_preset_sound(self, preset, **kwargs):
        # Calls self.play_sound() using arguments from
        # one of the sound presets in sounds.json.
        # We can pass in extra keyword arguments to override
        # ones in the original preset.
        presetData = dict(self.soundPresets[preset])
        for i in kwargs:
            presetData[i] = kwargs[i]
        self.play_sound(
            **self.process_sound_arguments(presetData)
        )
    
    def play_preset_positional_sound(self, preset, pos, **kwargs):
        # Similar to self.play_preset_sound(), just with
        # self.play_positional_sound().
        presetData = dict(self.soundPresets[preset])
        for i in kwargs:
            presetData[i] = kwargs[i]
        self.play_positional_sound(
            **self.process_sound_arguments(presetData),
            pos = pos
        )
    
    def process_sound_arguments(self, args):
        # In sounds.json, we can give sound arguments in special
        # formats to allow for additional functionality.
        args = dict(args)
        for i in args:
            if isinstance(args[i], (tuple, list)):
                if isinstance(args[i][0], int):
                    # We can provide a list of 2 integers, this
                    # will be replaced by a random integer between the
                    # two values.
                    args[i] = random.randint(*args[i])
                else:
                    # We can also provide a list of 2 floats, which
                    # will be replaced by a random float between the
                    # two values.
                    args[i] = random.uniform(*args[i])
        # We can provide a randomFilename argument. Any "@" characters in the
        # filename argument will be replaced by the value in randomFilename.
        # Providing a list of 2 integers will result in a random integer being
        # picked (this happens in the above code). We can use this to easily
        # pick a random sound from a list of sounds.
        if "randomFilename" in args:
            args["filename"] = args["filename"].replace("@", str(args["randomFilename"]))
            del args["randomFilename"]
        return args

    def stop_group(self, group):
        # Stops any sounds that belong to the given group.
        with self.lock:
            for sound in self.currentSounds:
                if sound.group == group:
                    sound.remove()

    def check_sounds(self):
        # Removes any sounds from self.currentSounds that
        # have finished playing.
        with self.lock:
            for sound in list(self.currentSounds):
                if sound.finished():
                    self.currentSounds.remove(sound)

    def set_group_values(self, group, volume = None, pitch = None, pan = None):
        # Sets the given attributes for any sound belonging to the given group.
        with self.lock:
            for sound in self.currentSounds:
                if sound.group == group:
                    if volume != None:
                        sound.volume = volume
                    if pitch != None:
                        sound.pitch = pitch
                    if pan != None:
                        sound.pan = pan
    
    def check_sound_exists(self, group):
        # Returns whether there are any sounds in the given group.
        with self.lock:
            for sound in self.currentSounds:
                if sound.group == group:
                    return True
        return False
    
    def stop_all(self):
        # Stops all currently playing sounds.
        for sound in self.currentSounds:
            sound.remove()
        self.allowNewSounds = False

class SoundData:
    # Stores sound data and provides a method for sampling
    # this data.
    def __init__(self, app, filename):
        self.app = app
        # Here we read the sound file and store its data.
        self.data, self.samplerate = soundfile.read(
            "sounds//" + filename,
            dtype = "float32",
            always_2d = True
        )
        self.length = len(self.data)

    def get_frames(
            self,
            startIndex,
            n,
            startVolume = 1,
            endVolume = 1,
            startPitch = 1,
            endPitch = 1,
            pan = 0,
            loop = False
    ):
        # This method returns the required number of frames from this
        # class's sound data, starting at the given index.

        # This method allows for the sound's pitch to be varied. We can provide
        # a pitch value for the start of the sound snippet we return, and a value
        # for the end. We smoothly transition between these pitches.
        # We multiply the pitch values by self.samplerate / SAMPLERATE to ensure that
        # sounds play at the same pitch regardless of their samplerate.
        startPitch *= self.samplerate / SAMPLERATE
        endPitch *= self.samplerate / SAMPLERATE
        pitch = np.linspace(startPitch, endPitch, n)

        # This code generates an array of indices to use when sampling
        # the audio data. It is generated using the pitch values calculated
        # earlier. If we are at a higher pitch, we want to sample the audio
        # more often / at a higher frequency.
        # We also wrap back around to the start of the sound if we go past
        # the end and the sound should be looped.
        indices = np.zeros(n)
        index = 0
        for i in range(n):
            indices[i] = startIndex + index
            if loop: indices[i] %= self.length
            index += pitch[i]
        indices = indices[indices < self.length - 1]

        # I am using linear interpolation when sampling the audio.
        # It is difficult to explain how this works in terms of arrays,
        # so I will try with a single element of each array.
        # The "floor index" could be 4, and the "ceiling index" could be 5.
        # The "interpolation" value could be 0.5.
        # The value in self.data[4] could be 10, and the value in
        # self.data[5] could be 20.
        # We interpolate between these two values using the interpolation
        # value (0.5) and get 15 (halfway between 10 and 20).
        # This process is repeated for each element in all of the lists.
        floorIndices = np.floor(indices).astype("int32")
        ceilIndices = np.ceil(indices).astype("int32")
        interpolation = self.mono_to_stereo(indices - floorIndices)

        floorData = self.data[floorIndices]
        ceilData = self.data[ceilIndices]
        frames = (ceilData - floorData) * interpolation + floorData

        # Similarly to the pitch, we can define a start and end volume
        # that will be smoothly transitioned between. We then multiply
        # the interpolated audio data from before by these volume values.
        startVolume = max(0, startVolume)
        endVolume = max(0, endVolume)
        frames *= self.mono_to_stereo(np.linspace(startVolume, endVolume, len(frames)))

        # Then we pan the audio data by the given pan factor.
        frames = self.pan_frames(frames, pan)

        # The pyaudio audio stream will close if we don't provide
        # enough frames, so we need to pad the data if we have
        # reached the end of the sound and haven't reached the
        # required length.
        while len(frames) < n:
            frames = np.append(frames, [[0, 0]], axis = 0)
        
        # Finally we return the audio data along with the index
        # at the end of the audio data. This is so we can update the
        # index attribute in the SoundInstance that is calling this
        # method.
        return frames, startIndex + index

    def mono_to_stereo(self, array):
        # Converts a 1D array to a 2D array (mono to stereo audio data).
        return np.repeat(array[:, np.newaxis], 2, axis = 1)

    def pan_frames(self, frames, factor):
        # Pans given audio data to the left or right
        # depending on the pan factor (left = -1, right = 1).
        panned = np.copy(frames)
        if factor > 0:
            panned[:, 1] += frames[:, 0] * factor
            panned[:, 0] *= 1-factor
        elif factor < 0:
            factor *= -1
            panned[:, 0] += frames[:, 1] * factor
            panned[:, 1] *= 1-factor
        return panned

class SoundLibrary:
    # Stores SoundData and creates SoundInstances.
    def __init__(self, app):
        self.app = app
        self.sounds = {}

        # Starts a thread to load sounds in the background.
        # Helps with performance as most sounds should be preloaded
        # before they actually need to be used during gameplay.
        _thread.start_new_thread(self.preload_sounds, tuple())
    
    def generate_sound(
            self,
            filename,
            volume = 1,
            pitch = 1,
            pan = 0,
            group = None,
            loop = False,
            priority = 1
    ):
        # Creates a new SoundInstance that references some SoundData
        # from this SoundLibrary.
        return SoundInstance(
            self.app,
            self.get_sound_data(filename),
            group,
            volume,
            pitch,
            pan,
            loop,
            priority
        )

    def generate_positional_sound(
            self,
            filename,
            pos,
            volume = 1,
            pitch = 1,
            group = None,
            loop = False,
            priority = 1
    ):
        # Creates a new PositionalSoundInstance that references some SoundData
        # from this SoundLibrary.
        return PositionalSoundInstance(
            self.app,
            self.get_sound_data(filename),
            pos,
            group,
            volume,
            pitch,
            loop,
            priority
        )

    def get_sound_data(self, filename):
        # If the sound data has already been loaded, just
        # return a reference to it. Otherwise load in the
        # sound data.
        if not filename in self.sounds:
            self.sounds[filename] = SoundData(self.app, filename)
        return self.sounds[filename]
    
    def preload_sounds(self):
        # Looks through the sound and music folders and loads all
        # of the audio files found. This method is called on a separate
        # thread so it doesn't interrupt gameplay.
        for filename in glob.glob("sounds/**/*.*", recursive=True):
            self.get_sound_data("//".join(filename.split("\\")[1:]))
        for filename in glob.glob("music/**/*.*", recursive=True):
            self.get_sound_data("..//music//" + "//".join(filename.split("\\")[1:]))

class SoundInstance:
    # An instance of a sound, stores a reference to some SoundData
    # which supplies the audio data. Also stores its own pitch,
    # volume, pan and progress through the sound.
    def __init__(
            self,
            app,
            data,
            group,
            volume = 1,
            pitch = 1,
            pan = 0,
            loop = False,
            priority = 1
    ):
        self.app = app

        self.group = group
        
        # We store the previous volume and pitch values to allow
        # this sound's volume and pitch to be smoothly transitioned
        # between. This prevents harsh popping sounds which are
        # caused by sudden changes in volume or pitch.
        self.volume = volume
        self.previousVolume = volume
        self.pan = pan
        self.pitch = pitch
        self.previousPitch = pitch

        self.data = data
        # self.index is the progress through the sound.
        # Each SoundInstance will have a different value
        # for this, even if they reference the same SoundData.
        self.index = 0
        self.loop = loop

        # If this is set to True, this SoundInstance will be removed
        # from SoundLibrary.currentSounds on the next call of
        # SoundLibrary.check_sounds().
        self.toRemove = False

        # Sounds with a lower priority are stopped if there are too
        # many sounds playing at once.
        self.priority = priority

    def get_frames(self, n):
        # Gets audio data from self.data and updates
        # some attributes ready for the next call of
        # this method.
        frames, self.index = self.data.get_frames(
            self.index,
            n,
            self.previousVolume,
            self.volume,
            self.previousPitch,
            self.pitch,
            self.pan,
            self.loop
        )
        if self.loop:
            self.index %= self.data.length
        self.previousVolume = self.volume
        self.previousPitch = self.pitch
        return frames

    def finished(self):
        # If self.toRemove is True or we have reached the end of the sound and
        # this sound isn't set to loop, we want the sound to be removed from
        # SoundLibrary.currentSounds so we return True.
        return self.toRemove or (not self.loop) and self.index > self.data.length

    def remove(self):
        # This sound should be removed from SoundLibrary.currentSounds
        # on the next call of SoundLibrary.check_sounds().
        self.volume = 0
        self.toRemove = True

class PositionalSoundInstance(SoundInstance):
    # A SoundInstance with a position, automatically calculates
    # volume and pan values based on its position relative to the
    # camera's position.
    def __init__(
            self,
            app,
            data,
            pos,
            group,
            volume = 1,
            pitch = 1,
            loop = False,
            priority = 1
    ):
        super().__init__(app, data, group, volume, pitch, 0, loop, priority)
        self.pos = pos
        # The volume values we calculate will be relative to this value.
        self.fullVolume = volume
        self.cameraPos = self.app.camera.pos
        self.previousVolume = self.calculate_volume_and_pan()[0]

    def get_frames(self, n):
        self.volume, self.pan = self.calculate_volume_and_pan()
        return super().get_frames(n)

    def calculate_volume_and_pan(self):
        # Here we calculate volume and pan values based on this sound's
        # position relative to the camera position.
        # You can see a graph of the volume falloff in the explanation
        # of this method in the document.
        volume = self.fullVolume * min(1, -(max(0, self.cameraPos.distance_to(self.pos) - 100) / 200) + 1)
        pan = min(1, max(-1, (self.pos.x - self.cameraPos.x) / 300))
        return volume, pan

class DelayEffect:
    # Takes audio data as input and applies a delay/comb filter
    # effect to it.
    def __init__(
            self,
            delayTime,
            decayFactor,
            delayVolume = 1
    ):
        # The delay between successive echoes.
        self.delayTime = delayTime
        # The factor that each successive echo's amplitude is multiplied by.
        self.decayFactor = decayFactor
        # The factor that the entire effect's amplitude is multiplied by.
        self.delayVolume = delayVolume

        # self.recentSamples is an array to store recent input samples.
        # This is written to and then sampled from at an earlier point,
        # causing the feedback delay effect.
        self.delaySamples = math.ceil(self.delayTime * SAMPLERATE)
        self.recentSamplesLength = self.delaySamples
        self.recentSamples = np.zeros((self.recentSamplesLength, 2), dtype = "float32")

    def apply(self, soundPlayer, data, frameCount):
        # The delay effect works by writing incoming audio data to
        # self.recentSamples and reading from this array at an earlier
        # point.
        writePointer = self.recentSamplesLength - frameCount
        readPointer = self.recentSamplesLength - self.delaySamples

        # Each time this method is called, we the audio data in self.recentSamples
        # down to make room for the incoming audio data to be written.
        self.recentSamples = np.concatenate([self.recentSamples[frameCount:], np.zeros((frameCount, 2))])

        # We write the incoming audio data to self.recentSamples.
        frames = data * self.decayFactor
        self.recentSamples[writePointer : writePointer + frameCount] += frames

        # Then we read from an eariler point in self.recentSamples, reduce its
        # amplitude and mix it with the audio data we have just written.
        # This is the echo. The audio we write feeds back into the audio we
        # read, so successive echoes will be picked up and be mixed back
        # into the audio at a lower amplitude.
        frames = self.recentSamples[readPointer : readPointer + frameCount] * self.decayFactor
        self.recentSamples[writePointer : writePointer + frameCount] += frames

        frames = self.recentSamples[readPointer : readPointer + frameCount] * self.delayVolume

        # Finally we apply the delay effect to the original audio input.
        soundPlayer.mix(data, frames)