try:
    from elevenlabs import voices, generate, play, save, set_api_key, get_api_key, VoiceSettings
except ImportError:
    raise ImportError(
        "Please install elevenlabs module: pip install elevenlabs (for installation details: https://github.com/elevenlabs/elevenlabs-python)")

if __name__ == '__main__':
    import argparse
import logging
from kivy.app import App
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.logger import Logger as log
from kivymd.uix.screen import MDScreen
from typing import Iterator, List
from ..base import BaseApiSettings, BaseApi
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown

class ElevenLabsAPIWidget(MDScreen):
    settings = ObjectProperty(None)
    title = StringProperty()
    # property values shown in widget
    api_key_input = ObjectProperty(None)
    voice_selection = ObjectProperty(None)
    model_selection = ObjectProperty(None)
    voice_names = ListProperty()
    model_names = ListProperty()

    def __init__(self, title: str = "ElevenLabs API Settings", **kwargs):
        super(ElevenLabsAPIWidget, self).__init__(**kwargs)
        self.title = title
        self.name = ElevenLabsAPI.__name__.lower() + "_settings"

    def transit(self, target: str, direction: str):
        log.info("Transitioning to %s, direction: %s", target, direction)
        self.manager.transition.direction = direction
        self.manager.current = target

    def transit_to_self(self):
        log.info("Transitioning to self")
        self.transit(self.name, 'right')

    # Will be called, when settings widget is left.
    def on_leave(self, *args):
        log.info("on_leave of settings")
        self.settings.save_settings()

    def get_current_voice(self):
        return self.voice_selection.text
    
class CustomSpinner(Button):
    def __init__(self, options, **kwargs):
        super().__init__(**kwargs)
        self.options = options
        self.dropdown = DropDown()
        for option in self.options:
            btn = Button(text=option, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
        self.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance,
                           x: setattr(self, 'text', x))

# Represents the model of the widget class (view).
# Contains the current settings values, which sould be used by the API.
class ElevenLabsAPISettings(BaseApiSettings):
    api_name = "ElevenLabsAPI"
    # NOTE ElevenLabs API SETTING properties (not to be mistaken with the properties of the widget, holding current selections)
    api_key_text = StringProperty("")
    voice_text = StringProperty("")
    model_text = StringProperty("")

    @classmethod
    def isSupported(cls):
        return True

    @classmethod
    def get_settings_widget(cls):
        return ElevenLabsAPIWidget()

    def __init__(self, widget: ElevenLabsAPIWidget, **kwargs):
        super(ElevenLabsAPISettings, self).__init__(**kwargs)
        self.widget = widget  # Save reference to the widget
        widget.settings = self  # Set the settings object in the widget

        # Two-way bind api-key
        # Changes in widget, update settings object
        self.widget.api_key_input.bind(text=self.update_settings)
        # Changes in settings object, update widget
        self.bind(api_key_text=self.widget.api_key_input.setter('text'))

        # Two-way bindings between widget properties and settings properties
        # Changes in widget, update settings object
        self.widget.model_selection.bind(text=self.update_settings)
        # Changes in settings object, update widget
        self.bind(model_text=self.widget.model_selection.setter('text'))

        # Changes in widget, update settings object
        self.widget.voice_selection.bind(text=self.update_settings)
        # Changes in settings object, update widget
        self.bind(voice_text=self.widget.voice_selection.setter('text'))

        self.load_settings()

    # loads the settings from the settings file.
    def load_settings(self):
        app_instance = App.get_running_app()
        self.api_key_text = app_instance.global_settings.get_setting(
            self.api_name, "api_key", default="")
        self.voice_text = app_instance.global_settings.get_setting(
            self.api_name, "voice", default="Serena")
        self.model_text = app_instance.global_settings.get_setting(
            self.api_name, "model", default=ElevenLabsAPI.get_models()[0])

    # saves the settings to the settings file.
    def save_settings(self):
        app_instance = App.get_running_app()
        app_instance.global_settings.update_setting(
            self.api_name, "api_key", self.api_key_text)
        app_instance.global_settings.update_setting(
            self.api_name, "voice", self.voice_text)
        app_instance.global_settings.update_setting(
            self.api_name, "model", self.model_text)

    # Updates the settings: Stores current values of the widget properties in the settings properties.
    def update_settings(self, instance, value):
        log.info("updating %s=%s",instance, value)
        self.api_key_text=self.widget.api_key_input.text
        self.model_text=self.widget.model_selection.text
        self.voice_text=self.widget.voice_selection.text
        #self.save_settings()

class ElevenLabsAPI(BaseApi):
    _models = [
        "eleven_multilingual_v2",
        "eleven_monolingual_v1"
    ]

    def __init__(self, settings: ElevenLabsAPISettings = None):
        super(ElevenLabsAPI, self).__init__(settings)
        logging.debug("Initializing ElevenLabsAPI instance...")
        self.settings = settings
        self.init_api()

    def init_api(self):
        self.settings.load_settings()
        # Try to init the API.
        # This will only work, if the settings are configured properly.
        try:
            set_api_key(self.settings.api_key_text)
            self.settings.widget.model_names=self.get_models()
            self.settings.widget.voice_names=self.get_voices()
        except:
            log.error("API Key invalid: %s",self.settings.api_key_text)
        finally:
            self.settings.widget.model_names=self.get_models()

    # FIXME: This is a duplicate to get_voices()
    def get_available_voices(self):
        """
        get list of available voices
        """
        # Implementeer logica om stemnamen op te halen van de API
        # Dit kan een HTTP-verzoek naar de API zijn of het ophalen van stemnamen uit een lokaal bestand of database
        # Retourneer een lijst met stemnamen
        # Dit is een voorbeeld, vervang dit door de echte implementatie
        try:
            self.init_api()
            return [voice.name for voice in voices()]
        except: return []

    def set_voice(self, voice_name):
        self.settings.voice_text=voice_name
        self.settings.save_settings()
        self.init_api()

    # neue Funktion
    def convert_text(self, text: str):
        text_arr = list(text)
        output_text = ""
        for char in text_arr:
            # print(char)
            if char == ",":  # default pause
                output_text = output_text + "<break time=\"0.0s\" />"

            elif char == "." or char == "?" or char == "!":
                output_text = output_text + "<break time=\"0.5s\" />"

            elif char == ";":
                output_text = output_text + "<break time=\"0.5s\" />"

            output_text = output_text + char
        return output_text

    def synthesize(self, input: str, out_filename: str = None):
        """
        Synthesize an input using the ElevenLabs TTS API.

        Args:
            sentence (str): sentence to be synthesized
            out_filename (str): output filename (Optional, if not provided, the audio will be played instead of saved)
        """
        print(input)
        self.init_api()

        if (not input):
            raise ValueError("Input must not be empty")

        shouldStream = True if not out_filename else False
        self.voice = next((v for v in voices() if v.name ==
                           self.settings.voice_text), None)
        self.model = self.settings.model_text
        set_api_key(self.settings.api_key_text)

        # TODO: hier neuer Teil
        converted_input = self.convert_text(input)

        audio = generate(text=converted_input, voice=self.voice,
                         model=self.model, stream=shouldStream)
        if (shouldStream):
            play(audio)
        else:
            save(audio, out_filename)

    def save(self):
        """
        now you can choose where to save the file .
        """
        pass 

    @staticmethod
    def get_config():
        return {
            "api_key": str,
            "language": str,
            "voice": str
        }

    @staticmethod
    def get_models() -> List[str]:
        return ElevenLabsAPI._models

    @staticmethod
    def get_voices() -> List[str]:
        return [v.name for v in voices()]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename",
                        help="Output filename", default=None)
    args = parser.parse_args()

    # Create an instance of ElevenLabsAPISettings
    api_settings = ElevenLabsAPISettings()

    # Load settings
    api_settings.load_settings()

    # Create an instance of ElevenLabsAPI with the correct settings
    api_key = api_settings.api_key_text
    tts = ElevenLabsAPI(api_settings, api_key)

    # Use the synthesize method with the desired input and output filename
    tts.synthesize(input="""
    Dear Natascha,

    I hope you are doing well! I just wanted to give you a quick update on our project, the SpeechJokey application. We have a small yet exciting update!

    We've been working on a class template that communicates with the ElevenLabs API. It's still in an early phase and more of a playground at the moment, but it's a step in the right direction. The aim is for you to find your own path as a DJ using a synthetic voice with this application.

    It's a small progress, but an important one. We are still experimenting and trying to fine-tune everything for you. Your thoughts and ideas on this are, as always, very welcome.

    Look forward to more as we make further advancements!

    Best regards,

    Serena the AI voice
    """, out_filename=args.filename)

    tts.play()
