# Kivy
from kivy.app import App
from kivy.properties import StringProperty, ObjectProperty
from kivy.logger import Logger as log
# KivyMD
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
from kivymd.uix.slider import MDSlider
from kivymd.uix.selectioncontrol import MDSwitch
# stdlib

# new
import os
from pathlib import Path
from pydub import AudioSegment          # TODO: add pydub to dependencies
from pydub.playback import play

# Custom
from ..base import BaseApiSettings, BaseApi

"""
This is an example API implementation. It is a template for creating new APIs.

Each API consists of three classes:
- The API class itself, which is responsible for the API logic and the API calls.
- The API settings class, which is the 'middleware' between the global settings instance and the API widge (View).
- The API widget class, which is the 'View' of the API settings.

In general, there are multiple design patterns possible with this layout.

One possible design pattern is the following:
- Place all SETTING properties in the API widget class.
- Create a special object property (ObjectProperty) holding the instance of the API settings class inside the API widget class.
- BIND the SETTING properties with the widget properties of the API widget class.
- Create callbacks for UI changes, which will update the SETTING properties and then use the API settings object to update the global settings instance. (save_settings)
- The API settings class will load settings from the global settings instance and update the API widget properties. (load_settings)

Another possible design pattern is the following:
- Place all SETTING properties in the API settings class.
- Create a special object property (ObjectProperty) holding the instance of the API settings class inside the API widget class.
- BIND the SETTING properties with the widget properties of the API widget class.
- Create callbacks for UI changes, which will use the API settings object to update the SETTING properties and then instruct settings class to update the global settings instance (save_settings).
- The API settings class will load settings from the global settings instance and update its own SETTING properties. (load_settings)

Both of these design patterns are valid and it's up to the developer to decide which one to use.
Personally, I'd go with the second design pattern, since then it is easer to access settings from the API class. (Otherwise called middleware)

This layout originates from the fact that we're using the BaseApiSettings class to generalize the behaviour of interacting with the global settings instance.
Any derived class of BaseApiSettings will automatically have the required Singleton pattern implemented.

In general, it is NOT necessary to instantiate any of these classes, since the API factory will take care of that upon application startup.
"""

# NOTE This class holds the widget objects and VIEW logic for the specific API settings view.
# NOTE The widget class is responsible for creating callbacks for UI changes and updating settings accordingly.
class ExampleAPIWidget(MDScreen):
    # NOTE The settings object is used whenever UI changes occur that need to update the settings object
    settings = ObjectProperty(None) # NOTE This property is bound to the settings object of the API by the settings class (not the widget class)
    title = StringProperty() # NOTE This property is used to set the title of the API settings screen
    # NOTE Here you could define the SETTING properties of the API if you go with the first design pattern
    # ... (e.g. setting_1 = BooleanProperty(), setting_2 = StringProperty(), setting_3 = NumericProperty(), setting_4 = BooleanProperty()

    def __init__(self, title: str = "Example API Settings", name: str = "example_api_settings", **kwargs):
        super(ExampleAPIWidget, self).__init__(**kwargs)
        self.title = title
        # NOTE The name of the settings screen is set here AND it should be the same copy-paste line for ALL API settings screens
        # You only need to change ExampleAPI to the name of the main logic class of the API
        # The main settings screen (settings.py) EXPECTS this naming scheme to be followed
        self.name = ExampleAPI.__name__.lower() + "_settings"
        # NOTE If you want to bind SETTING properties to widget properties, you would do it here
        # ...(e.g. self.<property>.bind(self.<widget-property> ... )) - Please only do this if you go with the first design pattern
    
    def on_change(self, id: str):
        if id not in self.ids:
            log.error("%s: Invalid setting ID: %s", self.__class__.__name__, id)
        # NOTE I'd recommend a more sophisticated way of determining which widget corresponds to which setting
        # for the sake of simplicity, I'll use the ID and the type of the widget
        # Changes to the SETTING properties are applied here in the first pattern
        if self.ids[id] is MDCheckbox:
            self.settings.setting_1 = self.ids[id].active
        elif self.ids[id] is MDTextField:
            self.settings.setting_2 = self.ids[id].text
        elif self.ids[id] is MDSlider:
            self.settings.setting_3 = self.ids[id].value
        elif self.ids[id] is MDSwitch:
            self.settings.setting_4 = self.ids[id].active
        # If any SETTING properties have changed, the settings object should be instructed to save the settings to the global setting instance.

    # NOTE This method is called when the user presses the 'Return' button in this API settings screen to return to the main settings screen.
    def on_settings_return(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'settings'

# NOTE This class holds the state of the specific API settings and must be derived from BaseApiSettings, which implements the required Singleton pattern for you.
# NOTE The settings class is responsible for loading and saving the settings using the global settings instance.
class ExampleAPISettings(BaseApiSettings):
    # NOTE Here you could define the SETTING properties of the API if you go with the second design pattern
    # ... (e.g. setting_1 = BooleanProperty(), setting_2 = StringProperty(), setting_3 = NumericProperty(), setting_4 = BooleanProperty()

    def __init__(self, widget, **kwargs):
        super(ExampleAPISettings, self).__init__(**kwargs)
        # NOTE Binding this settings object to the Widget's object property
        self.widget = widget # Store reference to the widget
        widget.settings = self # Bind the settings object to the widget
        # NOTE If you want to bind SETTING properties to widget properties, you would do it here
        # ...(e.g. self.<property>.bind(widget.<widget-property> ... )) - Please only do this if you go with the second design pattern

        self.load_settings() # Initial loading of settings for this API

    @classmethod
    def isSupported(cls):
        return True
    
    @classmethod
    def get_settings_widget(cls):
        return ExampleAPIWidget()

    def load_settings(self): # Settings are loaded using the global settings instance
        app_instance = App.get_running_app()
        # NOTE Here all the settings of the API are loaded from the global settings instance
        # First pattern ... (e.g.) self.widget.<setting> = app_instance.global_settings.get_setting(self.__class__.__name__, "<setting>")
        # Second pattern ... (e.g.) self.<setting> = app_instance.global_settings.get_setting(self.__class__.__name__, "<setting>")

    def save_settings(self): # Settings are stored using the global settings instance
        app_instance = App.get_running_app()
        # NOTE Here all the settings of the API are stored in the global settings instance
        # First pattern ... (e.g.) app_instance.global_settings.update_setting(self.__class__.__name__, "<setting>", self.widget.<setting>)
        # Second pattern ... (e.g.) app_instance.global_settings.update_setting(self.__class__.__name__, "<setting>", self.<setting>)
    
    # NOTE This method should return a string represation of the object and all currently valid settings
    def __str__(self) -> str:
        return f"ExampleAPISettings{{example_setting: {self.example_setting}}}"

# NOTE This class holds the API logic and performs the API calls. When instantiated, the settings class of the API shall be passed.
class ExampleAPI(BaseApi):
    def __init__(self, settings: ExampleAPISettings):
        super().__init__(settings)
        self.settings = settings # Store reference to the settings object
        # NOTE If you go with the first design pattern, you would access settings indirectly via the widget object: self.settings.widget.<setting>
        # NOTE If you go with the second design pattern, you would access settings directly through the middleware: self.settings.<setting>

        # NOTE Any API specific initialization code can be placed here

    # Implement abstract methods of BaseApi
    def play(self, input: str):
        """
        method plays audio file, that is saved in the 'tmp' folder.
        """
        print("playing...")
        # Placeholder implementation
        src_path = str(Path(os.path.dirname(__file__)).parents[2])
        tmp_path = os.path.join(src_path, 'tmp')
        # print(tmp_path)
        if len(os.listdir(tmp_path)) == 0:
            print("Directory is empty. Press generate first!")
        else:
            audio_path = os.path.join(tmp_path, 'sample-3s.wav')        # name of your audio file
            # print(audio_path)
            audio = AudioSegment.from_wav(audio_path)
            play(audio)

    def synthesize(self, input: str, file: str):
        print("synthesizing...")
        # Placeholder implementation
        pass
    
    def do_api_specific_stuff(self):
        print(f"Doing stuff with Example setting: ...")

    def __str__(self) -> str:
        return self.__class__.__name__
