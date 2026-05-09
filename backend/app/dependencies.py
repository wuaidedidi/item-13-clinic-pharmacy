from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import decode_token
from app.models import User

settings = get_settings()


def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=200, detail={"code": 401, "message": "登录已过期，请重新登录"})
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token, settings.secret_key)
        user_id = int(payload.get("sub"))
    except Exception as exc:
        raise HTTPException(status_code=200, detail={"code": 401, "message": "登录已过期，请重新登录"}) from exc
    user = db.get(User, user_id)
    if not user or user.status != "enabled":
        raise HTTPException(status_code=200, detail={"code": 401, "message": "登录已过期，请重新登录"})
    return user


def require_roles(*roles: str):
    def wrapper(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles and current_user.role != "admin":
            raise HTTPException(status_code=200, detail={"code": 403, "message": "无权访问该功能"})
        return current_user

    return wrapper
