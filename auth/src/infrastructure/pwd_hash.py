import logging

import bcrypt

logger = logging.getLogger(__name__)


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())  # type: ignore


def verify_password(password: str, hashed_password: bytes) -> bool:
    try:
        res = bcrypt.checkpw(password.encode(), hashed_password)
    except ValueError:
        logger.warning("Invalid hash")
        return False
    else:
        return res  # type: ignore
