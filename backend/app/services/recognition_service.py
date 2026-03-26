import sounddevice as sd
import soundfile as sf
import asyncio
from shazamio import Shazam
import json
from acrcloud.recognizer import ACRCloudRecognizer

class RecognitionService:
    def __init__(self):
        self.shazam = Shazam()
        self.acr_config = {
            'host': 'identify-eu-west-1.acrcloud.com',
            'access_key': 'd41e473cd4b971eb9759744bfb738176',
            'access_secret': 'FMTx4bPHVkj9QoD706gsfLJKpmSavfSYbFkEX2cM',
            'timeout': 10
        }
        self.acr_recognizer = ACRCloudRecognizer(self.acr_config)

    async def identify_audio(self, file_path):
        """
        Identifies audio using Shazam (Asynchronous) and ACRcloud.
        """
        print("⚡ Sending to Shazam...")
    
        try:
            out = await self.shazam.recognize(file_path)
            if len(out.get('matches', [])) > 0:
                track = out.get('track', {})
            
                apple_id = None
                for action in track.get('hub', {}).get('actions',[]):
                    if action.get('type') == 'applemusicplay':
                        apple_id = action.get('id')
                
                return {
                    'matches': [True],
                    'title': track.get('title'),
                    'artist': track.get('subtitle'),
                    'ids': {'apple': apple_id, 'spotify': None, 'youtube': None}
                }
        except Exception as e:
            print(f"⚠️ Shazam Error: {e}")

        print("☁️ Shazam failed. Attempting ACRCloud Fallback...")
        acr_result_raw = self.acr_recognizer.recognize_by_file(file_path, 0)
        acr_data = json.loads(acr_result_raw)
        
        if acr_data.get('status', {}).get('msg') == 'Success':
            music = acr_data['metadata']['music'][0]
            external = music.get('external_metadata', {})
            
            return {
                'matches': [True],
                'title': music.get('title'),
                'artist': music.get('artists', [{}])[0].get('name'),
                'ids': {
                    'apple': external.get('apple_music', {}).get('track', {}).get('id'),
                    'youtube': external.get('youtube', {}).get('vid')
                }
            }
            
        return {"matches": []}