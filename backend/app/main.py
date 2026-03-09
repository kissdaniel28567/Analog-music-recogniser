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

class GlobalState:
    is_playing = False
    is_identifying = False
    current_track = {'title': '', 'artist': '', 'cover': None}
    song_start_time = None
    click_history = []
    
    rms = 0.0
    current_clicks = 0
    
    stop_thread = False

state = GlobalState()

def identify_and_save(app, device_id=None):
    """
    Helper function to run recognition -> save to DB -> notify frontend.
    """
    state.is_identifying = True
    
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
        if len(result.get('matches', [])) > 0:
            track = result.get('track', {})
            state.current_track = {
                'title' : track.get('title'),
                'artist' : track.get('subtitle'),
                'cover' : track.get('images', {}).get('coverart')
            }
            found_match = True
            print(f"✅ Match: {state.current_track['title']} by {state.current_track['artist']}")

            # 5. Save to Database
            # TODO: Map to user
            with app.app_context():
                try:
                    history = TrackHistory(
                        title=state.current_track['title'], 
                        artist=state.current_track['artist'], 
                        cover_art=state.current_track['cover'])
                    db.session.add(history)
                    db.session.commit()
                except Exception as e:
                    print(f"❌ DB Error: {e}")
                    db.session.rollback()
                finally:
                    db.session.remove()
        else:
            print("❌ No match found")
            state.current_track = {'title': '', 'artist': '', 'cover': None}

    # 6. Send to Frontend
    state.is_identifying = False
    socketio.emit('track_identified', state.current_track if found_match else None)
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
    #song_start_time = None
    #click_history = []
    buffer_seconds = 0.0

    with app.app_context():
        last_commit_time = time.time()
        
        while not state.stop_thread:
            if state.is_identifying:
                time.sleep(1)
                continue

            try:
                with sd.InputStream(channels=2, samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE) as stream:
                    active_cart = Cartridge.query.filter_by(is_active_on_turntable=True).first()

                    while not state.stop_thread and not state.is_identifying:
                        #if state.is_identifying:
                        #    time.sleep(1)
                        #    continue
                        indata, overflow = stream.read(BLOCK_SIZE)
                        
                        # 1. Process Audio
                        clicks = processor.detect_clicks(indata)
                        music_just_started = processor.check_music_start(indata, chunk_duration=BLOCK_SIZE/SAMPLE_RATE)
                        rms_volume = processor.calculate_rms(indata)

                        state.is_playing = processor.is_playing
                        state.rms = float(rms_volume)
                        state.current_clicks = clicks

                        if music_just_started:
                            print("🎵 Music start detected! Triggering identification...")

                            state.current_track = {'title': '', 'artist': '', 'cover': None}
                            state.song_start_time = time.time()
                            state.click_history = []

                            threading.Thread(target=identify_and_save, args=(app,)).start()
                            break

                        # 2. Auto-Detect Trigger
                        current_track_time = 0.0
                        if state.is_playing:
                            if state.song_start_time is None:
                                state.song_start_time = time.time()
                                # TODO: Clear history for new song. This is not the appropriate place!
                                # click_history = []
                                print("⏱️ Timer Started")
                            current_track_time = time.time() - state.song_start_time
                            buffer_seconds += (BLOCK_SIZE / SAMPLE_RATE)

                            if clicks > 0:
                                event = {
                                    "time": round(current_track_time, 2),
                                    "count": clicks
                                }
                                state.click_history.append(event)
                                print(f"💥 Click detected at {event['time']}s: {clicks}")

                        # 4. WRITE TO DB
                        if time.time() - last_commit_time > DB_COMMIT_INTERVAL:
                            if buffer_seconds > 0:
                                try:
                                    active_cart = Cartridge.query.filter_by(is_active_on_turntable=True).first()
                                    
                                    if active_cart:
                                        active_cart.total_hours += (buffer_seconds / 3600.0)
                                        db.session.commit()
                                        print("💾 Stats saved to DB")
                                    buffer_seconds = 0.0
                                except Exception as e:
                                    print(f"⚠️ DB Write Error: {e}")
                                    db.session.rollback()
                                finally:
                                    db.session.remove() 
                            
                                active_cart = Cartridge.query.filter_by(is_active_on_turntable=True).first()
                            last_commit_time = time.time()
                        # 5. Emit to Frontend
                        socketio.emit('stats_update', {
                            'is_playing': state.is_playing,
                            'rms': state.rms,
                            'track_time': current_track_time,
                            # TODO: Replace this with proper track duration from the detected song
                            'track_duration': 180,
                            'click_history': state.click_history,
                            'click_count_now': state.current_clicks,
                            'current_track': state.current_track,
                            'total_hours': (active_cart.total_hours + (buffer_seconds/3600)) if active_cart else 0
                        })
            except Exception as e:
                print(f"❌ Stream Error: {e}")
                time.sleep(1)

@socketio.on('connect')
def handle_connect():
    print("👤 Client connected. Sending current state...")
    socketio.emit('stats_update', {
        'is_playing': state.is_playing,
        'rms': state.rms,
        'track_time': (time.time() - state.song_start_time) if state.song_start_time else 0,
        'track_duration': 180,
        'click_history': state.click_history,
        'click_count_now': 0,
        'current_track': state.current_track,
        'total_hours': 0
    })
    
    if state.is_identifying:
        socketio.emit('status_change', {'status': 'identifying'})

@socketio.on('manual_detect')
def handle_manual_detect():
    if not state.is_identifying:
        print("👤 User requested manual detection")
        from flask import current_app
        audio_processing_thread(current_app._get_current_object())

if __name__ == '__main__':
    app = create_app()

    t = threading.Thread(target=audio_processing_thread, args=(app,), daemon=True)
    t.start()

    print("Server starting on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)