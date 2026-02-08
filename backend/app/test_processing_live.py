import sounddevice as sd
import numpy as np
import sys
from audio.processing import AudioProcessor

# --- CONFIGURATION ---
SAMPLE_RATE = 44100
BLOCK_SIZE = 4096 # Size of the chunk 0.1 sedconds
# If it triggers too easily, increase to 0.05. 
# If it never triggers, decrease to 0.005.
RMS_THRESHOLD = 0.01 
REQUIRED_DURATION = 0.7 # Seconds

def main():
    processor = AudioProcessor(sample_rate=SAMPLE_RATE)
    
    chunk_duration = BLOCK_SIZE / SAMPLE_RATE

    print(f"--- Audio Processor Test ---")
    print(f"RMS Threshold: {RMS_THRESHOLD}")
    print(f"Waiting for {REQUIRED_DURATION}s of sustained audio...")
    print("----------------------------")

    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)

        # 1. CALCULATE RMS
        rms = processor.calculate_rms(indata)
        
        # 2. CHECK FOR MUSIC START
        music_started = processor.check_music_start(
            indata, 
            threshold=RMS_THRESHOLD, 
            required_duration=REQUIRED_DURATION,
            chunk_duration=chunk_duration
        )

        # 3. DETECT CLICKS
        click_count = processor.detect_clicks(indata, sensitivity=15)

        # --- VISUALIZATION ---
        
        bar_len = int(rms * 100)
        bar = "#" * bar_len
        
        state_msg = "WAITING"
        if processor.is_playing:
            state_msg = "PLAYING 🎵"
        
        if music_started:
            print("\n\n>>> 🚀 TRIGGER! MUSIC STARTED! 🚀 <<<\n")

        output = f"\r[{state_msg}] RMS: {rms:.4f} | Vol: {bar.ljust(20)} | Clicks: {click_count}"
        sys.stdout.write(output)
        sys.stdout.flush()

    # Select Device intro from before
    print(sd.query_devices())
    try:
        device_id = int(input("\nEnter USB Device ID: "))
    except:
        return
    
    try:
        with sd.InputStream(device=device_id, 
                            channels=2, 
                            samplerate=SAMPLE_RATE, 
                            callback=callback, 
                            blocksize=BLOCK_SIZE):
            print("\nStream started. Play your record! (Ctrl+C to stop)\n")
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()