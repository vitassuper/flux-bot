from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.bot.models.base import Base
from src.bot.utils.helper import Helper


class Exchange(Base):
    __tablename__ = 'exchanges'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    api_key: Mapped[str] = mapped_column(String(255), nullable=False)
    api_secret: Mapped[str] = mapped_column(String(255), nullable=False)
    hedge: Mapped[bool] = mapped_column(Boolean(), nullable=True, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)

    def get_api_key(self):
        return Helper.decrypt_string(self.api_key)

    def get_api_secret(self) -> str:
        return Helper.decrypt_string(self.api_secret)

