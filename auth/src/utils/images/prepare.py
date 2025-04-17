from io import BytesIO

from PIL import Image
from PIL.Image import Resampling


def process_image_to_webp(
    file_obj: BytesIO, resize_to: tuple[int, int] = (512, 512), quality: int = 85
) -> tuple[BytesIO, str]:
    """
    Обработка изображения для аватарки: центрированная обрезка, ресайз и конвертация в WebP.

    :param file_obj: BytesIO с данными изображения.
    :param resize_to: Размер для ресайза (ширина, высота), по умолчанию 512x512.
    :param quality: Качество WebP (0-100), по умолчанию 85.
    :return: (BytesIO с обработанным изображением, MIME-тип).
    """
    file_obj.seek(0)
    image = Image.open(file_obj).convert("RGB")  # Конвертируем в RGB для WebP

    # Центрированная обрезка до квадрата
    width, height = image.size
    min_side = min(width, height)
    left = (width - min_side) // 2
    top = (height - min_side) // 2
    image = image.crop((left, top, left + min_side, top + min_side))

    # Ресайз к целевому размеру
    image = image.resize(resize_to, Resampling.LANCZOS)

    # Сохранение в WebP
    output = BytesIO()
    image.save(output, format="WEBP", quality=quality)
    output.seek(0)

    return output, "image/webp"
