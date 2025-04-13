import logging
from io import BytesIO

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from src.config import settings
from src.infrastructure.exceptions import S3ClientException

logger = logging.getLogger(__name__)


class S3Client:
    def __init__(
        self,
        access_key: str = settings.S3_ACCESS_KEY,
        secret_key: str = settings.S3_SECRET_KEY,
        endpoint_url: str = settings.S3_ENDPOINT_URL,
        bucket_name: str = settings.S3_BUCKET_NAME,
        public_domain: str = settings.S3_PUBLIC_DOMAIN,
        region: str = "ru-7",
    ):
        """
        Инициализация клиента S3.

        :param access_key: Ключ доступа.
        :param secret_key: Секретный ключ.
        :param endpoint_url: URL эндпоинта S3 (например, https://s3.ru-7.storage.selcloud.ru).
        :param bucket_name: Имя бакета (например, portfolio-site).
        :param region: Регион (по умолчанию ru-7 для Selectel).
        """
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.region = region
        self.public_domain = public_domain

        self.client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
            region_name=region,
            config=Config(signature_version="s3v4"),
        )

    async def upload_file(
        self, file_obj: BytesIO, file_key: str, content_type: str
    ) -> dict[str, str]:
        """
        Загрузка файла в S3.

        :param file_obj: Объект BytesIO с данными файла.
        :param file_key: Имя файла в бакете (например, profiles/abc123.webp).
        :param content_type: MIME-тип файла (например, image/webp).
        :return: Словарь с информацией о файле (имя, URL).
        """
        try:
            # Сбрасываем позицию BytesIO, если она была изменена
            file_obj.seek(0)

            self.client.upload_fileobj(
                Fileobj=file_obj,
                Bucket=self.bucket_name,
                Key=file_key,
                ExtraArgs={
                    "ContentType": content_type,
                    "ACL": "public-read",  # Делаем объект публичным
                },
            )
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            raise S3ClientException("Failed to upload to S3")

        # Формируем полный URL файла
        file_url = f"https://{self.public_domain}/{file_key}"
        return {
            "filename": file_key,
            "file_url": file_url,
            "message": "File uploaded successfully",
        }
