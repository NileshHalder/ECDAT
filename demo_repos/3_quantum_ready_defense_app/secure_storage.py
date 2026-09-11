"""
Quantum-safe storage using SHA-3, Argon2id, and bcrypt.
"""
import hashlib

import argon2
import bcrypt


def calculate_sha3_digest(data: bytes) -> str:
    # Quantum-Safe: SHA-3 (Keccak) algorithm
    return hashlib.sha3_256(data).hexdigest()

def hash_master_credentials(password: str) -> str:
    # Quantum-Safe: Argon2id memory-hard KDF
    ph = argon2.PasswordHasher()
    return ph.hash(password)

def backup_password_hash(password: str) -> bytes:
    # Quantum-Safe: bcrypt key derivation
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
