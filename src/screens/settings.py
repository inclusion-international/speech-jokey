# Kivy
from kivy.app import App
from kivy.properties import StringProperty
from kivy.logger import Logger as log
# KivyMD
from kivymd.uix.screen import MDScreen
from kivymd.uix.widget import MDWidget
from kivymd.uix.button import MDButton
from kivymd.uix.button import MDButtonIcon
from kivymd.uix.button import MDButtonText
from kivymd.uix.list import MDListItem
# from ..api.elevenlabsapi.elevenlabsapi import ElevenLabsAPIWidget

# stdlib
import traceback
# Custom

class Settings(MDScreen):
    title = StringProperty()
    def __init__(self, title: str, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.title = title
    def setup_apis(self, apis: MDWidget):
        log.debug("%s: API: %s", self.__class__.__name__, apis)
        self.buttons = []
        for api in apis:
            if api is not None:
                try:
                    self.manager.add_widget(api.settings.widget)
                    button = MDButton(
                        MDButtonIcon(icon="chevron-right", pos_hint={"x": 0.05, "center_y": 0.5}),
                        MDButtonText(text=api.settings.widget.title),  # <--- text is VALID here
                        style="text",
                        pos_hint={"x": .01},
                        height="56dp"
                    )
                    # button.add_widget(MDButtonIcon(icon="chevron-right", pos_hint={"center_x": 0.5, "center_y": 0.5}))   # Dreieckspfeil auf Button
                    # button.add_widget(MDButtonText(text=api.settings.widget.title))                     # Text auf Button
                    button.bind(on_release=lambda x, api=api: self.on_settings_transition(api.__class__.__name__.lower() + "_settings"))
                    self.ids.settings_container.add_widget(button)
                    self.buttons.append(button)
                except Exception as e:
                    log.error("Error adding API settings screen: %s", str(e))
                    log.debug("Stacktrace: %s", traceback.format_exc())
    def on_settings_transition(self, screen: str):
        log.debug("%s: Transitioning to %s", self.__class__.__name__, screen)
        self.manager.transition.direction = 'left'
        self.manager.current = screen