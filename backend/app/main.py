import threading
import time
import sounddevice as sd
import numpy as np
from .extensions import db, socketio
from .models import Cartridge
from .audio.processing import AudioProcessor
from . import create_app

stop_thread = False

def audio_processing_thread(app):
    """
    Background thread that captures audio, processes it, 
    and updates the active cartridge stats in the database.
    """
    print("Audio Processing Thread Started")
    
    # Basic Settings
    SAMPLE_RATE = 44100
    BLOCK_SIZE = 4096
    DB_COMMIT_INTERVAL = 10

    processor = AudioProcessor(sample_rate=SAMPLE_RATE)
    
    # We need to manually push the app context because this is a separate thread
    with app.app_context():
        last_commit_time = time.time()
        
        with sd.InputStream(channels=2, samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE) as stream:
            
            while not stop_thread:
                # 1. Read Audio Data
                indata, overflow = stream.read(BLOCK_SIZE)
                
                if overflow:
                    print("⚠️ Audio Buffer Overflow")

                # 2. Process Audio
                clicks = processor.detect_clicks(indata)
                music_playing = processor.check_music_start(indata, chunk_duration=BLOCK_SIZE/SAMPLE_RATE)
                
                # 3. Calculate Visuals (Optional, for frontend, might be different in the future)
                rms_volume = processor.calculate_rms(indata)

                # 4. Update Database (Only if something happened)
                active_cart = Cartridge.query.filter_by(is_active_on_turntable=True).first()
                
                if music_playing or clicks > 0:
                    if active_cart:
                        if clicks > 0:
                            active_cart.total_clicks += clicks
                        
                        if music_playing:
                            seconds_passed = BLOCK_SIZE / SAMPLE_RATE
                            hours_to_add = seconds_passed / 3600.0
                            active_cart.total_hours += hours_to_add
                
                # 5. Commit to DB (Throttled)
                if time.time() - last_commit_time > DB_COMMIT_INTERVAL:
                    db.session.commit()
                    last_commit_time = time.time()

                # 6. Send Real-Time Data to Frontend
                socketio.emit('stats_update', {
                    'is_playing': music_playing,
                    'clicks': clicks,
                    'rms': float(rms_volume),
                    'total_hours': active_cart.total_hours if active_cart else 0,
                    'total_clicks': active_cart.total_clicks if active_cart else 0
                })

if __name__ == '__main__':
    # 1. Create the Flask App
    app = create_app()

    # 2. Start the Audio Thread
    t = threading.Thread(target=audio_processing_thread, args=(app,), daemon=True)
    t.start()

    # 3. Start the Web Server
    print("Server starting on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)