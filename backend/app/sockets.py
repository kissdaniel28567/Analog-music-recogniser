import threading
import time
from flask import current_app
from .extensions import socketio, db
from .models import Cartridge, AlbumColor
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
        state.is_userdetect = True
        state.temp_start_time = time.time()
        app = current_app._get_current_object()
        threading.Thread(target=identify_and_save, args=(app,)).start()

@socketio.on('set_vinyl_color')
def handle_set_vinyl_color(data):
    color_class = data.get('color')
    artist = state.current_track.get('artist')
    title = state.current_track.get('title')

    if not color_class or not title:
        return

    print(f"🎨 User changed vinyl color to: {color_class}")
    
    state.current_track['color'] = color_class

    app = current_app._get_current_object()
    with app.app_context():
        active_cart = Cartridge.query.filter_by(is_active_on_turntable=True).first()
        if active_cart and active_cart.owner:
            existing_record = AlbumColor.query.filter_by(
                user_id=active_cart.owner.id,
                artist=artist,
                title=title
            ).first()

            if existing_record:
                existing_record.color_class = color_class
            else:
                new_color_record = AlbumColor(
                    user_id=active_cart.owner.id,
                    artist=artist,
                    title=title,
                    color_class=color_class
                )
                db.session.add(new_color_record)
            
            db.session.commit()