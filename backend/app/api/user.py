from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import sounddevice as sd
from ..models import TrackHistory, Cartridge, User
from ..extensions import db
from ..services.lastfm_service import LastFmService

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    history = TrackHistory.query.order_by(TrackHistory.timestamp.desc()).limit(20).all()
    carts = Cartridge.query.filter_by(user_id=current_user.id).all()
    
    return jsonify({
        'username': current_user.username,
        'settings': {
            'rms_threshold': current_user.rms_threshold,
            'click_sensitivity': current_user.click_sensitivity,
            'audio_device_id': current_user.audio_device_id
        },
        'lastfm': {
            'connected': current_user.lastfm_session_key is not None,
            'username': current_user.lastfm_username
        },
        'history':[{'title': h.title, 'artist': h.artist, 'time': h.timestamp.strftime("%Y-%m-%d %H:%M")} for h in history],
        'cartridges':[{'id': c.id, 'name': c.name, 'hours': c.total_hours, 
                       'recommended_hours' : c.recommended_hours, 'active': c.is_active_on_turntable} for c in carts]
    })

@user_bp.route('/settings', methods=['POST'])
@login_required
def update_settings():
    data = request.json
    current_user.rms_threshold = float(data.get('rms_threshold', current_user.rms_threshold))
    current_user.click_sensitivity = float(data.get('click_sensitivity', current_user.click_sensitivity))
    
    device_id = data.get('audio_device_id')
    if device_id is None or str(device_id).strip() == "" or device_id == "null":
        current_user.audio_device_id = None
    else:
        current_user.audio_device_id = int(device_id)
        
    db.session.commit()
    return jsonify({'message': 'Settings saved successfully'})

@user_bp.route('/devices', methods=['GET'])
@login_required
def get_devices():
    devices = sd.query_devices()
    dev_list = [{"id": i, "name": d['name']} for i, d in enumerate(devices) if d['max_input_channels'] > 0]
    return jsonify(dev_list)

@user_bp.route('/lastfm/connect', methods=['POST'])
@login_required
def connect_lastfm():
    token = request.json.get('token')
    if not token:
        return jsonify({"error": "No token provided"}), 400

    try:
        lastfm_service = LastFmService()
        
        session_key, username = lastfm_service.get_session_key(token)
        
        current_user.lastfm_session_key = session_key
        current_user.lastfm_username = username
        db.session.commit()
        
        return jsonify({"message": "Connected successfully!", "username": username})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/lastfm/disconnect', methods=['POST'])
@login_required
def disconnect_lastfm():
    current_user.lastfm_session_key = None
    current_user.lastfm_username = None
    db.session.commit()
    return jsonify({"message": "Disconnected"})