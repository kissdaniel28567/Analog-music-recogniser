from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..models import Cartridge
from ..extensions import db

cart_bp = Blueprint('cartridges', __name__)

@cart_bp.route('/', methods=['GET'])
@login_required
def get_my_cartridges():
    carts = Cartridge.query.filter_by(user_id=current_user.id).all()
    output = []
    for c in carts:
        output.append({
            "id": c.id,
            "name": c.name,
            "hours": c.total_hours,
            "active": c.is_active_on_turntable
        })
    return jsonify(output)

@cart_bp.route('/set_active', methods=['POST'])
@login_required
def set_active_cartridge():
    cart_id = request.json.get('cartridge_id')

    my_carts = Cartridge.query.filter_by(user_id=current_user.id).all()
    for c in my_carts:
        c.is_active_on_turntable = False

    target = Cartridge.query.filter_by(id=cart_id, user_id=current_user.id).first()
    if target:
        target.is_active_on_turntable = True
        db.session.commit()
        return jsonify({"message": f"Active cartridge set to {target.name}"})
    
    return jsonify({"error": "Cartridge not found"}), 404