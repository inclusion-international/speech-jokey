# Kivy
from kivy.logger import Logger as log
# KivyMD
# stdlib
import os
import importlib
import traceback
# Custom
from modules.util.widget_loader import load_widget


class ApiFactory:
    @staticmethod
    def get_api(api_name: str):
        try:
            api_module = importlib.import_module(
                f"api.{api_name.lower()}.{api_name.lower()}")
            log.debug("%s: Imported API module: %s",
                      __class__.__name__, api_module)
            api_class = getattr(api_module, api_name)
            settings_class = getattr(api_module, f"{api_name}Settings")
            load_widget(os.path.join(os.path.dirname(
                api_module.__file__), f"{api_name.lower()}.kv"))
            # NOTE THIS is the ONLY place where the API instance is created (And should be created)
            api_instance = api_class(settings_class(settings_class.get_settings_widget()))
            log.debug("%s: Created API instance: %s", __class__.__name__, api_instance)
            return api_instance
        except (ModuleNotFoundError, AttributeError) as e:
            log.error("%s: Error loading API %s: %s",
                      __class__.__name__, api_name, e)
            log.debug("%s: %s", __class__.__name__, traceback.format_exc())
            return None

# Dynamic loading of APIs based on directory structure


def load_apis():
    # TODO Implement dynamic loading based on directory structure instead of a static name list
    # api_names = [name for name in os.listdir("api") if os.path.isdir(os.path.join("api", name))]
    api_names = ["ElevenLabsAPI", "ExampleAPI"]
    apis = {}
    for name in api_names:
        apis[name] = ApiFactory.get_api(name)
    return apis
