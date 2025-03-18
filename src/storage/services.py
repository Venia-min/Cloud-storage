import boto3
from botocore.exceptions import (
    ClientError,
    NoCredentialsError
)
from django.conf import settings
from django.core.exceptions import PermissionDenied

from src.storage.exceptions import (
    BucketCreationError,
    FileUploadError,
    FileDownloadError,
    StorageError,
    FileDeleteError,
)


# Инициализация клиента S3 (MinIO)
s3_client = boto3.client(
    "s3",
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


# Создание бакета в MinIO
def create_bucket(bucket_name: str):
    """
    Create bucket.
    :param bucket_name:
    :return:
    """
    try:
        # Проверяем, существует ли бакет
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        # Если бакет не существует, создаем его
        try:
            s3_client.create_bucket(Bucket=bucket_name)
        except ClientError as exc:
            raise BucketCreationError(f"Ошибка при создании бакета "
                                      f"{bucket_name}: {exc}")


def check_user_permission(user_id, filename):
    """Проверка прав доступа пользователя на файл"""
    if not filename.startswith(f"user-{user_id}-files/"):
        raise PermissionDenied(f"У вас нет прав для работы с файлом: {filename}")


def upload_file(file, user_id: int, filename: str, bucket_name=settings.AWS_STORAGE_BUCKET_NAME):
    """Загрузка файла в MinIO"""
    create_bucket(bucket_name)
    object_name = f"user-{user_id}-files/{filename}"

    try:
        s3_client.upload_fileobj(file, bucket_name, object_name)
    except (NoCredentialsError, ClientError) as exc:
        raise FileUploadError(filename, exc)

    return object_name


def download_file(user_id: int, filename: str, bucket_name=settings.AWS_STORAGE_BUCKET_NAME):
    """Скачивание файла из MinIO"""
    object_name = f"user-{user_id}-files/{filename}"

    try:
        with open(filename, 'wb') as file:
            s3_client.download_fileobj(bucket_name, object_name, file)
    except (NoCredentialsError, ClientError) as exc:
        raise FileDownloadError(filename, exc)

    return filename


def delete_file(
        user_id: int,
        filename: str,
        bucket_name=settings.AWS_STORAGE_BUCKET_NAME
) -> bool:
    """Удаление файла из MinIO"""
    check_user_permission(user_id, filename)

    try:
        s3_client.delete_object(Bucket=bucket_name, Key=filename)
    except ClientError as exc:
        raise FileDeleteError(filename, exc)

    return True


def list_user_files(
        user_id: int,
        path: str="",
        bucket_name=settings.AWS_STORAGE_BUCKET_NAME
):
    """Получение списка файлов пользователя"""
    prefix = f"user-{user_id}-files/{path}"  # Префикс папки пользователя

    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        files = []
        for obj in response.get("Contents", []):
            files.append({
                "id": obj["Key"], # Используем полный путь в качестве ID
                "name": obj["Key"].replace(prefix, "")})
        return files
    except ClientError as exc:
        raise StorageError(f"Ошибка при получении списка файлов пользователя "
                           f"{user_id}: {exc}")


def generate_breadcrumbs(path):
    """Генерация списка breadcrumbs для навигации"""
    breadcrumbs = []
    if path:
        parts = path.split("/")
        for i in enumerate(parts):
            breadcrumbs.append({
                "name": parts[i],
                "path": "/".join(parts[:i + 1])
            })
    return breadcrumbs


def rename_file(file_id, new_name, bucket_name = settings.AWS_STORAGE_BUCKET_NAME):
    """
    Rename file in minio.
    :param file_id:
    :param new_name:
    :param bucket_name:
    :return:
    """

    # Получаем текущий путь файла в MinIO
    current_key = file_id
    new_key = "/".join(current_key.split("/")[:-1]) + "/" + new_name

    # Переименование файла в MinIO (копируем и удаляем старый)
    s3_client.copy_object(
        Bucket=bucket_name,
        CopySource={"Bucket": bucket_name, "Key": current_key},
        Key=new_key
    )
    s3_client.delete_object(Bucket=bucket_name, Key=current_key)


def get_file_url(user_id, filename):
    """Получаем URL для файла в MinIO"""
    object_name = f"user-{user_id}-files/{filename}"
    return (f"{settings.AWS_S3_ENDPOINT_URL}/"
            f"{settings.AWS_STORAGE_BUCKET_NAME}/{object_name}")
