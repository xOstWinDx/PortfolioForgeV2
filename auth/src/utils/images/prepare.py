from io import BytesIO
from PIL import Image
from PIL.Image import Resampling

# TODO поправить работу с ресайзом, возможно стоит брать центр фотографии и увеличивать её до нужного размера.


def process_image_to_webp(
    file_obj: BytesIO, resize_to: tuple[int, int] = (512, 512), quality: int = 85
) -> tuple[BytesIO, str]:
    """
    Обработка изображения: ресайз и конвертация в WebP.

    :param file_obj: BytesIO с данными изображения.
    :param resize_to: Размер для ресайза (ширина, высота), по умолчанию 512x512.
    :param quality: Качество WebP (0-100), по умолчанию 85.
    :return: (BytesIO с обработанным изображением, MIME-тип).
    """
    # Сбрасываем позицию
    file_obj.seek(0)

    # Открываем изображение
    image = Image.open(file_obj)

    # Ресайз
    image.thumbnail(resize_to, Resampling.LANCZOS)  # LANCZOS для качества

    # Сохраняем в WebP
    output = BytesIO()
    image.save(output, format="WEBP", quality=quality)
    output.seek(0)

    return output, "webp"
