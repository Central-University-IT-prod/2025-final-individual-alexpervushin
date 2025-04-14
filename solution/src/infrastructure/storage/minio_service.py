import io
import json
from typing import Final
from uuid import UUID

from minio import Minio
from minio.error import S3Error
from src.core.settings import Settings
from src.domain.storage.exceptions import (
    MinioDeleteError,
    MinioGetUrlError,
    MinioServiceError,
    MinioUploadError,
)


class MinioService:
    MAX_FILE_SIZE: Final[int] = 10 * 1024 * 1024

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.bucket_name = settings.minio_bucket_name
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)

            policy: dict[
                str, str | list[dict[str, str | list[str] | dict[str, str]]]
            ] = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": [
                            "s3:GetObject",
                            "s3:ListBucket",
                            "s3:GetBucketLocation",
                        ],
                        "Resource": [
                            f"arn:aws:s3:::{self.bucket_name}/*",
                            f"arn:aws:s3:::{self.bucket_name}",
                        ],
                    }
                ],
            }
            self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))

        except S3Error as e:
            raise MinioServiceError(f"Failed to ensure bucket exists: {e}")

    async def upload_image(self, campaign_id: UUID, image_data: bytes) -> str:
        try:
            result = self.client.put_object(
                self.bucket_name,
                f"{campaign_id}",
                io.BytesIO(image_data),
                length=len(image_data),
                content_type="image/jpeg",
            )
            return result.object_name

        except S3Error as e:
            raise MinioUploadError(f"Failed to upload image: {e}")
        except Exception as e:
            raise MinioUploadError(f"Unexpected error uploading image: {e}")

    async def delete_image(self, campaign_id: UUID) -> None:
        try:
            self.client.remove_object(self.bucket_name, f"{campaign_id}")

        except S3Error as e:
            if e.code == "NoSuchKey":
                return
            raise MinioDeleteError(f"Failed to delete image: {e}")
        except Exception as e:
            raise MinioDeleteError(f"Unexpected error deleting image: {e}")

    async def get_image_url(self, campaign_id: UUID) -> str | None:
        try:
            url = f"http://{self.settings.minio_public_host}/{self.settings.minio_bucket_name}/{campaign_id}"
            return url

        except Exception as e:
            raise MinioGetUrlError(f"Unexpected error getting image URL: {e}")
