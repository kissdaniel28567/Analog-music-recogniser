import sounddevice as sd
import numpy as np
import sys

def list_devices():
    print("\n--- Available Audio Devices ---")
    print(sd.query_devices())
    print("-----------------------------\n")

def audio_callback(indata, frames, time, status):
    """
    Called continuously for each audio block.
    """
    if status:
        print(status, file=sys.stderr)
    
    # RMS calc might need it in the future
    volume_norm = np.linalg.norm(indata) * 10
    bar = "|" * int(volume_norm)
    
    sys.stdout.write("\r\033[K")
    sys.stdout.write(f"\rVolume: {bar.ljust(30)}")
    sys.stdout.flush()

def main():
    list_devices()
    
    try:
        device_id = int(input("Enter the ID number of your SOUND CARD (from the list above): "))
    except ValueError:
        print("Please enter a number!")
        return

    print(f"\nStarting monitoring on device {device_id}... (Press Ctrl+C to stop)")
    
    try:
        with sd.InputStream(device=device_id, channels=2, callback=audio_callback, blocksize=1024):
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()