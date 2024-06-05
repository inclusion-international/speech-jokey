# Kivy
from kivy.properties import StringProperty
from kivy.logger import Logger as log
# KivyMD
from kivymd.uix.screen import MDScreen
from kivymd.uix.widget import MDWidget
# from ..api.elevenlabsapi.elevenlabsapi import ElevenLabsAPIWidget

# stdlib
# Custom

class Settings(MDScreen):
    title = StringProperty()
    def __init__(self, title: str, api: MDWidget, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.title = title
        log.debug("%s: API: %s", self.__class__.__name__, api)
        if api is not None:
            try:
                self.ids.settings_container.add_widget(api)
            except Exception as e:
                log.error("Error adding widget to settings_container: %s", str(e))