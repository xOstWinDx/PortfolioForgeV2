import hashlib
from io import BytesIO


def calculate_image_id(image: BytesIO) -> str:
    return hashlib.sha256(image.getvalue()).hexdigest()
