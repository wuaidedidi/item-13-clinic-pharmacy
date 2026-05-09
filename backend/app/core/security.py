from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.hash import pbkdf2_sha256


ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pbkdf2_sha256.verify(password, password_hash)


def create_access_token(subject: str, secret_key: str, expires_minutes: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, secret_key, algorithm=ALGORITHM)


def decode_token(token: str, secret_key: str) -> dict[str, Any]:
    return jwt.decode(token, secret_key, algorithms=[ALGORITHM])
