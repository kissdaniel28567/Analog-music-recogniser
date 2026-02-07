import acoustid
import sounddevice as sd
import soundfile as sf
import os

class RecognitionService:
    def __init__(self):
        # Replace with your Client API Key from acoustid.org
        self.api_key = 'mH7FTfAlK6'

    def record_audio(self, duration=15, filename='temp_recording.wav', device_index=None):
        """
        Records audio. For AcoustID, we need a slightly longer sample 
        (15-20s) to have a better chance of matching vinyl.
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

    def identify_audio(self, file_path):
        """
        Generates a fingerprint using fpcalc and sends it to AcoustID.
        """
        print("🔍 Generating fingerprint and querying AcoustID...")
        
        try:
            for score, recording_id, title, artist in acoustid.match(self.api_key, file_path):
                # a match was found
                return {
                    "status": "Success",
                    "score": score,
                    "title": title,
                    "artist": artist,
                    "id": recording_id
                }
            
            # no match was found
            return {"status": "No Match Found"}

        except acoustid.FingerprintGenerationError:
            return {"status": "Error: Could not generate fingerprint. Is 'fpcalc' installed/in the folder?"}
        except acoustid.WebServiceError as e:
            return {"status": f"API Error: {e}"}
        except Exception as e:
            return {"status": f"Unknown Error: {e}"}