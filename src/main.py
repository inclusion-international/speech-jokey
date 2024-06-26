# Kivy
from kivymd.app import MDApp
from kivy.logger import Logger as log, LOG_LEVELS
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager
from kivy.resources import resource_add_path
from kivy.animation import Animation
from kivy.metrics import dp
# KivyMD
from kivymd.uix.list import MDListItemTrailingIcon
# stdlib
import os
import sys
# Custom
from screens.about import About
from screens.settings import Settings
from screens.main_screen import MainScreen
from modules.dialog.exitdialog import ExitDialog
from modules.util.widget_loader import load_widget
from settings.app_settings import GlobalSettings
from api.api_factory import load_apis

# FIXME This folder shall always be created in the location of the executable, but currently will always be created in the current working directory
# NOTE Need to differentiate launch environment (Release vs. Debug) - where one gets executed via python, the other via deployed executable
TMP_FOLDER = 'tmp'


class SpeechJokey(MDApp):
    def build(self):
        # load_widget(os.path.join(os.path.dirname(loaddialog.__file__), 'loaddialog.kv'))
        # load_widget(os.path.join(os.path.dirname(savedialog.__file__), 'savedialog.kv'))
        # load_widget(os.path.join(os.path.dirname(app_settings.__file__), 'AppSettingsPopup.kv'))
        load_widget(os.path.join(os.path.dirname(
            sys.modules[MainScreen.__module__].__file__), 'main_screen.kv'))
        load_widget(os.path.join(os.path.dirname(
            sys.modules[Settings.__module__].__file__), 'settings.kv'))
        load_widget(os.path.join(os.path.dirname(
            sys.modules[About.__module__].__file__), 'about.kv'))
        load_widget(os.path.join(os.path.dirname(
            sys.modules[ExitDialog.__module__].__file__), 'exitdialog.kv'))
        self.sm = ScreenManager()
        # self.screens = [Screen(name='Title {}'.format(i)) for i in range(4)]
        # self.screens = {
        #     "main": MainScreen(title="Speech Jokey", name="main"),
        #     "settings": Settings(title="Settings", name="settings"),
        #     "about": About(title="About", name="about")
        # }
        self.global_settings = GlobalSettings()
        self.icon = os.path.join(os.curdir, 'speech-jokey.ico')
        Config.set('kivy', 'window_icon', self.icon)
        log.setLevel(LOG_LEVELS["debug"])
        self.apis = load_apis()
        self.api = self.apis.get("ElevenLabsAPI", None)
        example_api = self.apis.get("ExampleAPI", None)
        self.sm.add_widget(MainScreen(title="Speech Jokey", name="main"))
        self.settings = Settings(title="Settings", name="settings")
        self.sm.add_widget(self.settings)
        self.settings.setup_apis([self.api, example_api])
        self.sm.add_widget(About(title="About", name="about"))
        return self.sm

if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    os.makedirs(TMP_FOLDER, exist_ok=True) # This should fix it permanently
    SpeechJokey(kv_file="SpeechJokey.kv").run()
