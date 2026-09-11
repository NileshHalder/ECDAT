"""
Database & secret storage using AES and ChaCha20 encryption.
"""
import hashlib
import hmac

from Crypto.Cipher import AES, ChaCha20


def encrypt_secret_payload(key: bytes, plaintext: bytes):
    # Partial Risk: AES (safe with 256-bit keys under Grover's)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return cipher.nonce, ciphertext, tag

def sign_webhook_hmac(secret_key: bytes, message: bytes) -> str:
    # Partial Risk: HMAC with SHA-256
    return hmac.new(secret_key, message, hashlib.sha256).hexdigest()

def stream_encrypt(key: bytes, nonce: bytes, data: bytes) -> bytes:
    # Partial Risk: ChaCha20 stream cipher
    cipher = ChaCha20.new(key=key, nonce=nonce)
    return cipher.encrypt(data)
