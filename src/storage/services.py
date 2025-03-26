import boto3
from botocore.exceptions import (
    ClientError,
    NoCredentialsError
)
from django.conf import settings

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
def create_bucket(bucket_name: str) -> None:
    """
    Create bucket in MinIO.
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
            raise BucketCreationError(
                f"Ошибка при создании бакета {bucket_name}: {exc}"
            )


def get_user_file_path(user_id: int, file_name: str) -> str:
    return f"user-{user_id}-files/{file_name}"


# def get_file_url(user_id: int, file_name: str) -> str:
#     """
#     Получаем URL для файла в MinIO.
#     :param user_id:
#     :param file_name:
#     :return:
#     """
#     full_file_path = get_user_file_path(user_id, file_name)
#     return (f"{settings.AWS_S3_ENDPOINT_URL}/"
#             f"{settings.AWS_STORAGE_BUCKET_NAME}/{full_file_path}")


def upload_file(file, user_id: int, file_name: str,
bucket_name=settings.AWS_STORAGE_BUCKET_NAME) -> str:
    """
    Загрузка файла в MinIO.
    :param file:
    :param user_id:
    :param file_name:
    :param bucket_name:
    :return:
    """
    create_bucket(bucket_name)
    full_file_path = get_user_file_path(user_id, file_name)
    try:
        s3_client.upload_fileobj(file, bucket_name, full_file_path)
    except (NoCredentialsError, ClientError) as exc:
        raise FileUploadError(file_name, exc)

    return file_name


def download_file(
        user_id: int,
        file_name: str,
        bucket_name=settings.AWS_STORAGE_BUCKET_NAME
) -> str:
    """
    Скачивание файла из MinIO.
    :param user_id:
    :param file_name:
    :param bucket_name:
    :return:
    """
    full_file_path = get_user_file_path(user_id, file_name)

    try:
        with open(file_name, 'wb') as file:
            s3_client.download_fileobj(bucket_name, full_file_path, file)
    except (NoCredentialsError, ClientError) as exc:
        raise FileDownloadError(file_name, exc)

    return file_name


def delete_file(
        user_id: int,
        file_name: str,
        bucket_name=settings.AWS_STORAGE_BUCKET_NAME
) -> bool:
    """
    Удаление файла из MinIO.
    :param user_id:
    :param file_name:
    :param bucket_name:
    :return:
    """
    full_file_path = get_user_file_path(user_id, file_name)
    try:
        included_files = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=full_file_path
        )
        objects_to_delete = [{"Key": obj["Key"]} for obj in included_files[
                "Contents"]]
        s3_client.delete_objects(Bucket=bucket_name,
                                 Delete={"Objects": objects_to_delete})
    except ClientError as exc:
        raise FileDeleteError(file_name, exc)
    else:
        return True


def list_user_files(
        user_id: int,
        path: str="",
        bucket_name=settings.AWS_STORAGE_BUCKET_NAME
) -> list[dict]|list:
    """
    Получение списка файлов пользователя.
    :param user_id:
    :param path:
    :param bucket_name:
    :return:
    """
    full_file_path = get_user_file_path(user_id, path)
    # Префикс папки пользователя
    files = []
    exist_files = set()
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=full_file_path)
        for obj in response.get("Contents", []):
            # Адрес вглубь от текущей папки для определения папка/файл
            long_file_name = obj["Key"].removeprefix(full_file_path)
            # Имя только текущего файла
            file_name = long_file_name.split("/")[0]
            if "/" in long_file_name:
                file_name += "/"
            file_path = path + file_name
            if file_name in exist_files or file_name == ".keep":
                continue
            exist_files.add(file_name)
            files.append({
                "id": file_path, # Используем путь в качестве ID
                "name": file_name,
                "is_folder": "/" in long_file_name
            })
    except ClientError as exc:
        raise StorageError(f"Ошибка при получении списка файлов пользователя "
                           f"{user_id}: {exc}")
    return sorted(files, key=lambda x: not x["is_folder"])


def generate_breadcrumbs(path: str) -> list[dict]:
    """
    Генерация списка breadcrumbs для навигации.
    :param path:
    :return:
    """
    breadcrumbs = [{"name": "Root", "path": ""}]
    if path:
        parts = path.split("/")
        for i, part in enumerate(parts):
            breadcrumbs.append({
                "name": part,
                "path": "/".join(parts[:i + 1]) + "/"
            })
    return breadcrumbs


def rename_file(file_name: str, new_name: str, bucket_name: str =
settings.AWS_STORAGE_BUCKET_NAME) -> None:
    """
    Rename file in minio.
    :param file_id:
    :param new_name:
    :param bucket_name:
    :return:
    """

    # Формируем новый путь файла в MinIO
    new_key = "/".join(file_name.split("/")[:-1]) + "/" + new_name

    # Переименование файла в MinIO (копируем и удаляем старый)
    s3_client.copy_object(
        Bucket=bucket_name,
        CopySource={"Bucket": bucket_name, "Key": file_name},
        Key=new_key
    )
    s3_client.delete_object(Bucket=bucket_name, Key=file_name)


def create_folder(user_id: int, file_name: str,
    bucket_name: str = settings.AWS_STORAGE_BUCKET_NAME) -> bool:
    """
    Создание папки в хранилище MinIO/S3.
    :param user_id:
    :param file_name:
    :param bucket_name:
    :return:
    """
    full_file_path = get_user_file_path(user_id, file_name)
    placeholder_file = full_file_path + "/.keep"
    try:
        # Создаем папку (загружаем пустой объект)
        s3_client.put_object(Bucket=bucket_name, Key=placeholder_file, Body=b'')
    except ClientError as exc:
        raise Exception(f"Не удалось создать папку: {str(exc)}")
    else:
        return True


def search_files(user_id: int, query: str,
    bucket_name=settings.AWS_STORAGE_BUCKET_NAME) -> list[dict]:
    """
    Поиск файлов и папок в хранилище MinIO/S3 по имени.
    :param user_id:
    :param query:
    :param bucket_name:
    :return:
    """
    full_prefix = get_user_file_path(user_id, "")  # Префикс папки пользователя

    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=full_prefix)
        results = []
        seen_folders = set()

        for obj in response.get("Contents", []):
            # Убираем user-{user_id}-files/
            full_path = obj["Key"].removeprefix(full_prefix)
            parts = full_path.split("/")

            # Файл
            if query.lower() in parts[-1].lower():
                results.append({
                    "name": parts[-1],
                    "folder_path": "/".join(parts[:-1]),  # Родительская папка
                    "is_folder": False
                })

            # Папка (проверяем все уровни пути)
            for i in range(len(parts) - 1):
                folder_name = parts[i]
                folder_path = "/".join(parts[:i + 1])

                if query.lower() in folder_name.lower() and folder_path not in seen_folders:
                    results.append({
                        "name": folder_name + "/",
                        "folder_path": "/".join(parts[:i]),  # Родительская папка
                        "is_folder": True
                    })
                    seen_folders.add(folder_path)

        return results

    except ClientError as exc:
        raise StorageError(f"Ошибка поиска файлов пользователя {user_id}: {exc}")
