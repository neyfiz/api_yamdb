# API YaMDb

Проект YaMDb собирает отзывы пользователей на различные произведения: фильмы, книги, музыку и другие. Пользователи могут оставлять текстовые отзывы, оценки и комментарии.

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

Документация API доступна по адресу: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

### Регистрация и аутентификация

1. Зарегистрировать пользователя:
    ```bash
    POST /api/v1/auth/signup/ 
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
