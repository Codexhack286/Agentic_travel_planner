# Voyager AI - AI Travel Concierge

An intelligent travel planning assistant that helps users find flights, hotels, create itineraries, check weather, and more through natural conversation.

## Project Overview

**Voyager AI** is a collaborative project built by a 4-person team with zero budget. The application combines a modern chat interface with AI-powered travel planning capabilities, leveraging the LangGraph agent framework and multiple travel APIs.

### Team Structure

| Role | Responsibility | Status |
|------|---------------|--------|
| **Full-Stack Developer** | Frontend UI + Backend API + Database | ✅ **COMPLETE** |
| **Agent Architect** | LangGraph multi-agent system | 🚧 Pending |
| **API Integration Engineer** | 6 travel APIs (flights, hotels, weather, etc.) | 🚧 Pending |
| **DevOps & Quality Engineer** | Docker, CI/CD, production deployment | 🚧 Pending |

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: React Context + useReducer
- **API Communication**: Custom SSE streaming hook
- **Testing**: Vitest + React Testing Library

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL (Neon serverless)
- **ORM**: SQLAlchemy 2.0 (async)
- **Agent Framework**: LangGraph (to be integrated)
- **Testing**: pytest + pytest-asyncio

### Database
- **Provider**: Neon (serverless PostgreSQL)
- **Schema**: Conversations + Messages with UUID primary keys
- **Migrations**: Alembic

## Prerequisites

Before setting up the project, ensure you have:

- **Node.js**: v18.x or higher ([Download](https://nodejs.org/))
- **Python**: 3.11 or higher ([Download](https://www.python.org/))
- **Package Managers**: npm (comes with Node.js), pip (comes with Python)
- **Neon Account**: Free PostgreSQL database ([Sign up](https://console.neon.tech/))

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Agentic_travel_planner
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at **http://localhost:3000**

See [frontend/README.md](frontend/README.md) for detailed frontend documentation.

### 3. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your Neon DATABASE_URL
```

**Important**: Get your Neon connection string from [Neon Console](https://console.neon.tech/) → Connection Details, then update `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.neon.tech/neondb?sslmode=require
```

Start the backend server:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**

API docs: **http://localhost:8000/docs**

See [backend/README.md](backend/README.md) for detailed backend documentation.

### 4. Database Setup

The database tables are created automatically on first startup. A welcome conversation is seeded for new users.

To create a migration after schema changes:

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Running Tests

### Frontend Tests

```bash
cd frontend
npm test                 # Run all tests
npm test -- --coverage   # Run with coverage report
```

Current coverage: **25+ tests** across components, hooks, and utilities.

### Backend Tests

```bash
cd backend
pytest                   # Run all tests
pytest --cov=app         # Run with coverage report
```

Current coverage: **9+ tests** across API endpoints and CRUD operations.

## Project Structure

```
Agentic_travel_planner/
├── frontend/                 # Next.js 14 frontend
│   ├── app/                 # Next.js App Router pages
│   ├── components/          # React components
│   │   ├── chat/           # Chat interface components
│   │   ├── sidebar/        # Sidebar components
│   │   └── ui/             # shadcn/ui base components
│   ├── contexts/           # React Context providers
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utilities and API clients
│   ├── tests/              # Vitest tests
│   └── types/              # TypeScript type definitions
│
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── db/             # Database (models, CRUD, engine)
│   │   ├── models/         # Pydantic schemas
│   │   ├── routers/        # API endpoints
│   │   └── main.py         # FastAPI app
│   ├── tests/              # pytest tests
│   ├── alembic/            # Database migrations
│   └── requirements.txt    # Python dependencies
│
└── README.md               # This file
```

## Features

### Implemented ✅

- **Chat Interface**: Modern, responsive chat UI with markdown support
- **Server-Sent Events**: Real-time streaming responses
- **Conversation Management**: Create, list, update, delete conversations
- **Message Persistence**: All messages stored in PostgreSQL
- **Tool Result Cards**: Specialized UI for flights, hotels, weather, etc.
- **Dark Mode**: System-aware theme with manual toggle
- **Welcome Conversation**: Helpful onboarding for new users
- **Comprehensive Tests**: 30+ tests across frontend and backend

### Pending 🚧

- **LangGraph Agent**: Multi-agent orchestration system (Agent Architect)
- **Travel APIs**: Integration with 6 travel APIs (API Integration Engineer)
  - Flight search (Amadeus/Skyscanner)
  - Hotel booking (Booking.com)
  - Weather forecasts (OpenWeather)
  - Currency conversion (ExchangeRate-API)
  - Attractions (Google Places)
  - Itinerary planning (custom logic)
- **Production Deployment**: Docker, CI/CD, monitoring (DevOps Engineer)

## Development Workflow

1. **Frontend Development**: Run `npm run dev` in `frontend/` directory
2. **Backend Development**: Run `uvicorn app.main:app --reload` in `backend/` directory
3. **Testing**: Run tests before committing changes
4. **Code Quality**: Follow existing patterns and conventions

## API Endpoints

### Conversations

- `GET /api/conversations` - List all conversations
- `POST /api/conversations` - Create new conversation
- `GET /api/conversations/{id}` - Get conversation by ID
- `PATCH /api/conversations/{id}` - Update conversation title
- `DELETE /api/conversations/{id}` - Delete conversation
- `GET /api/conversations/{id}/messages` - Get messages for conversation

### Chat

- `POST /api/chat/stream` - Stream chat response (SSE)

### Health

- `GET /health` - Health check endpoint

## Environment Variables

### Frontend (`.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (`.env`)

```env
DATABASE_URL=postgresql+asyncpg://user:password@host/database
HOST=0.0.0.0
PORT=8000
```

## Contributing

This project follows these conventions:

- **TypeScript**: Strict mode enabled
- **Python**: Type hints required
- **Code Style**: Prettier (frontend), Black (backend)
- **Commits**: Descriptive commit messages
- **Testing**: Write tests for new features

## License

MIT

## Contact

For questions or issues, please contact the team lead or create an issue in the repository.

---

**Built with ❤️ by the Voyager AI team**
