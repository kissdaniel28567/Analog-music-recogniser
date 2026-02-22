import threading
import time
import sounddevice as sd
import asyncio
from .extensions import db, socketio
from .models import Cartridge, TrackHistory, User
from .audio.capture import AudioCapture
from .audio.processing import AudioProcessor
from .services.recognition_service import RecognitionService
from . import create_app

stop_thread = False
is_identifying = False 

def identify_and_save(app, device_id=None):
    """
    Helper function to run recognition -> save to DB -> notify frontend.
    """
    global is_identifying
    is_identifying = True
    SAMPLE_RATE = 44100
    
    print("Identification triggered...")
    socketio.emit('status_change', {'status': 'identifying'})

    # 1. Initialize Service
    service = RecognitionService()
    processor = AudioCapture()
    
    # 2. Record Audio
    temp_file = processor.record_audio(duration=8, device_index=device_id)
    
    # 3. Identify
    if temp_file:
        result = asyncio.run(service.identify_audio(temp_file))
        
        # 4. Process Result
        match = None
        if len(result.get('matches', [])) > 0:
            track = result.get('track', {})
            title = track.get('title')
            artist = track.get('subtitle')
            cover = track.get('images', {}).get('coverart')
            
            match = {
                'title': title,
                'artist': artist,
                'cover': cover
            }
            print(f"✅ Match: {title} by {artist}")

            # 5. Save to Database
            with app.app_context():
                # TODO: Map to user
                history = TrackHistory(title=title, artist=artist, cover_art=cover)
                db.session.add(history)
                db.session.commit()
        else:
            print("❌ No match found")

        # 6. Send to Frontend
        socketio.emit('track_identified', match)
    
    is_identifying = False
    socketio.emit('status_change', {'status': 'listening'})

def audio_processing_thread(app):
    """
    Background thread that captures audio, processes it, 
    and updates the active cartridge stats in the database.
    """
    print("🎤 Audio Processing Thread Started")
    
    # Basic Settings
    SAMPLE_RATE = 44100
    BLOCK_SIZE = 4096
    DB_COMMIT_INTERVAL = 10

    processor = AudioProcessor(sample_rate=SAMPLE_RATE)
    
    with app.app_context():
        last_commit_time = time.time()
        
        # --- FIXED LOOP STRUCTURE ---
        while not stop_thread:
            # 1. State Check: If we are busy identifying, pause this thread
            if is_identifying:
                time.sleep(1)
                continue

            # 2. Open Stream (Only if we are LISTENING)
            try:
                print("👂 Opening Audio Stream...")
                with sd.InputStream(channels=2, samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE) as stream:
                    
                    # 3. Reading Loop
                    while not stop_thread and not is_identifying:
                        indata, overflow = stream.read(BLOCK_SIZE)
                        
                        if overflow:
                            print("⚠️ Audio Buffer Overflow")

                        clicks = processor.detect_clicks(indata)
                        music_playing = processor.check_music_start(indata, chunk_duration=BLOCK_SIZE/SAMPLE_RATE)
                        rms_volume = processor.calculate_rms(indata)

                        # --- AUTO-DETECT TRIGGER ---
                        if music_playing:
                            print("🎵 Music start detected! Triggering identification...")
                            
                            threading.Thread(target=identify_and_save, args=(app,)).start()
                            break 

                        # --- DB UPDATES ---
                        active_cart = Cartridge.query.filter_by(is_active_on_turntable=True).first()
                        
                        if music_playing or clicks > 0:
                            if active_cart:
                                if clicks > 0:
                                    active_cart.total_clicks += clicks
                                
                                if music_playing:
                                    seconds_passed = BLOCK_SIZE / SAMPLE_RATE
                                    hours_to_add = seconds_passed / 3600.0
                                    active_cart.total_hours += hours_to_add

                        if time.time() - last_commit_time > DB_COMMIT_INTERVAL:
                            db.session.commit()
                            last_commit_time = time.time()

                        # Send Data to Frontend
                        socketio.emit('stats_update', {
                            'is_playing': music_playing,
                            'clicks': clicks,
                            'rms': float(rms_volume),
                            'total_hours': active_cart.total_hours if active_cart else 0,
                            'total_clicks': active_cart.total_clicks if active_cart else 0
                        })
                        
            except Exception as e:
                print(f"❌ Stream Error: {e}")
                time.sleep(1)

@socketio.on('manual_detect')
def handle_manual_detect():
    if not is_identifying:
        from flask import current_app
        threading.Thread(target=identify_and_save, args=(current_app._get_current_object(),)).start()

if __name__ == '__main__':
    # 1. Create the Flask App
    app = create_app()

    # 2. Start the Audio Thread
    t = threading.Thread(target=audio_processing_thread, args=(app,), daemon=True)
    t.start()

    # 3. Start the Web Server
    print("Server starting on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)