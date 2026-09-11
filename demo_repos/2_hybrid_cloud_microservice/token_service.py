"""
Cloud Microservice Token Service.
Uses modern pre-quantum standards (ECDSA secp256r1 + SHA-256).
Vulnerable to quantum Shor's algorithm, requiring migration to ML-DSA (FIPS 204).
"""
import hashlib

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec


class MicroserviceTokenService:
    def __init__(self):
        # Vulnerable: Elliptic Curve (ECDSA NIST P-256) broken by Shor's algorithm
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()

    def generate_token_fingerprint(self, token_data: bytes) -> str:
        # Partial Risk: SHA-256 hash (needs 384/512 or SHA-3 for maximum quantum margin)
        return hashlib.sha256(token_data).hexdigest()

    def sign_jwt_claims(self, claims: bytes) -> bytes:
        return self.private_key.sign(
            claims,
            ec.ECDSA(hashes.SHA256())
        )
