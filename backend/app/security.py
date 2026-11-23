import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Хеширование пароля
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# Проверка пароля
def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def _get_jwt_secret_key() -> str:
    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY environment variable is not set")
    return secret_key


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        _get_jwt_secret_key(),
        algorithm="HS256",
    )


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        _get_jwt_secret_key(),
        algorithms=["HS256"],
    )