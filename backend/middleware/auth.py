"""
Authentication middleware for protecting routes with session tokens
"""
from functools import wraps
from flask import request, jsonify
import jwt
from utils.jwt_helper import verify_session_token


def require_session_token(f):
    """
    Decorator to protect routes - validates JWT session token from Chrome extension

    Usage:
        @require_session_token
        def protected_route():
            user_id = request.user_id  # Access user_id from token
            ...

    The decorator:
    1. Extracts session token from Authorization header
    2. Validates and decodes the JWT
    3. Attaches user_id to request object for use in route handler
    4. Returns 401 if token is missing, invalid, or expired

    Expected header format:
        Authorization: Bearer <session_token>
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401

        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid authorization header format. Expected: Bearer <token>'}), 401

        token = auth_header.split('Bearer ')[1]

        try:
            payload = verify_session_token(token)
            # Attach user_id to request object for use in route handler
            request.user_id = payload.get('user_id')
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Session token has expired'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': f'Invalid session token: {str(e)}'}), 401
        except Exception as e:
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401

    return decorated_function
