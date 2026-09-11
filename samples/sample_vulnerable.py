"""Sample file with deliberately vulnerable cryptography, for testing the scanner."""
import hashlib

from cryptography.hazmat.primitives.asymmetric import rsa


def generate_keys():
    # VULNERABLE: RSA is broken by Shor's algorithm
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key

def hash_password(password):
    # VULNERABLE: MD5 is broken classically
    return hashlib.md5(password.encode()).hexdigest()

def weak_hash(data):
    # VULNERABLE: SHA-1 is deprecated
    return hashlib.sha1(data.encode()).hexdigest()
