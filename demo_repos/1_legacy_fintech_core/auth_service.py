"""
Legacy Core Banking Authentication & Session Service.
Contains legacy cryptography vulnerable to quantum attacks (Shor's & Grover's).
"""
import hashlib

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class LegacyAuthManager:
    def __init__(self):
        # Vulnerable: RSA 2048-bit key pair (broken by Shor's algorithm)
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()

    def hash_user_password(self, password: str) -> str:
        # Vulnerable: MD5 hash function (collision and quantum weakness)
        return hashlib.md5(password.encode("utf-8")).hexdigest()

    def sign_session_token(self, payload: bytes) -> bytes:
        # Vulnerable: RSA PKCS1v15 signature with SHA-1
        signature = self.private_key.sign(
            payload,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        return signature
