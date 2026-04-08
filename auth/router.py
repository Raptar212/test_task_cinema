from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.models import User, get_db
from auth.schemas import (
    LoginRequest, LoginResponse,
    MeResponse,
    RegisterRequest, RegisterResponse,
)
from auth.service import AuthError, login_user, logout_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await register_user(db, body.email, body.password)
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    return RegisterResponse(message="Registration successful.", email=user.email)


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        token = await login_user(db, body.email, body.password)
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    user = await db.scalar(select(User).where(User.session_token == token))
    return LoginResponse(token=token, role=user.role)


@router.post("/logout", status_code=204)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await logout_user(db, current_user)


@router.get("/me", response_model=MeResponse)
async def me(current_user: User = Depends(get_current_user)):
    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
    )
