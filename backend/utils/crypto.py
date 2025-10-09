"""
Token encryption utilities using Fernet (AES-256)
"""
from cryptography.fernet import Fernet
from typing import Optional


def encrypt_token(token: str, encryption_key: str) -> str:
    """
    Encrypt GitHub access token using Fernet (AES-256)

    Args:
        token: Plain text GitHub access token
        encryption_key: Fernet encryption key (from environment variable)

    Returns:
        Encrypted token as base64 string
    """
    if not token or not encryption_key:
        raise ValueError("Token and encryption key are required")

    fernet = Fernet(encryption_key.encode())
    encrypted = fernet.encrypt(token.encode())
    return encrypted.decode()


def decrypt_token(encrypted_token: str, encryption_key: str) -> str:
    """
    Decrypt GitHub access token

    Args:
        encrypted_token: Encrypted token (base64 string)
        encryption_key: Fernet encryption key (from environment variable)

    Returns:
        Plain text GitHub access token
    """
    if not encrypted_token or not encryption_key:
        raise ValueError("Encrypted token and encryption key are required")

    fernet = Fernet(encryption_key.encode())
    decrypted = fernet.decrypt(encrypted_token.encode())
    return decrypted.decode()


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key

    Returns:
        Base64-encoded encryption key

    Note: Run this once and store the key in your .env file as ENCRYPTION_KEY
    """
    return Fernet.generate_key().decode()
