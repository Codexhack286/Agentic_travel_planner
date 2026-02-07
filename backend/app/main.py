from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Load .env BEFORE any other app imports (so DATABASE_URL is available)
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.engine import engine, async_session
from app.db.models import Base
from app.db.seed import seed_welcome_conversation
from app.routers import health, conversations, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (safe — skips existing tables)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed welcome conversation for new users
    async with async_session() as session:
        await seed_welcome_conversation(session)
        await session.commit()

    yield
    # Dispose engine on shutdown
    await engine.dispose()


app = FastAPI(
    title="Voyager AI Backend",
    description="AI Travel Concierge API with Neon PostgreSQL",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(conversations.router)
app.include_router(chat.router)
