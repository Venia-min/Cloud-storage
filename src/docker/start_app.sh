#!/bin/bash

# Запускаем миграции
echo "Запуск миграций..."
python manage.py migrate

# Собираем статику
echo "Сборка статических файлов..."
python manage.py collectstatic --noinput

# Запускаем сервер
echo "Запуск сервера..."
python manage.py runserver 0.0.0.0:8000