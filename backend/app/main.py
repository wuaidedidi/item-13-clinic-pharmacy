import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from app.api.auth import router as auth_router
from app.api.routes import router as business_router
from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine, wait_for_database
from app.core.exceptions import BusinessError
from app.core.logging import setup_logging
from app.core.response import failure
from app.core.security import hash_password
from app.services.common import ensure_demo_accounts, refresh_expiry_warnings

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(business_router)


@app.on_event("startup")
def on_startup() -> None:
    wait_for_database()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_demo_accounts(db, hash_password("123456"))
        refresh_expiry_warnings(db, settings.expiry_warning_days)
        logger.info("应用启动完成：%s", settings.app_name)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    logger.info("业务错误 %s %s：%s", request.method, request.url.path, exc.message)
    return failure(exc.code, exc.message)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    logger.info("参数校验失败 %s %s：%s", request.method, request.url.path, exc.errors())
    return failure(422, "提交信息不完整或格式不正确")


@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return failure(exc.detail.get("code", exc.status_code), exc.detail.get("message", "请求失败"))
    return failure(exc.status_code, str(exc.detail) if exc.detail else "请求失败")


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.warning("数据库约束错误 %s %s：%s", request.method, request.url.path, exc)
    return failure(400, "数据存在关联关系，无法完成该操作")


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("系统异常 %s %s", request.method, request.url.path)
    return failure(500, "服务器错误，请稍后重试", status_code=500)
