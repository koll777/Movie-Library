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

**Пока не реализованы:** подключение Frontend к API, отдельные API-маршруты для оценок и избранного, пагинация.

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
├── install.py
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
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   ├── js/app.js
│   └── images/
├── docker-compose.yml
├── .env
├── .env.example
└── README.md
```

Файлы `.env` содержат настройки и секреты. Их не следует добавлять в GitHub или отправлять другим людям.

## Frontend — дизайн-прототип

В `frontend/` находится адаптивный интерфейс Cinema Premium на HTML, CSS и JavaScript без сборщика. Интерфейс подключён к реальному FastAPI Backend: используются каталог и жанры, JWT-регистрация и вход, профиль и смена пароля, избранное и личные оценки.

Обычный запуск всего проекта выполняется установщиком из корневой папки:

```bash
python3 install.py
```

На Windows:

```powershell
py -3 install.py
```

Установщик запускает Docker Desktop при необходимости, создаёт настройки, базы и frontend/backend-сервисы. После запуска откройте <http://127.0.0.1:5500>.

## Требования

Для запуска через Docker нужны:

- Git;
- Docker Desktop с установленным Docker Compose;
- Python 3.9 или новее для установщика;
- доступ к GitHub для клонирования репозитория.

## Настройка перед первым запуском

### 1. Скачать проект

Откройте терминал (macOS/Linux) или PowerShell (Windows) и выполните:

```bash
git clone https://github.com/koll777/Movie-Library.git
cd Movie-Library
```

### 2. Установить и запустить проект

Из корневой папки проекта запустите один установщик. Он подготовит и запустит приложение полностью:

- запустит Docker Desktop, если он ещё не запущен;
- запросит пароль PostgreSQL при первом запуске;
- создаст `.env` и сгенерирует JWT-секрет;
- проверит Docker Compose и создаст Docker Volume;
- запустит PostgreSQL;
- синхронизирует пароль базы с `.env`;
- соберёт и запустит backend;
- запустит frontend-сервер;
- откроет приложение в браузере.

**macOS / Linux:**

```bash
python3 install.py
```

**Windows PowerShell:**

```powershell
py -3 install.py
```

Запускайте команду из корневой папки проекта, где находится `install.py`. При первом запуске установщик попросит придумать и подтвердить пароль PostgreSQL длиной не менее 10 символов. При вводе пароль **не отображается** в консоли — это нормально.

Установщик создаёт `.env` с параметрами:

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=kinoteka
DB_USER=postgres
POSTGRES_PASSWORD=<введённый пароль>
JWT_SECRET_KEY=<сгенерированный секрет>
```

Не публикуйте `.env`, пароль PostgreSQL или JWT-секрет. Файл `backend/.env` не используется.

## Запуск через Docker

Повторный запуск установщика обновит backend и запустит отсутствующие сервисы:

```bash
python3 install.py
```
При запуске Backend автоматически создаёт отсутствующие таблицы в PostgreSQL.

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
| PUT | `/users/me/password` | Смена пароля текущего пользователя (требуется JWT) |

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

Для смены пароля выполните `PUT /users/me/password` с JWT и JSON-телом:

```json
{
  "current_password": "текущий_пароль",
  "new_password": "новый_пароль_от_8_до_128_символов"
}
```

Новый пароль должен содержать от 8 до 128 символов и отличаться от текущего.

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

Frontend-сервер запускается установщиком в отдельном процессе. На macOS остановить его можно так:

```bash
lsof -nP -iTCP:5500 -sTCP:LISTEN
kill <PID>
```

**Не используйте `docker compose down -v` и не удаляйте Volume `kinoteka_postgres_data`, если хотите сохранить данные PostgreSQL.**

## Полное удаление

Удалить всё, что создал установщик проекта, можно одним скриптом:

```bash
python3 uninstall.py
```

На Windows:

```powershell
py -3 uninstall.py
```

Для удаления без интерактивного подтверждения:

```bash
python3 uninstall.py --yes
```

Удалитель останавливает frontend-сервер проекта, удаляет контейнеры и сеть Docker Compose, удаляет persistent Volume `kinoteka_postgres_data`, локальный Docker-образ backend и файлы `.env`, `frontend.log`, `frontend.pid`. Исходники проекта остаются.

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
