# Kivy
from kivy.uix.floatlayout import FloatLayout
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.logger import Logger as log
# KivyMD
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.dialog import MDDialog
from kivy.uix.popup import Popup
# stdlib
import os
import sys
# Custom
from modules.dialog.exitdialog import ExitDialog


class MainScreen(MDScreen):
    title = StringProperty()
    text_input = ObjectProperty(None)
    voice_dialog = None
    selected_voice = StringProperty()
    # FIXME The values of this dictionary needs to be kept in sync with the screen names in main.py (Unfortunately)
    menu_options = {
        "Settings": "settings",
        "About": "about",
        "Exit": None  # NOTE Exit just closes the app and doesn't have an associated screen
    }
    supported_text_files = ["txt", "md", "rst"]


    def __init__(self, title: str, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        # self.file_load_popup = loaddialog.LoadDialog(callback=self.load_textfile, title="Load file", size_hint=(0.9, 0.9))
        # # self.file_load_popup.size = (400, 400)
        # self.file_save_popup = savedialog.SaveDialog(callback=self.save_textfile, title="Save file", size_hint=(0.9, 0.9))
        # # self.file_save_popup.size = (400, 400)
        # self.settings_popup = app_settings.AppSettingsPopup()
        self.title = title
        self.last_path = None
        self.opened_file = None
        # FIXME This is used to keep track of the file manager state (open or closed) but is not currently used
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            icon_selection_button="folder-marker"
        )
        # TODO Adjust the scrollbar within MDFileManager to be more visible (not just a thin line)

        # new: for cursor movement and selection of words
        self.cnt_button = 0
        self.old_cnt_button = 0
        self.old_cursor_index = self.ids.text_main.cursor_index()
        Clock.schedule_once(self.set_focus, 0.1)
        self.load_current_voice()
        App.get_running_app().api.settings.bind(voice_text=self.update_current_voice)

    def load_current_voice(self): 
        app_instance = App.get_running_app()
        # print(f"API in main_screen: ", app_instance.api)
        self.selected_voice = app_instance.global_settings.get_setting("ElevenLabsAPI", "voice")

    def update_current_voice(self, instance, value):
        self.selected_voice = value

    def on_menu_open(self):
        menu_items = [
            {
                "text": option,
                "on_release": lambda x=option: self.menu_callback(x),
            } for option in self.menu_options.keys()
        ]
        self.drop_menu = MDDropdownMenu(
            caller=self.ids.btn_menu, items=menu_items
        )
        self.drop_menu.open()

    def menu_callback(self, text_item):
        self.manager.transition.direction = 'left'
        if text_item not in self.menu_options.keys():
            log.error("%s: Invalid menu option: %s",
                      self.__class__.__name__, text_item)
            return
        if text_item == "Exit":
            ExitDialog().open()
        self.manager.current = self.menu_options[text_item]
        self.drop_menu.dismiss()

    def select_path(self, path):
        log.info("%s: Selected path: %s", self.__class__.__name__, path)
        if os.path.isfile(path):
            self.opened_file = os.path.basename(path)
            self.last_path = os.path.dirname(path)
            log.debug("%s: File: %s - Path: %s", self.__class__.__name__,
                      self.opened_file, self.last_path)
        elif os.path.isdir(path):
            self.last_path = path
        else:
            log.error("%s: Invalid path selected: %s",
                      self.__class__.__name__, path)
        self.exit_manager()

    def exit_manager(self, *args):
        if all([self.last_path, self.opened_file]):
            file = os.path.join(self.last_path, self.opened_file)
            self.load_textfile(file)
        else:
            log.error("%s: No file selected. Last path: %s",
                      self.__class__.__name__, self.last_path)
        self.manager_open = False
        self.file_manager.close()

    def on_load_file(self):
        if self.last_path is not None:
            path = self.last_path
        else:
            path = os.path.expanduser("~")
        self.file_manager.show(path)
        self.manager_open = True

    def on_save_file(self):
        if self.last_path is None or self.opened_file is None:
            log.error("%s: No file opened to save.", self.__class__.__name__)
            return
        file = os.path.join(self.last_path, self.opened_file)
        self.save_textfile(file)

    def load_textfile(self, file: str):
        if file is None:
            log.error("%s: No file selected to load.", self.__class__.__name__)
            return
        if not os.path.isfile(file):
            log.error("%s: Selection is not a file: %s",
                      self.__class__.__name__, file)
            return
        file_base, file_ext = os.path.splitext(file)
        log.debug("%s: File: %s - Extension: %s",
                  self.__class__.__name__, file_base, file_ext)
        if file_ext[1:] not in self.supported_text_files:  # NOTE [1:] Skip the leading period
            log.error("%s: Unsupported file type: %s. Supported types: %s",
                      self.__class__.__name__, file_ext, self.supported_text_files)
            self.opened_file = None
            self.ids.text_main.text = ""
            return
        # FIXME This is not handling file encoding properly and will cause issues with non-ASCII characters (e.g. mutated vowels such as á, é, í, ó, ú, etc.)
        with open(os.path.abspath(file), 'r') as file:
            text = file.read()
            log.info("%s: Loaded file: %s", self.__class__.__name__, file)
            log.debug("%s: Text: %s...", self.__class__.__name__, text[0:40])
            self.ids.text_main.text = text

    def save_textfile(self, file: str):
        if file is None:
            log.error("%s: No file selected to save.", self.__class__.__name__)
            return
        with open(os.path.abspath(file), 'w') as file:
            file.write(self.ids.text_main.text)
            log.info("%s: Saved file: %s", self.__class__.__name__, file)

    def on_select_voice(self):
        api = App.get_running_app().api
        # print(f"This is the api used: {api}")
        print("clicked on voice selection")
        if api:
            voice_names = api.get_available_voices()
            if voice_names:
                # make list of menu-items for every voice
                menu_items = [
                    {
                        "text": voice_name,
                        "on_release": lambda x=voice_name: self.select_voice(x),
                    } for voice_name in voice_names
                ]
                # make dropdown-menu with voice options
                self.dropdown_menu = MDDropdownMenu(
                    # this has to correspond with ID of button that selects the voices
                    caller=self.ids.btn_select_voice,
                    items=menu_items,
                    width_mult=4,
                )
                self.dropdown_menu.open()
            else:
                log.error("%s: No voices available from API.",
                          self.__class__.__name__)
        else:
            log.error("%s: API not available.", self.__class__.__name__)

    def select_voice(self, voice_name):
        # process selected voice names
        log.info("%s: Selected voice: %s", self.__class__.__name__, voice_name)
        api = App.get_running_app().api
        api.set_voice(voice_name)

        popup_window = CustomPopup(content_text=f"You selected the voice: \n{voice_name}",
                                   size_hint=(None, None), size=(400, 400))
        popup_window.open()
        self.dropdown_menu.dismiss()

    def on_play(self):
        # TODO Implement audio playback (this is mostly a placeholder without a backend implementation yet)
        api = App.get_running_app().api
        if api:
            try:
                api.play(self.ids.text_main.text)
            except NotImplementedError:
                log.error(
                    "%s: Audio playback not implemented for this API.", self.__class__.__name__)
            except Exception as e:
                log.error("%s: Error during playback: %s",
                          self.__class__.__name__, e)

    def on_synthesize(self):
        # TODO Implement text to speech synthesis (this is mostly a placeholder without a backend implementation yet)
        api = App.get_running_app().api
        print(api)
        if api:
            try:
                # FIXME: Use constant or configurable output path
                api.synthesize(self.ids.text_main.text, os.path.join('tmp', 'output_file.wav'))
            except NotImplementedError:
                msg = "Text to speech synthesis not implemented for this API."
                log.error("%s: %s", self.__class__.__name__, msg)
                self.ids.label_status.text = msg
            except Exception as e:
                msg = "Error during synthesis"
                log.error("%s: %s: %s", self.__class__.__name__, msg, e)
                self.ids.label_status.text = msg

    def on_cursor_control(self):
        new_cursor_index = self.ids.text_main.cursor_index()
        old_cursor_index = self.old_cursor_index
        cnt_button = self.cnt_button
        old_cnt_button = self.old_cnt_button

        if abs(cnt_button - old_cnt_button) == 0 and abs(new_cursor_index - old_cursor_index) > 1:
            # set cursor to the end of the word
            cursor_in_row_index = self.ids.text_main._cursor[0]
            row = self.ids.text_main._cursor[1]
            text_row = self.ids.text_main._lines[row]

            spaces = []
            for index in range(cursor_in_row_index, len(text_row)):
                char = text_row[index]
                if char == " ":
                    spaces.append(index)
            if spaces:
                end_word_index = spaces[0]
                self.ids.text_main.cursor = (end_word_index, row)
            else:
                self.ids.text_main.do_cursor_movement('cursor_end')

        self.new_cursor_index = self.ids.text_main.cursor_index()
        self.save_old_cursor_index(new_cursor_index)
        self.save_old_cnt_button(cnt_button)

    def save_old_cursor_index(self, cursor_index):
        self.old_cursor_index = cursor_index

    def save_old_cnt_button(self, cnt_button):
        self.old_cnt_button = cnt_button

    def on_cursor_left(self):
        self.ids.text_main.do_cursor_movement('cursor_left')
        self.cnt_button = self.cnt_button + 1
        Clock.schedule_once(self.set_focus, 0.1)

    def on_cursor_right(self):
        self.ids.text_main.do_cursor_movement('cursor_right')
        self.cnt_button = self.cnt_button + 1
        Clock.schedule_once(self.set_focus, 0.1)

    def set_focus(self, dt):
        self.ids.text_main.focus = True
        
class CustomPopup(Popup):
    content_text = StringProperty("")

    def __init__(self, **kwargs):
        super(CustomPopup, self).__init__(**kwargs)


class Popups(FloatLayout):
    voice_name = StringProperty("")

    def __init__(self, voice_name="", **kwargs):
        super(Popups, self).__init__(**kwargs)
        self.voice_name = voice_name
