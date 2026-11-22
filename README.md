# Кинотека (Movie Library)

Учебное клиент-серверный проект для просмотра и управления каталогом фильмов. На текущем этапе реализована серверная часть на **Python/FastAPI** с базой данных **PostgreSQL**. Backend и база данных запускаются через **Docker Compose**.

## Содержание

- [Возможности](#возможности)
- [Технологии](#технологии)
- [Структура проекта](#структура-проекта)
- [Требования](#требования)
- [Настройка перед первым запуском](#настройка-перед-первым-запуском)
- [Запуск через Docker](#запуск-через-docker)
- [Проверка работы](#проверка-работы)
- [API](#api)
- [Авторизация](#авторизация)
- [Остановка проекта](#остановка-проекта)
- [Запуск Backend без Docker](#запуск-backend-без-docker)
- [Важно о данных базы](#важно-о-данных-базы)

## Возможности

В текущей версии Backend реализованы:

- получение списка фильмов и фильма по ID;
- создание, изменение и удаление фильмов;
- получение списка жанров и жанра по ID;
- создание и удаление жанров;
- регистрация пользователя;
- вход пользователя по email и паролю;
- выдача JWT-токена;
- получение профиля текущего пользователя по JWT-токену;
- проверка подключения к PostgreSQL.

Пароли пользователей сохраняются в виде хеша Argon2, а не в открытом виде.

**Пока не реализованы:** пользовательский Frontend, отдельные API-маршруты для оценок и избранного, поиск и фильтрация фильмов, пагинация.

## Технологии

- Python 3.12
- FastAPI
- Uvicorn
- PostgreSQL 18
- SQLAlchemy
- Alembic
- Pydantic
- JWT (Bearer authentication)
- Argon2
- Docker и Docker Compose
- Swagger UI

## Структура проекта

```text
Movie-Library/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   ├── seed.py
│   │   └── ...
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env
├── .env.example
└── README.md
```

Файлы `.env` содержат настройки и секреты. Их не следует добавлять в GitHub или отправлять другим людям.

## Требования

Для запуска через Docker нужны:

- Git;
- Docker Desktop с установленным Docker Compose;
- доступ к GitHub для клонирования репозитория.

## Настройка перед первым запуском

### 1. Скачать проект

Откройте терминал (macOS/Linux) или PowerShell (Windows) и выполните:

```bash
git clone https://github.com/koll777/Movie-Library.git
cd Movie-Library
```

### 2. Создать единый файл настроек

**macOS / Linux:**

```bash
cp .env.example .env
```

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

Откройте корневой `.env` и задайте собственные значения:

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=kinoteka
DB_USER=postgres
POSTGRES_PASSWORD=ВАШ_НАДЁЖНЫЙ_ПАРОЛЬ
JWT_SECRET_KEY=ВАШ_ДЛИННЫЙ_СЛУЧАЙНЫЙ_СЕКРЕТ
```

Для Docker Compose адрес базы внутри контейнера будет автоматически заменён на `db:5432`. При локальном запуске Backend используются указанные в `.env` `localhost:5433`. Для обоих способов пароль PostgreSQL задаётся один раз через `POSTGRES_PASSWORD`. Не публикуйте реальные пароли и JWT-ключ.

> Если корневой `.env` уже существует, не перезаписывайте его автоматически: добавьте или проверьте необходимые переменные. Файл `backend/.env` больше не используется.

## Запуск через Docker

Перед запуском убедитесь, что Docker Desktop запущен.

Из корневой папки проекта выполните:

```bash
docker volume create kinoteka_postgres_data
docker compose config --quiet
docker compose up --build -d
```

Первая команда создаёт постоянный Docker Volume для базы данных. Если Volume уже существует, Docker оставит его без изменений. Вторая команда проверяет конфигурацию, третья собирает Backend-образ и запускает оба сервиса.

Проверить состояние контейнеров:

```bash
docker compose ps
```

Контейнер базы данных должен перейти в состояние `healthy`, а Backend — быть запущен.

Посмотреть логи Backend:

```bash
docker compose logs backend
```

Посмотреть логи базы данных:

```bash
docker compose logs db
```

## Проверка работы

После запуска откройте в браузере:

| Назначение | Адрес |
|---|---|
| Swagger UI | http://127.0.0.1:8000/docs |
| OpenAPI JSON | http://127.0.0.1:8000/openapi.json |
| Корневой маршрут | http://127.0.0.1:8000/ |
| Проверка PostgreSQL | http://127.0.0.1:8000/db-check |

В Swagger UI можно раскрывать маршруты, указывать данные запросов и нажимать **Try it out** для проверки API.

Успешная проверка `/db-check` возвращает сообщение:

```json
{
  "message": "PostgreSQL подключен успешно!"
}
```

Если браузер показывает `{"detail":"Not Found"}`, проверьте, что адрес введён точно: `http://127.0.0.1:8000/docs` — без лишних символов после `docs`.

## API

Базовый адрес Backend:

```text
http://127.0.0.1:8000
```

### Фильмы

| Метод | Endpoint | Назначение |
|---|---|---|
| GET | `/movies` | Получить список фильмов |
| GET | `/movies/{movie_id}` | Получить фильм по ID |
| POST | `/movies` | Создать фильм |
| PUT | `/movies/{movie_id}` | Обновить фильм |
| DELETE | `/movies/{movie_id}` | Удалить фильм |

Для создания фильма пример тела запроса:

```json
{
  "title": "Пример фильма",
  "description": "Описание фильма",
  "release_year": 2024,
  "director": "Имя режиссёра",
  "poster_url": "https://example.com/poster.jpg",
  "genre_ids": [1]
}
```

Фактическая схема запроса отображается в Swagger UI.

### Жанры

| Метод | Endpoint | Назначение |
|---|---|---|
| GET | `/genres` | Получить список жанров |
| GET | `/genres/{genre_id}` | Получить жанр по ID |
| POST | `/genres` | Создать жанр |
| DELETE | `/genres/{genre_id}` | Удалить жанр |

### Пользователи

| Метод | Endpoint | Назначение |
|---|---|---|
| POST | `/users/register` | Регистрация |
| POST | `/users/login` | Вход и получение JWT |
| GET | `/users/me` | Профиль текущего пользователя |

### Служебные маршруты

| Метод | Endpoint | Назначение |
|---|---|---|
| GET | `/` | Проверка доступности Backend |
| GET | `/db-check` | Проверка соединения с PostgreSQL |

## Авторизация

1. В Swagger UI выполните `POST /users/register`, передав имя пользователя, email и пароль.
2. Выполните `POST /users/login` с теми же email и паролем.
3. Скопируйте значение `access_token` из ответа.
4. Нажмите **Authorize** в Swagger UI.
5. Введите токен в формате `Bearer ВАШ_ACCESS_TOKEN` (если Swagger показывает поле для самого Bearer-токена, следуйте подсказке интерфейса).
6. Выполните `GET /users/me`.

При успешной авторизации сервер вернёт данные пользователя. Хеш пароля в ответ не включается.

## Остановка проекта

Чтобы остановить контейнеры, не удаляя данные базы:

```bash
docker compose stop
```

Чтобы снова запустить уже созданные контейнеры:

```bash
docker compose start
```

Чтобы остановить и удалить контейнеры и сеть Compose, сохранив постоянный Volume базы данных:

```bash
docker compose down
```

**Не используйте `docker compose down -v` и не удаляйте Volume `kinoteka_postgres_data`, если хотите сохранить данные PostgreSQL.**

## Запуск Backend без Docker

Этот способ предназначен для локального запуска Python-приложения. Для него PostgreSQL должен быть доступен с компьютера, а параметры подключения в `backend/.env` должны указывать на локальный адрес и опубликованный порт базы:

```env
DB_HOST=localhost
DB_PORT=5433
```

Параметры `DB_NAME`, `DB_USER`, `POSTGRES_PASSWORD` и `JWT_SECRET_KEY` берутся из корневого `.env`. Отдельный `backend/.env` не нужен.

Из корневой папки проекта:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Для Windows PowerShell активация виртуального окружения:

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

После запуска документация API будет доступна по адресу http://127.0.0.1:8000/docs.

При локальном запуске Backend контейнер PostgreSQL должен быть запущен. Если порт `5433` занят другим процессом или контейнером, сначала необходимо разобраться, какой сервис его использует, а не удалять контейнер или Volume с данными.

## Важно о данных базы

PostgreSQL хранит данные в Docker Volume `kinoteka_postgres_data`. Контейнер можно пересоздать, не удаляя Volume: данные останутся в нём.

- Не удаляйте Volume, если в базе есть нужные данные.
- Не используйте `docker compose down -v` для обычной остановки проекта.
- Не меняйте пароль существующей базы простым изменением `.env`: переменная `POSTGRES_PASSWORD` применяется при первоначальной инициализации хранилища и сама по себе не меняет пароль уже созданного пользователя PostgreSQL.
- Для подключения Backend к БД внутри Compose используются `DB_HOST=db` и `DB_PORT=5432`; для локального запуска Python на компьютере — `DB_HOST=localhost` и `DB_PORT=5433`.

---

**Репозиторий:** https://github.com/koll777/Movie-Library
