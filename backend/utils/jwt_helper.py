"""
JWT session token utilities for Chrome extension authentication
"""
import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Optional


def generate_session_token(user_id: str, expires_in_days: int = 7) -> str:
    """
    Generate JWT session token for Chrome extension

    Args:
        user_id: User's UUID from Supabase users table
        expires_in_days: Token expiration in days (default: 7)

    Returns:
        JWT session token string
    """
    jwt_secret = os.getenv('JWT_SECRET')
    if not jwt_secret:
        raise ValueError("JWT_SECRET must be set in environment variables")

    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=expires_in_days),
        'iat': datetime.utcnow()
    }

    token = jwt.encode(payload, jwt_secret, algorithm='HS256')
    return token


def verify_session_token(token: str) -> Dict[str, str]:
    """
    Verify and decode JWT session token

    Args:
        token: JWT session token from Chrome extension

    Returns:
        Decoded token payload containing user_id

    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """
    jwt_secret = os.getenv('JWT_SECRET')
    if not jwt_secret:
        raise ValueError("JWT_SECRET must be set in environment variables")

    try:
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Session token has expired")
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError(f"Invalid session token: {str(e)}")
