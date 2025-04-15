from datetime import datetime
from io import BytesIO
from typing import Annotated

from PIL import Image

from src.application.interfaces.uow import AbstractUnitOfWork
from src.domain.exceptions import ValidationError
from src.domain.user import Avatar
from src.infrastructure.s3 import S3Client
from src.utils.images.calculate_id import calculate_image_id
from src.utils.images.prepare import process_image_to_webp

ImageID = Annotated[str, "image id from database"]
ImageURL = Annotated[str, "image url from s3"]


class ImageService:
    def __init__(self, s3_client: S3Client):
        self.s3_client = s3_client

    async def add(self, file: BytesIO, uow: AbstractUnitOfWork) -> Avatar:
        try:
            Image.open(file).verify()  # Проверяет, что это изображение
        except Exception:
            raise ValidationError("File is not a valid image")
        file.seek(0)  # Сбрасываем позицию для дальнейшей обработки

        file_content, file_extension = process_image_to_webp(file_obj=file)
        image_id = calculate_image_id(file_content)

        if file_url := await uow.images.get(id=image_id):
            return Avatar(id=image_id, file_url=file_url)

        # Формируем имя файла
        file_dir = "profiles/"
        file_name = f"{image_id}_{datetime.now().strftime('%Y-%m-%d')}.{file_extension}"
        file_key = file_dir + file_name
        # Загружаем в S3
        result = await self.s3_client.upload_file(
            file_obj=file_content, file_key=file_key, content_type="image/webp"
        )
        await uow.images.create(id=image_id, file_url=result["file_url"])

        return Avatar(id=image_id, file_url=result["file_url"])
