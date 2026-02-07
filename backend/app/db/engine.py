import os
from collections.abc import AsyncGenerator
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Create a backend/.env file with your Neon connection string."
    )

# Parse URL and remove sslmode/channel_binding from query string
# asyncpg requires these via connect_args, not URL params
parsed = urlparse(DATABASE_URL)
query_params = parse_qs(parsed.query)
query_params.pop("sslmode", None)
query_params.pop("channel_binding", None)
clean_query = urlencode(query_params, doseq=True)
clean_url = urlunparse((
    parsed.scheme,
    parsed.netloc,
    parsed.path,
    parsed.params,
    clean_query,
    parsed.fragment
))

engine = create_async_engine(
    clean_url,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    connect_args={
        "ssl": "require",
    },
)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
