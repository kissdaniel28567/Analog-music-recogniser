import sounddevice as sd
import soundfile as sf
import asyncio
from shazamio import Shazam

class RecognitionService:
    def __init__(self):
        self.shazam = Shazam()

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