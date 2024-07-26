from abc import ABC, abstractmethod
from kivy.event import EventDispatcher
from kivy.clock import Clock
from kivy.app import App

import os
import logging
import queue
import sys
import threading

try:
    import io

    import sounddevice as sd  # type: ignore
    import soundfile as sf  # type: ignore
except ModuleNotFoundError:
    message = (
        "`pip install sounddevice soundfile` required` "
    )
    raise ValueError(message)

class BaseApiSettings(ABC, EventDispatcher):
    _instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BaseApiSettings, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        super(BaseApiSettings, self).__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.load_settings, 1.5) # Do an initial load of settings

    @classmethod
    @abstractmethod
    def isSupported(cls):
        """
        This property must be overridden in derived classes.
        It should return a boolean indicating if the API is functionally supported yet.
        """
        pass

    @classmethod
    @abstractmethod
    def get_settings_widget(cls):
        """
        This method must be overridden in derived classes.
        It should return the widget that will be displayed in the settings popup.
        """
        pass

    @abstractmethod
    def load_settings(self):
        """
        This method must be overridden in derived classes.
        It should load the API specific settings into the application.
        """
        pass

    @abstractmethod
    def save_settings(self):
        """
        This method must be overridden in derived classes.
        It should return the settings from the API in JSON format.
        """
        pass

class BaseApi(ABC, EventDispatcher):
    _instance = None
    buffersize = 2
    blocksize = 2048

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BaseApi, cls).__new__(cls)
        return cls._instance

    def __init__(self, settings: BaseApiSettings, **kwargs):
        super(BaseApi, self).__init__(**kwargs)
        self.settings = settings
        self.q = queue.Queue(maxsize=self.buffersize)
        self.event = threading.Event()

    def play(self, audio_file_name="output_file.wav"):
        """
        This method plays the given audio_file_name in the tmp folder.

        Only override it, if you need a special playback.
        """
        # Placeholder implementation
        app_instance = App.get_running_app()
        tmp_path = app_instance.global_settings.get_tmp_dir()
        if len(os.listdir(tmp_path)) == 0:
            logging.error("Directory is empty. Press generate first!")
        else:
            # name of your audio file
            audio_path = os.path.join(tmp_path, audio_file_name)
            logging.info("Playing audio file %s",audio_path)
            logging.info("file exists %s",os.path.exists(audio_path))
            try:
                t=threading.Thread(target=lambda: self.play_raw(audio_path))
                t.start()
            except Exception as error:
                logging.error("Could not play audio file: %s, reason: %s", audio_path,error)



    @abstractmethod
    def synthesize(self, input: str, file: str):
        """
        This method must be overridden in derived classes.
        It should synthesize the text to audio and save it to the file.

        If the API does not support audio synthesis, it should raise a NotImplementedError.
        """
        pass

    def callback(self, outdata, frames, time, status):
        assert frames == self.blocksize
        if status.output_underflow:
            print('Output underflow: increase blocksize?', file=sys.stderr)
            raise sd.CallbackAbort
        assert not status
        try:
            data = self.q.get_nowait()
        except queue.Empty as e:
            print('Buffer is empty: increase buffersize?', file=sys.stderr)
            raise sd.CallbackAbort from e
        if len(data) < len(outdata):
            outdata[:len(data)] = data
            outdata[len(data):] = b'\x00' * (len(outdata) - len(data))
            raise sd.CallbackStop
        else:
            outdata[:] = data

    def play_raw(self, filename):
        self.q = queue.Queue(maxsize=self.buffersize)
        try:
            with sf.SoundFile(filename) as f:
                for _ in range(self.buffersize):
                    data = f.buffer_read(self.blocksize, dtype='float32')
                    if not data:
                        break
                    self.q.put_nowait(data)  # Pre-fill queue
                stream = sd.RawOutputStream(
                    samplerate=f.samplerate, blocksize=self.blocksize,
                    channels=f.channels, dtype='float32',
                    callback=self.callback, finished_callback=self.event.set)
                with stream:
                    timeout = self.blocksize * self.buffersize / f.samplerate
                    while data:
                        data = f.buffer_read(self.blocksize, dtype='float32')
                        self.q.put(data, timeout=timeout)
                    self.event.wait()  # Wait until playback is finished
        except Exception as e:
            logging.error(type(e).__name__ + ': ' + str(e))
