import os
import io
from groq import Groq
from termcolor import colored
from dotenv import load_dotenv

load_dotenv()

class KuroTTS:
    def __init__(self):
        print(colored("🎤 Initializing Groq TTS...", "cyan"))
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
             print(colored("❌ Groq API Key missing in .env", "red"))
             self.client = None
             return

        try:
            self.client = Groq(api_key=api_key)
            print(colored("✅ Groq TTS Ready", "green"))
        except Exception as e:
            print(colored(f"❌ Failed to initialize Groq TTS: {e}", "red"))
            self.client = None

    def generate_audio(self, text: str):
        if not self.client:
            print(colored("❌ TTS Client not initialized", "red"))
            return None

        print(colored(f"🗣️  Generating audio via Groq: '{text[:30]}...'", "cyan"))
        
        try:
            response = self.client.audio.speech.create(
                model="canopylabs/orpheus-v1-english",
                voice="autumn",
                response_format="wav",
                input=text,
            )
            
            # Convert binary content to BytesIO buffer to match existing interface
            # Note: BinaryAPIResponse might need .read() or .content depending on version
            # User snippet used stream_to_file. .read() should get all bytes.
            audio_data = response.read()
            buffer = io.BytesIO(audio_data)
            buffer.seek(0)
            return buffer

        except Exception as e:
            print(colored(f"❌ Groq TTS Generation Error: {e}", "red"))
            return None

# Singleton instance
tts_engine = KuroTTS()
