import unittest
import json
from app import create_app
from app.extensions import db
from app.models import User, Cartridge

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.app = create_app()

        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True

        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            from werkzeug.security import generate_password_hash
            test_user = User(
                username='test_user', 
                password_hash=generate_password_hash('password123')
            )
            db.session.add(test_user)
            db.session.commit()

            test_cart = Cartridge(
                name='Default Cartridge', 
                user_id=test_user.id, 
                is_active_on_turntable=True,
                total_hours=12.5,
                recommended_hours=1000
            )
            db.session.add(test_cart)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self):
        """Simulates a login request to establish a session cookie."""
        return self.client.post('/auth/login', json={
            'username': 'test_user',
            'password': 'password123'
        })

    def test_login_success(self):
        """Test if valid credentials return 200 OK and user ID."""
        response = self.login()
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Login successful')
        self.assertIn('user_id', data)

    def test_login_failure(self):
        """Test if invalid credentials return 401 Unauthorized."""
        response = self.client.post('/auth/login', json={
            'username': 'test_user',
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, 401)

    def test_get_profile_unauthorized(self):
        """Test that unauthenticated users cannot access the profile."""
        response = self.client.get('/api/user/profile')

        self.assertIn(response.status_code, [302, 401])

    def test_get_profile_authorized(self):
        """Test that authenticated users receive the correct JSON profile structure."""
        self.login() 

        response = self.client.get('/api/user/profile')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)

        self.assertEqual(data['username'], 'test_user')
        self.assertIn('settings', data)
        self.assertIn('history', data)
        self.assertIn('cartridges', data)

        self.assertEqual(len(data['cartridges']), 1)
        self.assertEqual(data['cartridges'][0]['hours'], 12.5)

    def test_update_settings(self):
        """Test if sending a POST request to settings updates the User model in the DB."""
        self.login()

        new_settings = {
            'rms_threshold': 0.05,
            'click_sensitivity': 25.0,
            'audio_device_id': 2
        }

        response = self.client.post('/api/user/settings', json=new_settings)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            user = User.query.filter_by(username='test_user').first()
            self.assertEqual(user.rms_threshold, 0.05)
            self.assertEqual(user.click_sensitivity, 25.0)
            self.assertEqual(user.audio_device_id, 2)

    def test_update_cartridge_limits(self):
        """Test if the recommended_hours can be updated via the API."""
        self.login()

        response = self.client.post('/api/cartridges/1/update_limits', json={
            'recommended_hours': 500
        })
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            cart = Cartridge.query.get(1)
            self.assertEqual(cart.recommended_hours, 500)

    def test_reset_cartridge_hours(self):
        """Test if the reset endpoint zeroes out the total_hours."""
        self.login()

        response = self.client.post('/api/cartridges/1/reset')
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            cart = Cartridge.query.get(1)

            self.assertEqual(cart.total_hours, 0.0)