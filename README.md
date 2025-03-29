# Cloud Storage

## Описание проекта
Этот проект представляет собой облачное хранилище файлов с возможностью загрузки, управления файлами и папками, а также авторизации пользователей.

## Требования
Перед запуском убедитесь, что у вас установлены:
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Настройка и запуск

1. **Клонируйте репозиторий**  
 ```bash
 git clone https://github.com/Venia-min/Cloud-storage.git
 cd Cloude-storage
 ```

3. **Создайте .env файл**
- Скопируйте .env.example в .env:
```bash
cp .env.example .env
```

4. Заполните .env файл, соответствуя параметрам вашего окружения.

5. **Запустите контейнеры**
- Для запуска Docker контейнеров используйте команду:
```bash
docker-compose up --build
```

6.	**Откройте проект в браузере**
- Главная страница сервиса по адресу:
  http://localhost:8000
- Администрирование MinIO по адресу:
  http://localhost:9001

## Дополнительные команды
-	Применение миграций:
```bash
docker-compose exec app python manage.py migrate
```

-	Создание суперпользователя:
```bash
docker-compose exec app python manage.py createsuperuser
```

-	Остановка контейнеров:
```bash
docker-compose down
```





