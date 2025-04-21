from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from auth.src.config import settings

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()


private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption(),
)

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.PKCS1
)

with open(settings.__PRIVATE_KEY_PATH, "wb") as f:
    f.write(private_pem)

with open(settings.PUBLIC_KEY_PATH, "wb") as f:
    f.write(public_pem)
