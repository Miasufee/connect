import aioboto3
from botocore.exceptions import ClientError

from .base import StorageBackend


class S3Storage(StorageBackend):
    def __init__(
        self,
        bucket: str,
        region: str,
        access_key: str,
        secret_key: str,
        endpoint_url: str | None = None,
    ):
        self.bucket = bucket
        self.session = aioboto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )
        self.endpoint_url = endpoint_url

    async def upload(
        self,
        data: bytes,
        key: str,
        content_type: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        async with self.session.client(
            "s3", endpoint_url=self.endpoint_url
        ) as s3:
            await s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
                Metadata=metadata or {},
            )
        return f"s3://{self.bucket}/{key}"

    async def download(self, key: str) -> bytes:
        async with self.session.client(
            "s3", endpoint_url=self.endpoint_url
        ) as s3:
            obj = await s3.get_object(Bucket=self.bucket, Key=key)
            return await obj["Body"].read()

    async def delete(self, key: str) -> None:
        async with self.session.client(
            "s3", endpoint_url=self.endpoint_url
        ) as s3:
            await s3.delete_object(Bucket=self.bucket, Key=key)

    async def exists(self, key: str) -> bool:
        async with self.session.client(
            "s3", endpoint_url=self.endpoint_url
        ) as s3:
            try:
                await s3.head_object(Bucket=self.bucket, Key=key)
                return True
            except ClientError:
                return False

    async def get_url(self, key: str, expires: int | None = 3600) -> str:
        async with self.session.client(
            "s3", endpoint_url=self.endpoint_url
        ) as s3:
            return await s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires,
            )
