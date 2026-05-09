from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    app_name: str = Field(default="诊所药房药品批次与效期预警系统", alias="APP_NAME")
    app_env: str = Field(default="production", alias="APP_ENV")
    secret_key: str = Field(default="change-me", alias="APP_SECRET_KEY")
    access_token_expire_minutes: int = Field(default=720, alias="APP_ACCESS_TOKEN_EXPIRE_MINUTES")
    database_host: str = Field(default="mysql", alias="DATABASE_HOST")
    database_port: int = Field(default=3306, alias="DATABASE_PORT")
    database_user: str = Field(default="clinic", alias="DATABASE_USER")
    database_password: str = Field(default="clinic123", alias="DATABASE_PASSWORD")
    database_name: str = Field(default="clinic_pharmacy", alias="DATABASE_NAME")
    database_charset: str = Field(default="utf8mb4", alias="DATABASE_CHARSET")
    expiry_warning_days: int = Field(default=90, alias="EXPIRY_WARNING_DAYS")

    @property
    def sqlalchemy_url(self) -> str:
        return (
            "mysql+pymysql://"
            f"{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
            f"?charset={self.database_charset}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
