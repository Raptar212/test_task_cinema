from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from auth.security import (
    generate_session_token,
    hash_password,
    is_token_expired,
    session_expires_at,
    verify_password,
)


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


async def register_user(db: AsyncSession, email: str, password: str) -> User:
    existing = await db.scalar(select(User).where(User.email == email))
    if existing:
        raise AuthError("Email already registered", 409)

    user = User(
        email=email,
        password_hash=hash_password(password),
        role="viewer",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, email: str, password: str) -> str:
    user = await db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        raise AuthError("Invalid email or password", 401)

    token = generate_session_token()
    user.session_token = token
    user.session_expires_at = session_expires_at()
    await db.commit()
    return token


async def logout_user(db: AsyncSession, user: User) -> None:
    user.session_token = None
    user.session_expires_at = None
    await db.commit()


async def get_user_by_token(db: AsyncSession, token: str) -> User:
    user = await db.scalar(select(User).where(User.session_token == token))
    if not user or is_token_expired(user.session_expires_at):
        raise AuthError("Invalid or expired session", 401)
    return user