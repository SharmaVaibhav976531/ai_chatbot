# backend/app/storage/s3.py

import boto3
import asyncio
from botocore.exceptions import ClientError
from app.core.config import settings
from app.storage.base import BaseStorage

class S3Storage:
    """AWS S3 storage implementation."""

    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket = settings.AWS_S3_BUCKET

    async def save(self, file_content: bytes, destination: str) -> str:
        def _upload():
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=destination,
                Body=file_content
            )
            return f"s3://{self.bucket}/{destination}"

        return await asyncio.to_thread(_upload)

    async def delete(self, path: str) -> None:
        def _delete():
            try:
                self.s3_client.delete_object(Bucket=self.bucket, Key=path)
            except ClientError:
                pass # Ignore if not found

        await asyncio.to_thread(_delete)