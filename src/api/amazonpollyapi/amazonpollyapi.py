import boto3
from botocore.exceptions import BotoCoreError, ClientError
import logging as log
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from ..base import BaseApi, BaseApiSettings


class AmazonPollyAPIWidget(MDScreen):
    settings = ObjectProperty(None)
    title = StringProperty("Amazon Polly API Settings")
    access_key_id_input = ObjectProperty(None)  # Field for access key ID input
    secret_access_key_input = ObjectProperty(None)  # Field for secret access key input
    region_input = ObjectProperty(None)  # Field for region input
    voice_selection = ObjectProperty(None)  # Dropdown for selecting voices
    voice_names = ListProperty()

    def __init__(self, title: str = "Amazon Polly API Settings", **kwargs):
        super(AmazonPollyAPIWidget, self).__init__(**kwargs)
        self.title = title
        self.name = AmazonPollyAPI.__name__.lower() + "_settings"
        # Set voice_names from the available voices in AmazonPollyAPI
        self.voice_names = [f"{voice['display_name']}" for voice in AmazonPollyAPI.voices]

    def on_leave(self, *args):
        log.info("Leaving Amazon Polly settings screen.")
        if self.settings:
            self.settings.save_settings()

    def get_current_voice(self):
        return self.voice_selection.text

    def init_api(self):
        self.settings.update_settings(self.access_key_id_input, self.secret_access_key_input)
        self.settings.save_settings()
        app_instance = App.get_running_app()
        api_name = "AmazonPollyAPI"
        app_instance.api_factory.get_api(api_name).reset_api()
        app_instance.api_factory.get_api(api_name).init_api()
        if self.__check_polly_api_key():
            log.info("Amazon Polly API key valid.")
        else:
            log.error("Amazon Polly API key invalid.")

    def __check_polly_api_key(self):
        try:
            session = boto3.session.Session(
                aws_access_key_id=self.settings.access_key_id_text,
                aws_secret_access_key=self.settings.secret_access_key_text,
                region_name=self.settings.region_text
            )

            sts_client = session.client("sts")
            response = sts_client.get_caller_identity()
            return True

        except ClientError as e:
            # Request error
            log.error(f"ClientError: {e.response['Error']['Message']}")
            return False
        except BotoCoreError as e:
            # General boto3 error
            log.error(f"BotoCoreError: {str(e)}")
            return False


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
        self.dropdown.bind(on_select=lambda instance, x: setattr(self, 'text', x))


class AmazonPollyAPISettings(BaseApiSettings):
    api_name = "AmazonPollyAPI"
    access_key_id_text = StringProperty("")
    secret_access_key_text = StringProperty("")
    region_text = StringProperty("")
    voice_text = StringProperty("Vicky")

    @classmethod
    def isSupported(cls):
        return True

    @classmethod
    def get_settings_widget(cls):
        return AmazonPollyAPIWidget()

    def __init__(self, widget, **kwargs):
        super(AmazonPollyAPISettings, self).__init__(**kwargs)
        self.widget = widget
        widget.settings = self

        # Bind the text fields in the widget to settings (correct references)
        self.widget.access_key_id_input.bind(text=self.update_settings)
        self.bind(access_key_id_text=self.widget.access_key_id_input.setter('text'))

        self.widget.secret_access_key_input.bind(text=self.update_settings)
        self.bind(secret_access_key_text=self.widget.secret_access_key_input.setter('text'))

        self.widget.voice_selection.bind(text=self.update_settings)
        self.bind(voice_text=self.widget.voice_selection.setter('text'))

        self.widget.region_input.bind(text=self.update_settings)
        self.bind(region_text=self.widget.region_input.setter('text'))

        self.load_settings()

    def load_settings(self):
        app_instance = App.get_running_app()

        self.access_key_id_text = app_instance.global_settings.get_setting(
            self.api_name, "access_key_id_input", default="")
        self.secret_access_key_text = app_instance.global_settings.get_setting(
            self.api_name, "secret_access_key_input", default="")
        self.region_text = app_instance.global_settings.get_setting(
            self.api_name, "region", default="")
        self.voice_text = app_instance.global_settings.get_setting(
            self.api_name, "voice", default=""
        )
        matching_voice = next(
            (v["display_name"] for v in AmazonPollyAPI.voices if v["internal_name"] == self.voice_text),
            None
        )
        if matching_voice:
            self.widget.voice_selection.text = matching_voice
        else:
            log.warning(f"No matching display name for internal name: {self.voice_text}")

    def save_settings(self):
        app_instance = App.get_running_app()
        app_instance.global_settings.update_setting(
            self.api_name, "access_key_id_input", self.access_key_id_text)
        app_instance.global_settings.update_setting(
            self.api_name, "secret_access_key_input", self.secret_access_key_text)
        app_instance.global_settings.update_setting(
            self.api_name, "region", self.region_text)
        app_instance.global_settings.update_setting(
            self.api_name, "voice", self.voice_text)

    def update_settings(self, instance, value):
        self.access_key_id_text = self.widget.access_key_id_input.text
        self.secret_access_key_text = self.widget.secret_access_key_input.text
        self.region_text = self.widget.region_input.text

        selected_voice = next(
            (v for v in AmazonPollyAPI.voices if v["display_name"] == self.widget.voice_selection.text),
            None
        )
        if selected_voice:
            self.voice_text = selected_voice["internal_name"]
            log.info(f"Saved internal_name: {self.voice_text}")


class AmazonPollyAPI(BaseApi):
    # Define available voices with display names and internal identifiers
    voices = [
        {"display_name": "Vicki (de-DE)", "internal_name": "Vicki", "language": "de-DE"},
        {"display_name": "Marlene (de-DE)", "internal_name": "Marlene", "language": "de-DE"},
        {"display_name": "Hans (de-DE)", "internal_name": "Hans", "language": "de-DE"},
        {"display_name": "Salli (en-US)", "internal_name": "Salli", "language": "en-US"},
        {"display_name": "Kimberly (en-US)", "internal_name": "Kimberly", "language": "en-US"},
        {"display_name": "Justin (en-US)", "internal_name": "Justin", "language": "en-US"},
        {"display_name": "Joey (en-US)", "internal_name": "Joey", "language": "en-US"},
        {"display_name": "Emma (en-GB)", "internal_name": "Emma", "language": "en-GB"},
        {"display_name": "Brian (en-GB)", "internal_name": "Brian", "language": "en-GB"},
        {"display_name": "Amy (en-GB)", "internal_name": "Amy", "language": "en-GB"},
        {"display_name": "Raveena (en-IN)", "internal_name": "Raveena", "language": "en-IN"},
        {"display_name": "Aditi (en-IN)", "internal_name": "Aditi", "language": "en-IN"}
    ]

    ssml_tags = {
        "⏸️": ('<break time="2s"/>', ""),
        "😐": ("<emphasis level=\"reduced\">", "</emphasis>"),
        "🙂": ("<emphasis level=\"moderate\">", "</emphasis>"),
        "😁": ("<emphasis level=\"strong\">", "</emphasis>"),
        "🔈": ("<prosody volume=\"silent\">", "</prosody>"),
        "🔉": ("<prosody volume=\"medium\">", "</prosody>"),
        "🔊": ("<prosody volume=\"loud\">", "</prosody>"),
        "🌏": ("<lang xml:lang=\"en-US\">", "</lang>")
    }

    # Create a mapping for quick lookup of internal names by display name
    voice_mapping = {voice["display_name"]: voice["internal_name"] for voice in voices}

    def __init__(self, settings: AmazonPollyAPISettings):
        super(AmazonPollyAPI, self).__init__(settings)
        self.settings = settings
        self.reset_api()

    def init_api(self):
        if self.session != None and self.polly_client != None:
            # Return, if we are already initialized
            return

        # Load settings if needed for other configurations
        self.settings.load_settings()

        # Access the TextInput fields from the settings widget
        access_key_id_input = self.settings.widget.ids.access_key_id_input.text
        secret_access_key_input = self.settings.widget.ids.secret_access_key_input.text
        region_input = self.settings.widget.ids.region_input.text

        # Initialize a boto3 session with the provided credentials
        self.session = boto3.session.Session(
            aws_access_key_id=access_key_id_input,
            aws_secret_access_key=secret_access_key_input,
            region_name=region_input
        )

        # Create the Polly client from the session
        self.polly_client = self.session.client("polly")

    def reset_api(self):
        self.session=None
        self.polly_client=None

    def get_available_model_names(self):
        return []

    def text_to_api_format(self, text):
        return text

    def text_from_api_format(self, text):
        return text

    def get_available_voice_names(self):
        return [voice["display_name"] for voice in self.voices]

    def set_voice_name(self, display_name):
        # Map the display name to the internal name for synthesis
        internal_name = self.voice_mapping.get(display_name)
        if internal_name:
            self.settings.voice_text = internal_name
            self.settings.save_settings()
        else:
            log.error("Voice not found for display name: %s", display_name)

    def get_voice_name(self):
        selected_voice = self.__get_selected_voice()
        return selected_voice["display_name"]

    def emoji_to_ssml_tag(self, text: str, ssml_tags: dict):
        """
        Convert emojis in the text to Polly-compatible SSML tags.
        """
        ssml_text = "<speak>"
        for emoji, tags in ssml_tags.items():
            open_tag, close_tag = tags
            if close_tag:  # For emojis with both open and close tags
                text = text.replace(emoji, open_tag, 1)  # First occurrence as open tag
                text = text.replace(emoji, close_tag, 1)  # Next occurrence as close tag
            else:  # For self-closing tags
                text = text.replace(emoji, open_tag)
        ssml_text += text + "</speak>"

        return ssml_text

    def synthesize(self, input_text: str, out_filename: str):
        try:
            # First ensure that API is initialized
            self.init_api()

            # Perform SSML conversion
            processed_text = self.emoji_to_ssml_tag(input_text, self.ssml_tags)

            response = self.polly_client.synthesize_speech(
                Text=processed_text,
                TextType="ssml",
                OutputFormat="mp3",
                VoiceId=self.settings.voice_text
            )

            # Ensure audio stream exists and save to file
            if "AudioStream" in response:
                with open(out_filename, "wb") as file:
                    file.write(response["AudioStream"].read())
            else:
                log.error("AudioStream not found in the response.")

        except (BotoCoreError, ClientError) as error:
            log.error(f"An error occurred: {error}")
            raise

    def __get_selected_voice(self):
        selected_voice = next(
            (v for v in self.voices if v['internal_name'] == self.settings.voice_text), None
        )
        return selected_voice
