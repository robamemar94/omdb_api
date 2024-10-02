import hashlib
import logging
import json

from database.database import DatabaseSession
from database.models import User
from services.jwt_service import generate_jwt

logger = logging.getLogger(__name__)


class AuthAPI:
    @staticmethod
    def register(username, password):
        """Registers a new user with the specified username and password."""
        with DatabaseSession() as session:
            existing_user = (
                session.query(User).filter_by(username=username).first()
            )
            if existing_user:
                return {
                           "message": f"User '{username}' already exists."
                       }, 409

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            user = User(username=username, password_hash=password_hash)
            session.add(user)
            session.commit()

            return {
                       "message": f"User '{username}' registered successfully."
                   }, 201

    @staticmethod
    def login(username, password):
        """Logs in and returns a JWT token."""
        with DatabaseSession() as session:
            user = (
                session.query(User).filter(User.username == username).first()
            )

            if user and (
                    user.password_hash == hashlib.sha256(password.encode()).
                    hexdigest()
            ):
                token = generate_jwt(user.id)
                return {
                           "token": token,
                           "message": "Login successful."
                       }, 200
            else:
                return {"error": "Invalid credentials"}, 401


def handle_login(handler):
    """Handles user authentication for login or registration."""
    content_length = int(handler.headers['Content-Length'])
    post_data = handler.rfile.read(content_length)
    data = json.loads(post_data)

    if 'username' not in data or 'password' not in data:
        handler.send_error(400, 'Username and password are required')
        return

    action = handler.path.strip('/').split('?')[0]  # register or login
    username = data['username']
    password = data['password']

    if action == 'register':
        response, status_code = AuthAPI.register(username, password)
    elif action == 'login':
        response, status_code = AuthAPI.login(username, password)

    handler.send_http_response(response, status_code)
