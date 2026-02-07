# Voyager AI - Backend

The backend API for Voyager AI, built with FastAPI and PostgreSQL (Neon).

## Tech Stack

- **Framework**: FastAPI 0.115+
- **Language**: Python 3.11+
- **Database**: PostgreSQL (Neon serverless)
- **ORM**: SQLAlchemy 2.0 (async)
- **Database Driver**: asyncpg
- **Migrations**: Alembic
- **Testing**: pytest + pytest-asyncio + httpx
- **Environment**: python-dotenv
- **Agent Framework**: LangGraph (to be integrated)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (comes with Python)
- Neon PostgreSQL database account ([Sign up free](https://console.neon.tech/))

### Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

1. Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

2. Get your Neon connection string:
   - Go to [Neon Console](https://console.neon.tech/)
   - Select your project → Connection Details
   - Copy the connection string
   - **Important**: Change `postgresql://` to `postgresql+asyncpg://`

3. Update `.env`:

```env
# Neon PostgreSQL connection string (REQUIRED)
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.neon.tech/neondb?sslmode=require

# Server
HOST=0.0.0.0
PORT=8000

# LLM Provider (for future use)
# OPENAI_API_KEY=sk-...
# LLM_MODEL=gpt-4o-mini
```

### Running the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Project Structure

```
backend/
├── app/
│   ├── db/                      # Database layer
│   │   ├── models.py           # SQLAlchemy ORM models
│   │   ├── crud.py             # CRUD operations
│   │   ├── engine.py           # Database engine & sessions
│   │   └── seed.py             # Database seeding
│   │
│   ├── models/                  # Pydantic schemas
│   │   └── schemas.py          # Request/response models
│   │
│   ├── routers/                 # API endpoints
│   │   ├── health.py           # Health check
│   │   ├── conversations.py    # Conversation management
│   │   └── chat.py             # Chat streaming
│   │
│   └── main.py                  # FastAPI app
│
├── tests/                       # pytest tests
│   ├── conftest.py             # Test fixtures
│   ├── test_conversations.py   # Conversation endpoint tests
│   └── test_crud.py            # Database CRUD tests
│
├── alembic/                     # Database migrations
│   ├── versions/               # Migration scripts
│   └── env.py                  # Alembic configuration
│
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

## Database

### Schema

#### Conversations Table

```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) DEFAULT 'New conversation',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversations_updated_at ON conversations(updated_at);
```

#### Messages Table

```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL,
  content TEXT DEFAULT '',
  tool_results JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
```

### Database Migrations

The app creates tables automatically on first startup via `Base.metadata.create_all()` in the lifespan event.

For schema changes, use Alembic:

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

### Database Seeding

On first startup, the app automatically seeds a welcome conversation if the database is empty. See `app/db/seed.py`.

To manually seed:

```python
from app.db.engine import async_session
from app.db.seed import seed_welcome_conversation

async with async_session() as session:
    await seed_welcome_conversation(session)
    await session.commit()
```

## API Endpoints

### Health Check

```http
GET /health
```

Returns server health status.

### Conversations

```http
GET /api/conversations
```
List all conversations (ordered by `updated_at` DESC).

```http
POST /api/conversations
Content-Type: application/json

{
  "title": "Trip to Paris"  // optional
}
```
Create a new conversation.

```http
GET /api/conversations/{conversation_id}
```
Get a single conversation by ID.

```http
PATCH /api/conversations/{conversation_id}
Content-Type: application/json

{
  "title": "Updated Title"
}
```
Update conversation title.

```http
DELETE /api/conversations/{conversation_id}
```
Delete a conversation (cascades to messages).

```http
GET /api/conversations/{conversation_id}/messages
```
Get all messages for a conversation.

### Chat Streaming

```http
POST /api/chat/stream
Content-Type: application/json

{
  "conversationId": "uuid-here",
  "message": "Find me flights to Tokyo"
}
```

Returns a Server-Sent Events (SSE) stream with:
- `token`: Incremental text chunks
- `tool_result`: Tool execution results
- `complete`: Final message with full content and tool results
- `error`: Error messages

Example response:

```
event: token
data: {"content": "I'll"}

event: token
data: {"content": " search"}

event: tool_result
data: {"type": "flight", "data": {...}}

event: complete
data: {"content": "I'll search for flights...", "toolResults": [...]}
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_conversations.py

# Run with coverage
pytest --cov=app

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Test Structure

- **conftest.py**: Shared fixtures (test database, test client)
- **test_conversations.py**: API endpoint tests (5 tests)
- **test_crud.py**: Database CRUD tests (4 tests)

### Test Database

Tests use an in-memory SQLite database for speed and isolation:

```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

Each test gets a fresh database with tables created and dropped automatically.

### Example Test

```python
@pytest.mark.asyncio
async def test_create_conversation(test_client: AsyncClient):
    response = await test_client.post(
        "/api/conversations",
        json={"title": "My Trip to Paris"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My Trip to Paris"
    assert "id" in data
```

## CRUD Operations

All database operations are in `app/db/crud.py`:

```python
from app.db import crud

# List conversations (ordered by updated_at DESC)
conversations = await crud.list_conversations(db)

# Get single conversation
conversation = await crud.get_conversation(db, conversation_id)

# Create conversation
conversation = await crud.create_conversation(db, title="Trip to Paris")

# Update conversation
conversation = await crud.update_conversation(db, conversation_id, "New Title")

# Delete conversation
deleted = await crud.delete_conversation(db, conversation_id)

# Get messages
messages = await crud.get_messages(db, conversation_id)

# Add message
message = await crud.add_message(
    db,
    conv_id=conversation_id,
    role="user",
    content="Hello!",
    tool_results=None,
)
```

## Pydantic Schemas

Request/response models in `app/models/schemas.py`:

```python
class Conversation(BaseModel):
    id: str
    title: str
    createdAt: str
    updatedAt: str

class Message(BaseModel):
    id: Optional[str] = None
    role: str
    content: str
    toolResults: Optional[list] = None
    timestamp: str

class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New conversation"

class UpdateConversationRequest(BaseModel):
    title: str
```

## CORS Configuration

The API allows requests from the frontend dev server:

```python
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
```

For production, update `allow_origins` with your frontend domain.

## Adding New Endpoints

1. Create a new router in `app/routers/`:

```python
# app/routers/my_feature.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/my-feature")

@router.get("")
async def get_my_feature():
    return {"message": "Hello from my feature"}
```

2. Register the router in `app/main.py`:

```python
from app.routers import my_feature

app.include_router(my_feature.router)
```

## Common Tasks

### Connect to Neon Database Directly

```bash
# Install psql if not already installed
# Then connect using your connection string
psql "postgresql://user:password@ep-xxx.neon.tech/neondb?sslmode=require"
```

### Reset Database

```bash
# Drop all tables and recreate
alembic downgrade base
alembic upgrade head

# Or manually in Neon Console → SQL Editor
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
```

Then restart the server to recreate tables.

### View Database Schema

```sql
-- List all tables
\dt

-- Describe conversations table
\d conversations

-- Describe messages table
\d messages

-- View indexes
\di
```

### Enable SQL Echo (Debug Mode)

In `app/db/engine.py`:

```python
engine = create_async_engine(
    clean_url,
    echo=True,  # Enable SQL logging
    ...
)
```

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ Yes | - |
| `HOST` | Server host | ❌ No | `0.0.0.0` |
| `PORT` | Server port | ❌ No | `8000` |
| `OPENAI_API_KEY` | OpenAI API key (future) | ❌ No | - |
| `LLM_MODEL` | LLM model name (future) | ❌ No | - |

## Troubleshooting

### Connection Errors

**Error**: `RuntimeError: DATABASE_URL environment variable is not set`

**Solution**: Create a `.env` file with your Neon connection string.

---

**Error**: `TypeError: connect() got an unexpected keyword argument 'sslmode'`

**Solution**: Make sure your `DATABASE_URL` uses `postgresql+asyncpg://` (not `postgresql://`). The app automatically strips `sslmode` from the URL and passes it via `connect_args`.

---

**Error**: `asyncpg.exceptions.DataError: can't subtract offset-naive and offset-aware datetimes`

**Solution**: This is already fixed in `app/db/models.py` using `PG_TIMESTAMP(timezone=True)`.

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # On Mac/Linux
netstat -ano | findstr :8000  # On Windows

# Kill the process
kill -9 <PID>  # On Mac/Linux
taskkill /PID <PID> /F  # On Windows
```

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade --force-reinstall -r requirements.txt
```

## Performance

### Connection Pooling

The app uses connection pooling for efficiency:

```python
engine = create_async_engine(
    clean_url,
    pool_size=5,        # Max 5 connections in pool
    max_overflow=10,    # Max 10 overflow connections
    pool_pre_ping=True, # Verify connections before use
)
```

### Database Indexes

- `idx_conversations_updated_at`: Speeds up conversation list queries
- `idx_messages_conversation_id`: Speeds up message lookups

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Neon Documentation](https://neon.tech/docs)
- [pytest Documentation](https://docs.pytest.org/)

---

**Backend built with FastAPI and PostgreSQL (Neon)**
