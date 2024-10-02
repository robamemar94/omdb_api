import jwt
import datetime
import os
from functools import wraps
from http import HTTPStatus

SECRET_KEY = os.getenv('SECRET_KEY')


def generate_jwt(user_id):
    """Generates a JWT token for the specified user."""
    payload = {
        'sub': user_id,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def verify_jwt(token):
    """Verifies a JWT token and returns the user ID if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def jwt_required(func):
    """Decorator to enforce JWT authentication."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        auth_header = self.headers.get('Authorization')

        if not auth_header:
            self.send_http_response(
                "Authorization header is missing.", HTTPStatus.UNAUTHORIZED
            )
            return

        try:
            token = auth_header.split()[1]
            user_id = verify_jwt(token)

            if user_id is None:
                self.send_http_response(
                    "Invalid or expired token.", HTTPStatus.UNAUTHORIZED
                )
                return

        except IndexError:
            self.send_http_response(
                "Invalid Authorization header format.", HTTPStatus.UNAUTHORIZED
            )
            return

        return func(self, *args, **kwargs)

    return wrapper