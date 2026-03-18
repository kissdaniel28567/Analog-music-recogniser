import threading
import time
import sounddevice as sd
import asyncio
import urllib.request
import urllib.parse
import json

from .extensions import db, socketio
from .models import Cartridge, TrackHistory, AlbumColor
from .audio.capture import AudioCapture
from .audio.processing import AudioProcessor
from .services.recognition_service import RecognitionService

from .state import state

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
        found_match = False
        if len(result.get('matches', [])) > 0:
            track = result.get('track', {})
            new_title = track.get('title')

            if state.current_track['title'] == new_title and state.failed_attempts < 5:
                if state.is_userdetect:
                    message = f"⚠️ Detected the same song again: {new_title}. If you think this is worng press detect again"
                    socketio.emit('info', message)
                else:
                    print(f"⚠️ Detected the same song again: {new_title}. Retrying...")
                    state.failed_attempts += 1
                    found_match = False
            else:
                state.current_track = {
                    'title' : track.get('title'),
                    'artist' : track.get('subtitle'),
                    'album': 'Unknown Album',
                    'cover' : track.get('images', {}).get('coverart'),
                    'color' : 'v-classic'
                }

                # TODO: Might need to reset something else too
                if state.is_userdetect and state.temp_start_time is not None:
                    state.song_start_time = state.temp_start_time - 1
                    state.click_history = []
                
                state.track_duration = 210.0

                apple_music_id = None
                hub = track.get('hub', {})
                for action in hub.get('actions',[]):
                    if action.get('type') == 'applemusicplay' and 'id' in action:
                        apple_music_id = action['id']
                        break
            
                if apple_music_id:
                    try:
                        url = f"https://itunes.apple.com/lookup?id={apple_music_id}"
                        req = urllib.request.Request(url, headers={'User-Agent': 'SmartTurntable/1.0'})
                        
                        with urllib.request.urlopen(req, timeout=5) as response:
                            itunes_data = json.loads(response.read().decode())
                            
                            if itunes_data['resultCount'] > 0:
                                itunes_result = itunes_data['results'][0]
                                duration_ms = itunes_result['trackTimeMillis']
                                state.track_duration = duration_ms / 1000.0

                                fetched_album = itunes_result.get('collectionName')
                                if fetched_album:
                                    state.current_track['album'] = fetched_album
                                print(f"⏱️ Exact duration: {state.track_duration}s | 💿 Album: {state.current_track['album']}")
                            else:
                                print("⚠️ ID lookup returned no duration, using fallbacks.")
                    except Exception as e:
                        print(f"⚠️ API lookup failed: {e}")
                else:
                    print("⚠️ No Apple Music ID in Shazam data, using 210s fallback.")

                with app.app_context():
                    active_cart = Cartridge.query.filter_by(is_active_on_turntable=True).first()
                    if active_cart and active_cart.owner:
                            saved_color_record = AlbumColor.query.filter_by(
                                user_id=active_cart.owner.id,
                                artist=state.current_track['artist'],
                                album=state.current_track['album']
                            ).first()
                            
                            if saved_color_record:
                                state.current_track['color'] = saved_color_record.color_class
                                print(f"🎨 Loaded saved vinyl color: {saved_color_record.color_class}")
                            else:
                                print("🎨 Something went wrong getting vinyl color")

                try:
                    artist_safe = urllib.parse.quote(state.current_track['artist'])
                    track_safe = urllib.parse.quote(state.current_track['title'])

                    lrc_url = f"https://lrclib.net/api/get?artist_name={artist_safe}&track_name={track_safe}"
                    lrc_req = urllib.request.Request(lrc_url, headers={'User-Agent': 'SmartTurntable/1.0'})
                    
                    with urllib.request.urlopen(lrc_req, timeout=5) as response:
                        lrc_data = json.loads(response.read().decode())
                        lyrics = lrc_data.get('syncedLyrics') or lrc_data.get('plainLyrics') or ""
                        state.current_track['lyrics'] = lyrics
                        
                        if lrc_data.get('syncedLyrics'):
                            print("📝 Synced lyrics found!")
                        elif lrc_data.get('plainLyrics'):
                            print("📜 Plain (unsynced) lyrics found.")
                        else:
                            print("⚠️ Lyrics not found in database.")
                except urllib.error.HTTPError as e:
                    # FYI: This only sees if the song is in the database not the lyrics
                    if e.code == 404:
                        print("⚠️ Lyrics not found in database.")
                    else:
                        print(f"⚠️ Lyrics had some HTTP problems {e}")
                except Exception as e:
                    print(f"⚠️ Lyrics API failed: {e}")
                
                if state.is_userdetect and state.temp_start_time is not None:
                    state.song_start_time = state.temp_start_time - 1
                    state.click_history =[]
                    state.temp_start_time = None

                state.failed_attempts = 0
                found_match = True
                print(f"✅ Match: {state.current_track['title']} by {state.current_track['artist']}")

            # 5. Save to Database
            with app.app_context():
                try:
                    history = TrackHistory(
                        title=state.current_track['title'], 
                        artist=state.current_track['artist'],
                        album=state.current_track['album'],
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
            state.failed_attempts += 1

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

                    while not state.stop_thread:
                        if state.is_identifying:
                            time.sleep(1)
                            continue
                        indata, overflow = stream.read(BLOCK_SIZE)
                        
                        current_rms_threshold = 0.01
                        current_click_sensitivity = 15.0
                        
                        if active_cart and active_cart.owner:
                            current_rms_threshold = active_cart.owner.rms_threshold
                            current_click_sensitivity = active_cart.owner.click_sensitivity

                        # 1. Process Audio
                        clicks = processor.detect_clicks(indata, sensitivity=current_click_sensitivity)
                        music_just_started = processor.check_music_start(
                            indata, chunk_duration=BLOCK_SIZE/SAMPLE_RATE,
                            threshold=current_rms_threshold)
                        rms_volume = processor.calculate_rms(indata)
                        rumble_value = processor.measure_rumble(indata)

                        state.is_playing = processor.is_playing
                        state.rms = float(rms_volume)
                        state.current_clicks = clicks
                        state.rumble = float(rumble_value)

                        needs_retry = (state.is_playing
                                       and 0 < state.failed_attempts < 5)
                        
                        if music_just_started or needs_retry:
                            print("🎵 Music start detected! Triggering identification...")
                            state.song_start_time = time.time() - 1
                            state.click_history = []

                            state.is_userdetect = False
                            threading.Thread(target=identify_and_save, args=(app,)).start()
                            break

                        # 2. Auto-Detect Trigger
                        current_track_time = 0.0
                        if state.is_playing:
                            if state.song_start_time is None:
                                state.song_start_time = time.time() - 1
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

                            time_left = state.track_duration - current_track_time

                            if time_left <= 5.0:
                                silence_detected = processor.check_silence_start(
                                    indata, 
                                    threshold=current_rms_threshold, 
                                    required_duration=1.0,
                                    chunk_duration=BLOCK_SIZE/SAMPLE_RATE
                                )
                                
                                if silence_detected:
                                    print("🛑 Silence detected at end of track! Resetting for next song...")
                                    state.is_playing = False
                                    state.song_start_time = None
                                    state.failed_attempts = 0
                                    state.click_history =[]
                                    processor.is_playing = False

                            stop_detected = processor.check_silence_start(
                                indata, 
                                threshold=current_rms_threshold, 
                                required_duration=10.0,
                                chunk_duration=BLOCK_SIZE/SAMPLE_RATE
                            )

                            state.is_paused = processor.track_end_silence_duration >= 3.0

                            if stop_detected:
                                print("🛑 Long silence detected! Resetting for next song...")
                                state.current_track = {
                                    'title': '',
                                    'artist': '', 'album': '', 
                                    'cover': None, 'color': 'v-classic',
                                    'lyrics': ''
                                }
                                state.is_playing = False
                                state.is_paused = False
                                state.song_start_time = None
                                state.failed_attempts = 0
                                state.click_history =[]
                                processor.is_playing = False
                        # 4. WRITE TO DB
                        if time.time() - last_commit_time > DB_COMMIT_INTERVAL:
                            if buffer_seconds > 0:
                                try:
                                    active_cart = Cartridge.query.filter_by(is_active_on_turntable=True).first()
                                    
                                    if active_cart:
                                        active_cart.total_hours += (buffer_seconds / 3600.0)
                                        db.session.commit()
                                        # might need in the future for debug
                                        #print("💾 Stats saved to DB")
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
                            'is_paused': state.is_paused,
                            'rms': state.rms,
                            'track_time': current_track_time,
                            'track_duration': state.track_duration,
                            'click_history': state.click_history,
                            'click_count_now': state.current_clicks,
                            'rumble': state.rumble,
                            'current_track': state.current_track,
                            'total_hours': (active_cart.total_hours + (buffer_seconds/3600)) if active_cart else 0
                        })
            except Exception as e:
                print(f"❌ Stream Error: {e}")
                time.sleep(1)