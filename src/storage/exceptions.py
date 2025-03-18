class StorageError(Exception):
    """Базовый класс для всех исключений, связанных с хранилищем файлов."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class BucketCreationError(StorageError):
    """Ошибка при создании бакета."""

    def __init__(self, bucket_name, error):
        super().__init__(f"Ошибка при создании бакета '{bucket_name}': {error}")

class FileUploadError(StorageError):
    """Ошибка при загрузке файла."""

    def __init__(self, filename, error):
        super().__init__(f"Ошибка при загрузке файла '{filename}': {error}")

class FileDownloadError(StorageError):
    """Ошибка при скачивании файла."""

    def __init__(self, filename, error):
        super().__init__(f"Ошибка при скачивании файла '{filename}': {error}")

class FileNotfoundError(StorageError):
    """Файл не найден в хранилище."""

    def __init__(self, filename, error=None):
        super().__init__(f"Файл '{filename}' не найден в хранилище. '{error}'")

class FileDeleteError(StorageError):
    """Ошибка при удалении файла."""

    def __init__(self, filename, error=None):
        super().__init__(f"Не удалось удалить файл: {filename}. '{error}'")
