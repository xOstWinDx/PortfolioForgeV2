from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import settings

engine = create_async_engine(settings.DB_URL)

DEFAULT_SESSION_FACTORY = async_sessionmaker(engine, expire_on_commit=False)
