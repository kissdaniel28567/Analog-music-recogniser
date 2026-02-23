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
                with app.app_context():
                    try:
                        history = TrackHistory(title=title, artist=artist, cover_art=cover)
                        db.session.add(history)
                        db.session.commit()
                    except Exception as e:
                        print(f"❌ DB Error: {e}")
                        db.session.rollback()
                    finally:
                        db.session.remove()
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
    
    SAMPLE_RATE = 44100
    BLOCK_SIZE = 4096
    DB_COMMIT_INTERVAL = 10 

    processor = AudioProcessor(sample_rate=SAMPLE_RATE)
    buffer_clicks = 0
    buffer_seconds = 0.0

    with app.app_context():
        last_commit_time = time.time()
        
        while not stop_thread:
            if is_identifying:
                time.sleep(1)
                continue

            try:
                with sd.InputStream(channels=2, samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE) as stream:
                    while not stop_thread and not is_identifying:
                        indata, overflow = stream.read(BLOCK_SIZE)
                        
                        # 1. Process Audio
                        clicks = processor.detect_clicks(indata)
                        music_playing = processor.check_music_start(indata, chunk_duration=BLOCK_SIZE/SAMPLE_RATE)
                        rms_volume = processor.calculate_rms(indata)

                        # 2. Auto-Detect Trigger
                        if music_playing:
                            print("🎵 Music start detected! Triggering identification...")
                            threading.Thread(target=identify_and_save, args=(app,)).start()
                            break 

                        # 3. ACCUMULATE IN MEMORY
                        if music_playing:
                            buffer_seconds += (BLOCK_SIZE / SAMPLE_RATE)
                        
                        if clicks > 0:
                            buffer_clicks += clicks

                        # 4. WRITE TO DB
                        if time.time() - last_commit_time > DB_COMMIT_INTERVAL:
                            if buffer_seconds > 0 or buffer_clicks > 0:
                                try:
                                    active_cart = Cartridge.query.filter_by(is_active_on_turntable=True).first()
                                    
                                    if active_cart:
                                        active_cart.total_hours += (buffer_seconds / 3600.0)
                                        active_cart.total_clicks += buffer_clicks
                                        
                                        db.session.commit()
                                        print("💾 Stats saved to DB")

                                    buffer_clicks = 0
                                    buffer_seconds = 0.0
                                except Exception as e:
                                    print(f"⚠️ DB Write Error: {e}")
                                    db.session.rollback()
                                finally:
                                    db.session.remove() 
                            
                            last_commit_time = time.time()

                        # 5. Emit to Frontend
                        #socketio.emit('stats_update', {
                        #    'is_playing': music_playing,
                        #    'clicks': clicks,
                        #    'rms': float(rms_volume),
                        #})

                        socketio.emit('stats_update', {
                            'is_playing': processor.is_playing, 
                            'clicks': clicks,
                            'rms': float(rms_volume)#,
                            #'total_hours': active_cart.total_hours if active_cart else 0,
                            #'total_clicks': active_cart.total_clicks if active_cart else 0
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