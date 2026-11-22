# 🎬 Кинотека (Movie Library)

Веб-приложение для просмотра и управления каталогом фильмов.

Проект разработан в рамках учебной дисциплины «Сетевое программирование».

## 📌 О проекте

«Кинотека» — клиент-серверное веб-приложение, позволяющее пользователям работать с каталогом фильмов.

### Возможности

- Просмотр каталога фильмов.
- Получение подробной информации о фильмах.
- Поиск фильмов.
- Фильтрация по жанрам и году выпуска.
- Добавление, редактирование и удаление фильмов.
- Просмотр списка жанров.
- Регистрация пользователей.
- Авторизация с использованием JWT.
- Получение информации о текущем пользователе.
- Хранение данных в PostgreSQL.

## 🛠 Используемые технологии

| Технология | Назначение |
|---|---|
| Python 3 | Язык Backend |
| FastAPI | Разработка REST API |
| PostgreSQL | Реляционная база данных |
| SQLAlchemy | Работа с базой данных через ORM |
| Alembic | Миграции базы данных |
| Pydantic | Проверка входящих данных |
| JWT | Авторизация пользователей |
| Argon2 | Хеширование паролей |
| Uvicorn | ASGI-сервер |
| Docker | Контейнеризация |
| Git | Контроль версий |

## 📁 Структура проекта

```text
kinoteka/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   ├── seed.py
│   │   └── init__db.py
│   │
│   ├── alembic/
│   ├── .env.example
│   └── requirements.txt
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 🚀 Быстрый запуск через Docker

Это рекомендуемый способ запуска проекта.

### 1. Установите Docker

Перед запуском необходимо установить Docker Desktop:

- macOS: https://www.docker.com/products/docker-desktop/
- Windows: https://www.docker.com/products/docker-desktop/

После установки запустите Docker Desktop и дождитесь полной загрузки.

### 2. Скачайте проект

Откройте терминал и выполните:

```bash
git clone https://github.com/koll777/Movie-Library.git
```

Перейдите в папку проекта:

```bash
cd Movie-Library
```

### 3. Запустите проект

Выполните одну команду:

```bash
docker compose up --build -d
```

Docker автоматически соберёт Backend, запустит PostgreSQL и FastAPI.

### 4. Откройте приложение

После запуска Backend будет доступен по адресу:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

Через Swagger UI можно выполнять запросы, проверять работу API, регистрировать пользователей и авторизовываться.

### 5. Остановка проекта

Для остановки контейнеров выполните:

```bash
docker compose down
```

Данные PostgreSQL сохраняются в Docker Volume и не удаляются при обычной остановке контейнеров.

Для повторного запуска достаточно выполнить:

```bash
docker compose up -d
```

## 💻 Альтернативный запуск без Docker

Если Docker не установлен, проект можно запустить вручную.

Для этого потребуется Python 3 и установленный PostgreSQL.

### macOS

Откройте Terminal и перейдите в папку проекта:

```bash
cd Movie-Library/backend
```

Создайте виртуальное окружение:

```bash
python3 -m venv venv
```

Активируйте его:

```bash
source venv/bin/activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

Создайте файл `.env` на основе `.env.example` и укажите параметры подключения к PostgreSQL.

Пример настроек:

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=kinoteka
DB_USER=postgres
DB_PASSWORD=your_password
JWT_SECRET_KEY=your_secret_key
```

Запустите сервер:

```bash
uvicorn app.main:app --reload
```

### Windows

Откройте PowerShell и перейдите в папку проекта:

```powershell
cd Movie-Library\backend
```

Создайте виртуальное окружение:

```powershell
python -m venv venv
```

Активируйте его:

```powershell
.\venv\Scripts\Activate.ps1
```

Если PowerShell запрещает запуск скриптов, выполните:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Затем повторите активацию виртуального окружения.

Установите зависимости:

```powershell
pip install -r requirements.txt
```

Создайте файл `.env` на основе `.env.example` и настройте подключение к PostgreSQL.

Запустите сервер:

```powershell
uvicorn app.main:app --reload
```

Если команда `python` не распознаётся, попробуйте использовать `py`.

## 🔐 Авторизация

В проекте реализована JWT-авторизация.

### Регистрация пользователя

**POST** `/users/register`

Пример запроса:

```json
{
  "username": "test_user",
  "email": "test@example.com",
  "password": "TestPassword123"
}
```

### Вход в систему

**POST** `/users/login`

При успешной авторизации сервер возвращает:

- `access_token` — JWT-токен;
- `token_type` — тип токена (`bearer`).

### Получение текущего пользователя

**GET** `/users/me`

Для выполнения запроса необходимо передать JWT-токен в заголовке:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

В ответе возвращаются идентификатор, имя пользователя и электронная почта.

Пароль и его хеш клиенту не передаются.

## 📡 Основные API-маршруты

### Фильмы

| Метод | Endpoint | Описание |
|---|---|---|
| GET | `/movies` | Получение списка фильмов |
| GET | `/movies/{id}` | Получение фильма по ID |
| POST | `/movies` | Добавление фильма |
| PUT | `/movies/{id}` | Обновление фильма |
| DELETE | `/movies/{id}` | Удаление фильма |

### Жанры

| Метод | Endpoint | Описание |
|---|---|---|
| GET | `/genres` | Получение списка жанров |
| GET | `/genres/{id}` | Получение жанра по ID |
| POST | `/genres` | Добавление жанра |
| DELETE | `/genres/{id}` | Удаление жанра |

### Пользователи

| Метод | Endpoint | Описание |
|---|---|---|
| POST | `/users/register` | Регистрация |
| POST | `/users/login` | Авторизация |
| GET | `/users/me` | Информация о текущем пользователе |

## 🗄 База данных

В проекте используется PostgreSQL.

Предусмотрены следующие таблицы:

- `users` — пользователи;
- `movies` — фильмы;
- `genres` — жанры;
- `ratings` — оценки;
- `favorites` — избранное;
- `movie_genres` — связь фильмов и жанров.

Для взаимодействия с базой данных используется SQLAlchemy ORM.

## ⚙️ Переменные окружения

Настройки подключения к PostgreSQL и секретный ключ JWT хранятся в файле `.env`.

Файл `.env` не должен попадать в GitHub.

Для примера настроек предусмотрен `.env.example`.

Не используйте тестовые секреты и пароли в производственной среде.

## 🧪 Тестирование API

Для проверки API используется Swagger UI.

После запуска сервера откройте:

http://localhost:8000/docs

В Swagger можно:

1. Посмотреть все доступные маршруты.
2. Выполнить GET-запросы.
3. Создать и изменить записи.
4. Удалить записи.
5. Зарегистрировать пользователя.
6. Авторизоваться и получить JWT.
7. Проверить доступ к защищённым маршрутам.