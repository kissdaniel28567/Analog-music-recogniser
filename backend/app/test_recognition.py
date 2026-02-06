from services.recognition_service import RecognitionService
import sounddevice as sd
import asyncio
import os

def main():
    # 1. List devices (only for testing with CLI)
    print(sd.query_devices())
    
    try:
        device_id = int(input("\nEnter your USB Audio Device ID: "))
    except ValueError:
        print("Invalid ID")
        return

    # 2. Initialize Service
    service = RecognitionService()

    # 3. Record (Shazam is very good, 5-8 seconds is usually enough!)
    audio_file = service.record_audio(duration=8, device_index=device_id)

    if not audio_file:
        print("Error recording audio.")
        return

    # 4. Identify (Must run async function)
    result = asyncio.run(service.identify_audio(audio_file))

    # 5. Print Results
    print("\n--- 🎵 SHAZAM RESULT 🎵 ---")
    
    # Check if a match was found
    if len(result.get('matches', [])) > 0:
        track = result.get('track', {})
        print(f"Title:  {track.get('title')}")
        print(f"Artist: {track.get('subtitle')}")
        
        images = track.get('images', {})
        print(f"Cover:  {images.get('coverart')}")
        
        sections = track.get('sections', [])
        if len(sections) > 0:
            for metadata in sections[0].get('metadata', []):
                if metadata.get('title') == 'Album':
                    print(f"Album:  {metadata.get('text')}")
    else:
        print("No match found.")
        # Optional: Print raw result to debug. May create a flag if needed
        print(result)

    # Cleanup
    os.remove(audio_file)

if __name__ == "__main__":
    main()