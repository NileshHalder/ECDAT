"""
User credential derivation using PBKDF2.
"""
import hashlib


def derive_user_encryption_key(password: str, salt: bytes) -> bytes:
    # Partial Risk: PBKDF2 (recommend migrating to Argon2id)
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000,
        dklen=32
    )
