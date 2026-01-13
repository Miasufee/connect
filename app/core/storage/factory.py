from app.core.storage.local import LocalStorage
from app.core.storage.s3 import S3Storage
from app.core.utils.settings import settings


def get_storage():
    if settings.STORAGE_BACKEND == "s3":
        return S3Storage()

    return LocalStorage()
