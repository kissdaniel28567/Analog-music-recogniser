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

@cart_bp.route('/<int:id>/update_limits', methods=['POST'])
@login_required
def update_cart_limits(id):
    data = request.json
    cart = Cartridge.query.filter_by(id=id, user_id=current_user.id).first()
    if not cart: return jsonify({"error": "Not found"}), 404
    
    cart.recommended_hours = int(data.get('recommended_hours', cart.recommended_hours))
    db.session.commit()
    return jsonify({"message": "Limits updated"})

@cart_bp.route('/<int:id>/reset', methods=['POST'])
@login_required
def reset_cart_hours(id):
    cart = Cartridge.query.filter_by(id=id, user_id=current_user.id).first()
    if not cart: return jsonify({"error": "Not found"}), 404
    
    cart.total_hours = 0.0
    db.session.commit()
    return jsonify({"message": "Hours reset to zero"})

@cart_bp.route('/add', methods=['POST'])
@login_required
def add_cartridge():
    data = request.json
    name = data.get('name')
    recommended_hours = data.get('recommended_hours', 1000)
    
    if not name or str(name).strip() == "":
        return jsonify({"error": "Cartridge name is required"}), 400
        
    new_cart = Cartridge(
        name=name.strip(),
        recommended_hours=int(recommended_hours),
        user_id=current_user.id,
        total_hours=0.0,
        total_clicks=0,
        is_active_on_turntable=False # Inactive at defult, this might change in the future. 
    )
    
    db.session.add(new_cart)
    db.session.commit()
    
    return jsonify({"message": f"Cartridge '{name}' added successfully!"}), 201

@cart_bp.route('/<int:id>/delete', methods=['DELETE'])
@login_required
def delete_cartridge(id):
    cart_to_delete = Cartridge.query.filter_by(id=id, user_id=current_user.id).first()
    if not cart_to_delete: 
        return jsonify({"error": "Cartridge not found"}), 404
        
    # Prevent deleting if it's the only cartridge they own
    user_carts = Cartridge.query.filter_by(user_id=current_user.id).count()
    if user_carts <= 1:
        return jsonify({"error": "You cannot delete your only cartridge!"}), 400

    if cart_to_delete.is_active_on_turntable:
        fallback_cart = Cartridge.query.filter_by(user_id=current_user.id).filter(Cartridge.id != id).first()
        if fallback_cart:
            fallback_cart.is_active_on_turntable = True
            
    db.session.delete(cart_to_delete)
    db.session.commit()
    
    return jsonify({"message": "Cartridge deleted successfully"})