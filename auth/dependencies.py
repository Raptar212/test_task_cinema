from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User, get_db
from auth.service import AuthError, get_user_by_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    try:
        return await get_user_by_token(db, credentials.credentials)
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def require_viewer(user: User = Depends(get_current_user)) -> User:
    if user.role != "viewer":
        raise HTTPException(status_code=403, detail="Access denied")
    return user
