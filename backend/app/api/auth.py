from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import BusinessError
from app.core.response import success
from app.core.security import verify_password
from app.dependencies import get_current_user
from app.models import User
from app.schemas import LoginRequest, LoginResponse, PasswordChangeRequest, ProfileUpdateRequest, RegisterRequest, UserOut
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.login(db, payload)
    token = auth_service.create_token(user)
    return success(LoginResponse(access_token=token, user=UserOut.model_validate(user)), "登录成功")


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register(db, payload)
    return success(UserOut.model_validate(user), "注册成功")


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return success(UserOut.model_validate(current_user))


@router.put("/profile")
def update_profile(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = auth_service.update_profile(current_user, payload)
    db.commit()
    db.refresh(user)
    return success(UserOut.model_validate(user), "个人资料已更新")


@router.put("/password")
def change_password(
    payload: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    auth_service.change_password(current_user, payload.old_password, payload.new_password)
    db.commit()
    return success(None, "密码已更新")
