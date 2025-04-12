import base64
from typing import Any, Annotated

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import APIRouter, Depends

from auth.src.config import settings
from auth.src.utils.load_rsa import load_public_key

router = APIRouter(prefix="/")

jwks = Annotated[dict[str, list[dict[str, Any]]], 200]


@router.get("/.well-known/jwks.json", status_code=200)
async def get_jwks(public_key: RSAPublicKey = Depends(load_public_key)) -> jwks:
    public_numbers = public_key.public_numbers()
    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": settings.current_kid,
                "use": "sig",
                "alg": "RS256",
                "n": base64.urlsafe_b64encode(
                    public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8)
                )
                .decode()
                .rstrip("="),
                "e": base64.urlsafe_b64encode(
                    public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8)
                )
                .decode()
                .rstrip("="),
            }
        ]
    }
