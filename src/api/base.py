from abc import ABC, abstractmethod
from kivy.event import EventDispatcher
from kivy.clock import Clock
import os
from pathlib import Path
import logging

try:
    import io

    import sounddevice as sd  # type: ignore
    import soundfile as sf  # type: ignore
except ModuleNotFoundError:
    message = (
        "`pip install sounddevice soundfile numpy` required` "
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

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BaseApi, cls).__new__(cls)
        return cls._instance

    def __init__(self, settings: BaseApiSettings, **kwargs):
        super(BaseApi, self).__init__(**kwargs)
        self.settings = settings

    def play(self, audio_file_name="output_file.wav"):
        """
        This method plays the given audio_file_name in the tmp folder.

        Only override it, if you need a special playback.
        """
        # Placeholder implementation
        src_path = str(Path(os.path.dirname(__file__)).parents[1])
        tmp_path = os.path.join(src_path, 'tmp')
        if len(os.listdir(tmp_path)) == 0:
            logging.error("Directory is empty. Press generate first!")
        else:
            # name of your audio file
            audio_path = os.path.join(tmp_path, audio_file_name)
            logging.info("Playing audio file %s",audio_path)
            logging.info("file exists %s",os.path.exists(audio_path))
            try:
                data, fs = sf.read(audio_path)
                sd.play(data, fs)
                # don't call sd.wait() as we want the playback in the background.
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
