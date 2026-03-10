from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import sounddevice as sd
from ..models import TrackHistory, Cartridge, User
from ..extensions import db

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
        'history':[{'title': h.title, 'artist': h.artist, 'time': h.timestamp.strftime("%Y-%m-%d %H:%M")} for h in history],
        'cartridges':[{'name': c.name, 'hours': c.total_hours, 'active': c.is_active_on_turntable} for c in carts]
    })

@user_bp.route('/settings', methods=['POST'])
@login_required
def update_settings():
    data = request.json
    current_user.rms_threshold = float(data.get('rms_threshold', current_user.rms_threshold))
    current_user.click_sensitivity = float(data.get('click_sensitivity', current_user.click_sensitivity))
    
    device_id = data.get('audio_device_id')
    if device_id is not None and str(device_id).strip() != "":
        current_user.audio_device_id = int(device_id)
        
    db.session.commit()
    return jsonify({'message': 'Settings saved successfully'})

@user_bp.route('/devices', methods=['GET'])
@login_required
def get_devices():
    devices = sd.query_devices()
    dev_list = [{"id": i, "name": d['name']} for i, d in enumerate(devices) if d['max_input_channels'] > 0]
    return jsonify(dev_list)
