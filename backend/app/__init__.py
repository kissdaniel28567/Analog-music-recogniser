from flask import Flask
from flask_cors import CORS
from .extensions import db, login_manager, socketio
from .models import User

def create_app():
    app = Flask(__name__)
    
    # SECURITY NOTE: Might need to change the random long string!
    app.config['SECRET_KEY'] = 'dev_secret_key_123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turntable.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {"timeout": 30} 
    }

    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .api.auth import auth_bp
    from .api.cartridges import cart_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(cart_bp, url_prefix='/api/cartridges')

    with app.app_context():
        from sqlalchemy import text
        try:
            db.session.execute(text("PRAGMA journal_mode=WAL"))
            print("✅ SQLite WAL Mode Enabled")
        except Exception as e:
            print(f"⚠️ Could not enable WAL mode: {e}")
        db.create_all()

    return app