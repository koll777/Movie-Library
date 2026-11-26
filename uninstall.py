#!/usr/bin/env python3

import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"
FRONTEND_PID_FILE = ROOT / "frontend.pid"
FRONTEND_LOG_FILE = ROOT / "frontend.log"
VOLUME_NAME = "kinoteka_postgres_data"
BACKEND_IMAGE = "movie-library-backend"


def docker_is_available() -> bool:
    try:
        return (
            subprocess.run(
                ["docker", "info"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            ).returncode
            == 0
        )
    except OSError:
        return False


def is_project_frontend_process(pid: int) -> bool:
    try:
        if sys.platform.startswith("linux"):
            command = (
                Path(f"/proc/{pid}/cmdline")
                .read_bytes()
                .replace(b"\0", b" ")
                .decode("utf-8", errors="replace")
            )
            return "http.server" in command and "5500" in command

        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
        command = result.stdout.lower()
        return result.returncode == 0 and "http.server" in command and "5500" in command
    except (OSError, ValueError):
        return False


def stop_project_frontend() -> None:
    pid = None
    if FRONTEND_PID_FILE.exists():
        try:
            pid = int(FRONTEND_PID_FILE.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            pid = None

    if pid is not None and is_project_frontend_process(pid):
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Остановлен frontend-сервер (PID {pid}).")
        except (OSError, ProcessLookupError):
            pass
    elif sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["lsof", "-t", "-iTCP:5500", "-sTCP:LISTEN"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False,
            )
            for value in result.stdout.split():
                try:
                    port_pid = int(value)
                except ValueError:
                    continue
                if is_project_frontend_process(port_pid):
                    os.kill(port_pid, signal.SIGTERM)
                    print(f"Остановлен frontend-сервер (PID {port_pid}).")
        except (OSError, ProcessLookupError):
            pass

    FRONTEND_PID_FILE.unlink(missing_ok=True)


def remove_docker_resources() -> bool:
    if not docker_is_available():
        print("Docker Desktop недоступен; Docker-ресурсы пропущены.", file=sys.stderr)
        return False

    subprocess.run(
        ["docker", "compose", "down", "--rmi", "local", "--volumes"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )

    subprocess.run(
        ["docker", "volume", "rm", "-f", VOLUME_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )

    subprocess.run(
        ["docker", "rmi", "-f", BACKEND_IMAGE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return True


def remove_local_files() -> None:
    for path in (ENV_FILE, FRONTEND_LOG_FILE, FRONTEND_PID_FILE):
        try:
            path.unlink(missing_ok=True)
        except OSError as error:
            print(f"Не удалось удалить {path.name}: {error}", file=sys.stderr)


def confirm_removal() -> bool:
    answer = input(
        "Удалить контейнеры, базу, frontend и локальные настройки проекта? [д/Н]: "
    )
    return answer.strip().lower() in ("д", "да", "y", "yes")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Полностью удалить локальные ресурсы Movie Library"
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Удалить без подтверждения",
    )
    args = parser.parse_args()

    if not args.yes and not confirm_removal():
        print("Удаление отменено.")
        return 0

    print("Останавливаю frontend...")
    stop_project_frontend()

    print("Удаляю Docker-ресурсы...")
    remove_docker_resources()

    print("Удаляю локальные настройки...")
    remove_local_files()

    print("Удаление завершено.")
    print("Исходники проекта в папке репозитория не удалены.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
