from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import settings

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

async_session = async_sessionmaker(bind=engine)
