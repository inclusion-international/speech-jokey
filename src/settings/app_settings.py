# Kivy
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, ListProperty
from kivy.event import EventDispatcher
from kivy.logger import Logger as log
# KivyMD
from kivymd.uix.screen import MDScreen
# stdlib
import os
import importlib
import inspect
import json
from pathlib import Path
# Custom
from api.base import BaseApiSettings
from modules.util.widget_loader import load_widget

def none_settings():
    pass

class GlobalSettings(EventDispatcher):
    _instance = None
    _settings_file = "app_settings.json"
    _default_settings = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalSettings, cls).__new__(cls)
            cls._instance.load_or_initialize_settings()
        return cls._instance

    def load_or_initialize_settings(self):
        if not os.path.exists(self._settings_file):
            self.reset()
        else:
            with open(self._settings_file, 'r') as file:
                self._settings = json.load(file)


    def save_settings(self):
        with open(self._settings_file, 'w') as file:
            json.dump(self._settings, file, indent=4)
            log.info("%s: Settings saved: %s", self.__class__.__name__, self._settings_file)
    
    def load_settings(self):
        if os.path.exists(self._settings_file):
            with open(self._settings_file, 'r') as file:
                self._settings = json.load(file)
        else:
            log.error("%s: Settings file does not exist. Reset or save is required.", self.__class__.__name__)

    def update_setting(self, api_name, key, value):
        log.debug("%s: Update %s: %s to '%s'.", self.__class__.__name__, api_name, key, value)
        if api_name in self._settings.keys():
            self._settings[api_name][key] = value
            self.save_settings()
        else:
            self._settings[api_name] = {key: value}
            self.save_settings()

    def get_setting(self, api_name, key, default=None):
        value = self._settings.get(api_name, {}).get(key, default)
        log.debug("%s: Load %s: %s", self.__class__.__name__, key, value)
        return value
    
    def reset(self):
        self._settings = self._default_settings.copy()
        self.save_settings()