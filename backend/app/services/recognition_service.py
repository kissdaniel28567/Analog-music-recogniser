import os
import json
import sounddevice as sd
import soundfile as sf
from acrcloud.recognizer import ACRCloudRecognizer

class RecognitionService:
    def __init__(self):
        # REPLACE THESE WITH YOUR ACTUAL KEYS FROM ACRCLOUD DASHBOARD
        self.config = {
            'host': 'identify-eu-west-1.acrcloud.com', # Check your specific host region
            'access_key': 'YOUR_ACCESS_KEY_HERE',
            'access_secret': 'YOUR_ACCESS_SECRET_HERE',
            'timeout': 10, # seconds
            'debug': False
        }
        self.recognizer = ACRCloudRecognizer(self.config)

    def record_audio(self, duration=10, filename='temp_recording.wav', device_index=None):
        """
        Records audio from the specified device for 'duration' seconds.
        """
        samplerate = 44100
        channels = 2
        
        print(f"🎤 Recording {duration} seconds...")
        
        # Start recording
        recording = sd.rec(int(duration * samplerate), 
                           samplerate=samplerate, 
                           channels=channels,
                           device=device_index)
        
        # Wait for the recording to finish
        sd.wait()
        
        # Save as WAV file
        sf.write(filename, recording, samplerate)
        print(f"💾 Audio saved to {filename}")
        return filename

    def identify_audio(self, file_path):
        """
        Sends the audio file to ACRCloud and returns the result.
        """
        print("☁️ Sending to ACRCloud for identification...")
        
        # The recognizer.recognize_by_file returns a JSON string
        result_str = self.recognizer.recognize_by_file(file_path, 0)
        
        # Parse JSON string to Python dictionary
        try:
            result = json.loads(result_str)
            return result
        except json.JSONDecodeError:
            return {"status": {"msg": "Error decoding JSON"}}