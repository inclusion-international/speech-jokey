try:
    from elevenlabs import voices, generate, play, save, set_api_key, get_api_key
except ImportError:
    raise ImportError("Please install elevenlabs module: pip install elevenlabs (for installation details: https://github.com/elevenlabs/elevenlabs-python)")

if( __name__ == '__main__'):
    import argparse
import pyaudio
from typing import Iterator

# NOTE This is not very functionally solid, just a template for the API integration that can be iterated upon
class ElevenLabsTTS():
    """
    This is a TTS implementation for the ElevenLabs TTS API.
    """
    _models = [
        "eleven_multilingual_v2",
        "eleven_monolingual_v1"
    ]
    def __init__(self, api_key: str = None, voice_name: str = 'Serena', model: str ="eleven_multilingual_v2"):
        if(model not in self._models):
            raise ValueError(f'Model not supported: {model} (must be one of: {", ".join(self._models)})')
        if(not api_key):
            api_key = get_api_key()
            if(not api_key):
                raise ValueError("No API key provided and no API key found in environment variable (ELEVENLABS_API_KEY)");
        else:
            set_api_key(api_key)
        self.voice = next((v for v in voices() if v.name == voice_name), None)
        if(not self.voice):
            raise ValueError(f'Voice not found: {voice_name} (available voices: {", ".join(v.name for v in voices())})')
        self.model = model

    def synthesize(self, input: str, out_filename: str = None):
        """
        Synthesize an input using the ElevenLabs TTS API.

        Args:
            sentence (str): sentence to be synthesized
            out_filename (str): output filename (Optional, if not provided, the audio will be played instead of saved)
        """
        if(not input):
            raise ValueError("Input must not be empty")
        shouldStream = True if not out_filename else False
        audio = generate(text=input, voice=self.voice, model=self.model, stream=shouldStream)
        if(shouldStream):
            play(audio) # FIXME returns a bytes error at the moment
        else:
            save(audio, out_filename)

    @staticmethod
    def get_config():
        return {
            "api_key": str,
            "language": str,
            "voice": str
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="Output filename", default=None)
    args = parser.parse_args()
    tts = ElevenLabsTTS("1935142dfef1ff0488bddbf191a26a94")
    tts.synthesize(input="""
Dear Natascha,

I hope you are doing well! I just wanted to give you a quick update on our project, the SpeechJokey application. We have a small yet exciting update!

We've been working on a class template that communicates with the ElevenLabs API. It's still in an early phase and more of a playground at the moment, but it's a step in the right direction. The aim is for you to find your own path as a DJ using a synthetic voice with this application.

It's a small progress, but an important one. We are still experimenting and trying to fine-tune everything for you. Your thoughts and ideas on this are, as always, very welcome.

Look forward to more as we make further advancements!

Best regards,

Serena the AI voice
    """, out_filename=args.filename)