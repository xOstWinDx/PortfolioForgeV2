from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from auth.src.config import settings


def load_private_key() -> RSAPrivateKey:
    with open(settings.project_root / "private_key.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
        return private_key


def load_public_key() -> RSAPublicKey:
    with open(settings.project_root / "public_key.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return public_key
