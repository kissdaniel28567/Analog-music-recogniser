import threading
import time
from flask import current_app
from .extensions import socketio
from .state import state
from .tasks import identify_and_save

@socketio.on('connect')
def handle_connect():
    print("👤 Client connected. Sending current state...")
    socketio.emit('stats_update', {
        'is_playing': state.is_playing,
        'rms': state.rms,
        'track_time': (time.time() - state.song_start_time) if state.song_start_time else 0,
        'track_duration': state.track_duration,
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
        state.isUserdetect = True
        app = current_app._get_current_object()
        threading.Thread(target=identify_and_save, args=(app,)).start()