from .extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    cartridges = db.relationship('Cartridge', backref='owner', lazy=True)

class Cartridge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    total_hours = db.Column(db.Float, default=0.0)
    total_clicks = db.Column(db.Integer, default=0)
    recommended_hours = db.Column(db.Integer, default=1000)

    is_active_on_turntable = db.Column(db.Boolean, default=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)