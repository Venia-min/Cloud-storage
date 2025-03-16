# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем переменные окружения для предотвращения записи в .pyc файлы и буферизацию
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем файлы зависимостей в рабочую директорию
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости без dev-пакетов и без создания локального venv
RUN poetry config virtualenvs.create false && poetry install --no-root

# Копируем весь код проекта в контейнер
COPY . .

# Определяем команду для запуска приложения
RUN chmod a+x /app/src/docker/*.sh

CMD ["/app/src/docker/start_app.sh"]