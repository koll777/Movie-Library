#!/usr/bin/env python3

import getpass
import os
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"
REQUIRED_ENV_VARS = (
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "POSTGRES_PASSWORD",
    "JWT_SECRET_KEY",
)
DEFAULT_ENV_VALUES = {
    "DB_HOST": "localhost",
    "DB_PORT": "5433",
    "DB_NAME": "kinoteka",
    "DB_USER": "postgres",
}


class SetupError(Exception):
    pass


def _quote_env_value(value: str) -> str:
    escaped_value = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped_value}'"


def _format_env_entry(key: str, value: str) -> str:
    if key in ("POSTGRES_PASSWORD", "JWT_SECRET_KEY"):
        value = _quote_env_value(value)
    return f"{key}={value}\n"


def _write_new_env_file(path: Path, values: dict[str, str]) -> None:
    contents = "".join(_format_env_entry(key, value) for key, value in values.items())
    created = False
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        created = True
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as env_file:
            env_file.write(contents)
            env_file.flush()
            os.fsync(env_file.fileno())
    except OSError:
        if created and path.exists():
            path.unlink()
        raise


def _update_existing_env(path: Path, values: dict[str, str]) -> None:
    try:
        original_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    except (OSError, UnicodeError) as error:
        raise SetupError("Не удалось прочитать существующий .env.") from error

    lines_by_key = {}
    for index, line in enumerate(original_lines):
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#") or "=" not in stripped_line:
            continue
        key = stripped_line.split("=", 1)[0].strip()
        if key in values:
            lines_by_key.setdefault(key, []).append(index)

    duplicates = [key for key, indexes in lines_by_key.items() if len(indexes) > 1]
    if duplicates:
        raise SetupError(
            "В существующем .env повторяются параметры "
            f"{', '.join(duplicates)}. Исправьте дубликаты и запустите установщик снова."
        )

    replacement_lines = {}
    for key, value in values.items():
        indexes = lines_by_key.get(key)
        if indexes:
            replacement_lines[indexes[0]] = _format_env_entry(key, value)
        else:
            if original_lines and not original_lines[-1].endswith(("\n", "\r")):
                original_lines[-1] += "\n"
            original_lines.append(_format_env_entry(key, value))

    updated_lines = [
        replacement_lines.get(index, line)
        for index, line in enumerate(original_lines)
    ]
    temporary_path = None
    try:
        descriptor, temporary_path = tempfile.mkstemp(
            prefix=".env.", suffix=".tmp", dir=path.parent
        )
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as env_file:
            env_file.writelines(updated_lines)
            env_file.flush()
            os.fsync(env_file.fileno())
        if os.name != "nt":
            os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, path)
    except OSError as error:
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except OSError:
                pass
        raise SetupError("Не удалось обновить настройки в корневом .env.") from error


def _read_env_values(path: Path) -> tuple[dict[str, str], set[str]]:
    values = {}
    present = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in present and key in REQUIRED_ENV_VARS:
            raise SetupError(f"В существующем .env повторяется параметр {key}.")
        present.add(key)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        values[key] = value
    return values, present


def _prepare_env_file(path: Path) -> bool:
    was_existing = path.exists()
    if was_existing:
        try:
            existing_values, present_keys = _read_env_values(path)
        except (OSError, UnicodeError) as error:
            raise SetupError("Не удалось прочитать существующий .env.") from error
    else:
        existing_values, present_keys = {}, set()

    values_to_set = {}
    for key, default in DEFAULT_ENV_VALUES.items():
        existing_value = existing_values.get(key, "")
        if key not in present_keys or not existing_value:
            values_to_set[key] = default

    for key in ("POSTGRES_PASSWORD", "JWT_SECRET_KEY"):
        existing_value = existing_values.get(key, "")
        if key in present_keys and (
            not existing_value or existing_value.startswith("replace_with_")
        ):
            values_to_set[key] = ""
        elif key not in present_keys:
            values_to_set[key] = ""

    if not values_to_set:
        return False

    if "POSTGRES_PASSWORD" in values_to_set:
        values_to_set["POSTGRES_PASSWORD"] = _ask_database_password()
    if "JWT_SECRET_KEY" in values_to_set:
        values_to_set["JWT_SECRET_KEY"] = secrets.token_urlsafe(48)

    if was_existing:
        _update_existing_env(path, values_to_set)
    else:
        ordered_values = {
            **DEFAULT_ENV_VALUES,
            "POSTGRES_PASSWORD": values_to_set["POSTGRES_PASSWORD"],
            "JWT_SECRET_KEY": values_to_set["JWT_SECRET_KEY"],
        }
        try:
            _write_new_env_file(path, ordered_values)
        except FileExistsError as error:
            raise SetupError(
                "Файл .env появился во время установки; он не был перезаписан."
            ) from error
        except OSError as error:
            raise SetupError("Не удалось безопасно создать корневой .env.") from error
    return True


def _ask_database_password() -> str:
    print("Введите пароль PostgreSQL. Ввод пароля не отображается на экране.")
    while True:
        password = getpass.getpass("Придумайте пароль для PostgreSQL (минимум 10 символов): ")
        if len(password) < 10:
            print("Пароль должен содержать не менее 10 символов.")
            continue
        if "\n" in password or "\r" in password:
            print("Пароль не должен содержать символы переноса строки.")
            continue

        confirmation = getpass.getpass("Повторите пароль: ")
        if password != confirmation:
            print("Пароли не совпали, попробуйте ещё раз.")
            continue
        return password


def _run(command: list[str], error_message: str) -> None:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError as error:
        raise SetupError(error_message) from error
    if result.returncode != 0:
        raise SetupError(error_message)


def main() -> int:
    try:
        print("Проверяю подключение к Docker Desktop...", flush=True)
        _run(
            ["docker", "info"],
            "Docker недоступен. Запустите Docker Desktop и повторите установку.",
        )

        env_exists = ENV_FILE.exists()
        print("Проверяю настройки проекта...", flush=True)
        env_changed = _prepare_env_file(ENV_FILE)
        if env_changed and env_exists:
            print("Добавлены недостающие настройки; существующие значения сохранены.")
        elif env_changed:
            print("Создан корневой .env; JWT-секрет сгенерирован.")
        else:
            print("Корневой .env уже настроен; оставляю его без изменений.")

        print("Проверяю Docker Compose...", flush=True)
        _run(
            ["docker", "compose", "config", "--quiet"],
            "Не удалось проверить Docker Compose. Проверьте конфигурацию проекта.",
        )
        print("Подготавливаю хранилище базы данных...", flush=True)
        _run(
            ["docker", "volume", "create", "kinoteka_postgres_data"],
            "Не удалось создать Docker Volume для базы данных.",
        )
    except SetupError as error:
        print(f"Ошибка установки: {error}", file=sys.stderr)
        return 1

    print("Настройка завершена; приложение ещё не запущено.")
    print("Из корневой папки проекта выполните:")
    print("  docker compose up --build -d")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
