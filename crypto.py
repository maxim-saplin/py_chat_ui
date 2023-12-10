from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

def encrypt_data(data: bytes, encryption_key: bytes) -> bytes:
    f = Fernet(encryption_key)
    return f.encrypt(data)

def decrypt_data(data: bytes, encryption_key: bytes) -> bytes:
    f = Fernet(encryption_key)
    return f.decrypt(data)


def generate_fernet_key(password: str) -> bytes:
    salt = b'salte_val'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

