import sounddevice as sd
import soundfile as sf
import asyncio
from shazamio import Shazam

class RecognitionService:
    def __init__(self):
        self.shazam = Shazam()

    def record_audio(self, duration=10, filename='temp_recording.wav', device_index=None):
        """
        Records audio (Synchronous).
        """
        samplerate = 44100
        channels = 2
        
        print(f"🎤 Recording {duration} seconds...")
        
        try:
            recording = sd.rec(int(duration * samplerate), 
                               samplerate=samplerate, 
                               channels=channels,
                               device=device_index)
            sd.wait()
            sf.write(filename, recording, samplerate)
            print(f"💾 Audio saved to {filename}")
            return filename
        except Exception as e:
            print(f"Error recording: {e}")
            return None

    async def identify_audio(self, file_path):
        """
        Identifies audio using Shazam (Asynchronous).
        """
        print("⚡ Sending to Shazam...")
        
        try:
            out = await self.shazam.recognize(file_path)
            return out
        except Exception as e:
            return {"matches": [], "error": str(e)}