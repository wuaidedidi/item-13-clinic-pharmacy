from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import BusinessError
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas import LoginRequest, ProfileUpdateRequest, RegisterRequest

settings = get_settings()


def login(db: Session, payload: LoginRequest) -> User:
    user = db.query(User).filter(User.username == payload.username).one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise BusinessError(400, "用户名或密码错误")
    if user.status != "enabled":
        raise BusinessError(403, "账号已停用")
    return user


def register(db: Session, payload: RegisterRequest) -> User:
    exists = db.query(User).filter(User.username == payload.username).one_or_none()
    if exists:
        raise BusinessError(409, "用户名已存在")
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        nickname=payload.nickname,
        role="doctor",
        phone=payload.phone,
        email=payload.email,
        status="enabled",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_token(user: User) -> str:
    return create_access_token(str(user.id), settings.secret_key, settings.access_token_expire_minutes)


def update_profile(user: User, payload: ProfileUpdateRequest) -> User:
    user.nickname = payload.nickname
    user.phone = payload.phone
    user.email = payload.email
    return user


def change_password(user: User, old_password: str, new_password: str) -> None:
    if not verify_password(old_password, user.password_hash):
        raise BusinessError(400, "原密码不正确")
    user.password_hash = hash_password(new_password)
