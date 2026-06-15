from functools import lru_cache

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError
from fastapi import HTTPException

from app.core.config import settings


class ObjectStorageService:
    def __init__(self) -> None:
        self.bucket = settings.minio_bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.minio_endpoint_url,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            use_ssl=settings.minio_secure,
        )

    def ensure_bucket(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code in {"404", "NoSuchBucket"}:
                self.client.create_bucket(Bucket=self.bucket)
                return
            raise HTTPException(status_code=503, detail="Object storage is unavailable") from exc
        except EndpointConnectionError as exc:
            raise HTTPException(status_code=503, detail="Object storage is unavailable") from exc

    def upload_bytes(
        self,
        *,
        object_key: str,
        content: bytes,
        content_type: str | None = None,
    ) -> None:
        self.ensure_bucket()
        try:
            kwargs = {
                "Bucket": self.bucket,
                "Key": object_key,
                "Body": content,
            }
            if content_type:
                kwargs["ContentType"] = content_type
            self.client.put_object(**kwargs)
        except (ClientError, EndpointConnectionError) as exc:
            raise HTTPException(status_code=503, detail="Object storage is unavailable") from exc

    def create_presigned_url(self, object_key: str, expires_in: int = 3600) -> str:
        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": object_key},
                ExpiresIn=expires_in,
            )
        except ClientError as exc:
            raise HTTPException(status_code=503, detail="Object storage is unavailable") from exc


@lru_cache
def get_storage_service() -> ObjectStorageService:
    return ObjectStorageService()
