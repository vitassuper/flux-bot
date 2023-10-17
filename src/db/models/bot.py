from datetime import datetime

from sqlalchemy import Boolean, String, DateTime, Integer, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base
from src.bot.types.bot_side_type import BotSideType


class Bot(Base):
    __tablename__ = "bots"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    api_key: Mapped[str] = mapped_column(String(255), nullable=False)
    api_secret: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
    copy_bot_id: Mapped[int] = mapped_column(Integer(), nullable=True)
    exchange_id: Mapped[int] = mapped_column(Integer(), nullable=True)
    side: Mapped[BotSideType] = mapped_column(SmallInteger(), nullable=True)
