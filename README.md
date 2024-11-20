# API YaMDb

Проект **YaMDb** собирает отзывы пользователей на различные произведения: фильмы, книги, музыку и другие. Пользователи могут оставлять текстовые отзывы, оценки и комментарии.

## Используемые технологии

- **Python** — 3.9.13
- **Django** — 3.2
- **Django REST Framework** — 3.12.4
- **SQLite** — (по умолчанию)

## Установка

1. Клонировать репозиторий:

    ```bash
    git clone git@github.com:neyfiz/api_yamdb.git
    cd api_yamdb
    ```

2. Создать виртуальное окружение:

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. Установить зависимости:

    ```bash
    pip install -r requirements.txt
    ```

4. Выполнить миграции:

    ```bash
    python manage.py migrate
    ```

5. Запустить сервер:

    ```bash
    python manage.py runserver
    ```

## Использование API

Документация доступна по адресу: [http://127.0.0.1:8000/redoc/]

### Регистрация и аутентификация

1. Зарегистрировать пользователя:

    ```bash
    POST /api/v1/auth/signup/  
    { 
        "email": "user@example.com", 
        "username": "username" 
    }
    ```

    Ответ:

    ```json
    {
        "email": "user@example.com",
        "username": "username"
    }
    ```

2. Получить токен:

    ```bash
    POST /api/v1/auth/token/ 
    { 
        "username": "username", 
        "confirmation_code": "code_from_email" 
    }
    ```

    Ответ:

    ```json
    {
        "token": "your_jwt_access_token"
    }
    ```

3. Создать отзыв:

    ```bash
    POST /api/v1/titles/{title_id}/reviews/
    Authorization: Bearer your_jwt_access_token
    Content-Type: application/json
    ```

    Пример запроса:

    ```json
    {
        "text": "Great movie, highly recommended!",
        "score": 5
    }
    ```

    Ответ:

    ```json
    {
        "id": 1,
        "text": "Great movie, highly recommended!",
        "author": "username",
        "score": 5,
        "pub_date": "2019-08-24T14:15:22Z"
    }
    ```

4. Получить список произведений:

    ```bash
    GET /api/v1/titles/
    Authorization: Bearer your_jwt_access_token
    ```

    Ответ:

    ```json
    {
    "count": 2,
    "next": "string",
    "previous": "string",
    "results": [
        {
            "id": 1,
            "name": "Film Title",
            "year": 2023,
            "rating": 4.5,
            "description": "A thrilling movie about...",
            "genre": [
                {
                    "name": "Action",
                    "slug": "action"
                }
            ],
            "category": {
                "name": "Film",
                "slug": "film"
            }
        }
    }
    ```

5. Добавить комментарий к отзыву:

    ```bash
    POST /api/v1/reviews/1/comments/
    Authorization: Bearer your_jwt_access_token
    Content-Type: application/json
    ```

    Пример запроса:

    ```json
    {
        "text": "I totally agree with this review!"
    }
    ```

    Ответ:

    ```json
    {
        "id": 1,
        "text": "I totally agree with this review!",
        "author": "username",
        "pub_date": "2023-10-01T14:15:22Z"
    }
    ```

## Роли пользователей

- **Аноним** — чтение произведений и отзывов.
- **Пользователь** — создание отзывов и комментариев.
- **Модератор** — редактирование и удаление отзывов и комментариев.
- **Админ** — полные права.

## Команда проекта

Над проектом работали:

- **Neyfiz** — [GitHub](https://github.com/neyfiz)
- **NikLight** — [GitHub](https://github.com/NikLight)
- **Elena Gruzintseva** — [GitHub](https://github.com/ElenaGruzintseva)
