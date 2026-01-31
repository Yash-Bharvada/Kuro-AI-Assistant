import os
import io
import soundfile as sf
import numpy as np
from kokoro import KPipeline
from termcolor import colored

class KuroTTS:
    def __init__(self):
        print(colored("🎤 Initializing Kokoro TTS...", "cyan"))
        try:
            # lang_code='a' is likely American English (check documentation if fails)
            # This might download the model on first run
            self.pipeline = KPipeline(lang_code='a') 
            print(colored("✅ Kokoro TTS Ready", "green"))
        except Exception as e:
            print(colored(f"❌ Failed to load Kokoro TTS: {e}", "red"))
            self.pipeline = None

    def generate_audio(self, text: str):
        if not self.pipeline:
            raise RuntimeError("TTS Pipeline not initialized")

        print(colored(f"🗣️  Generating audio via Kokoro: '{text[:30]}...'", "cyan"))
        
        # Generate audio
        # pipeline returns a generator or list of (graphemes, phonemes, audio)
        # voice='af_bella' is a good default for female, 'am_michael' for male
        # Let's pick a default voice, 'af_bella' seems popular or 'af_sarah'
        generator = self.pipeline(text, voice='af_bella', speed=1)
        
        # Concatenate audio segments if multiple sentences
        audio_segments = []
        for _, _, audio in generator:
            audio_segments.append(audio)
            
        if not audio_segments:
            return None
            
        full_audio = np.concatenate(audio_segments)
        
        # Convert to WAV bytes
        buffer = io.BytesIO()
        sf.write(buffer, full_audio, 24000, format='WAV') # Kokoro usually 24khz
        buffer.seek(0)
        return buffer

# Singleton instance
tts_engine = KuroTTS()
