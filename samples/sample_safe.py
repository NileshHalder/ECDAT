"""Sample file with quantum-safe / current-best-practice cryptography."""
import hashlib

import bcrypt


def hash_password(password):
    # SAFE: bcrypt is a well-vetted KDF, not broken by quantum computers
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def strong_hash(data):
    # SAFE: SHA-3 has no known quantum break beyond Grover's generic speedup
    return hashlib.sha3_256(data.encode()).hexdigest()
