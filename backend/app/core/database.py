import logging
import time

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

engine = create_engine(
    settings.sqlalchemy_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def wait_for_database(max_attempts: int = 30, interval_seconds: int = 2) -> None:
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("数据库连接成功，已完成第 %s 次探测", attempt)
            return
        except Exception as exc:  # pragma: no cover - startup guard
            last_error = exc
            logger.warning("等待数据库可用，第 %s/%s 次尝试失败：%s", attempt, max_attempts, exc)
            time.sleep(interval_seconds)
    raise RuntimeError("数据库在规定时间内未能就绪") from last_error


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
