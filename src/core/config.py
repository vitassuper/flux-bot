from typing import Any, Dict, Optional

from pydantic import PostgresDsn, validator, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG_MODE: bool

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator('SQLALCHEMY_DATABASE_URI', mode='before')
    def assemble_db_connection(cls, v: Optional[str], values: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=values.data.get('POSTGRES_USER'),
            password=values.data.get('POSTGRES_PASSWORD'),
            host=values.data.get('POSTGRES_SERVER'),
            path=values.data.get('POSTGRES_DB') or '',
        )

    CONNECTOR_SECRET: Optional[str] = None
    TELEGRAM_BOT_TOKEN: str

    API_PASSWORD: str
    TELEGRAM_CHAT_ID: str
    TELEGRAM_CHAT_ID2: str

    APP_KEY: str

    class Config:
        env_file = '.env'
        case_sensitive = True


settings = Settings()
