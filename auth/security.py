import secrets
from datetime import datetime, timezone

from passlib.context import CryptContext

from auth.config import SESSION_TTL

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def generate_session_token() -> str:
    return secrets.token_hex(48)


def session_expires_at() -> datetime:
    return datetime.now(timezone.utc) + SESSION_TTL


def is_token_expired(expires_at: datetime | None) -> bool:
    if expires_at is None:
        return True
    return datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc)