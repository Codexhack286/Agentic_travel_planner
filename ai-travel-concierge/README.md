# AI Travel Concierge - LangGraph + LangChain Implementation

## Project Overview
AI-powered travel concierge system using LangGraph for orchestrating multi-agent workflows and LangChain for RAG-based travel recommendations.

## Architecture
- **LangGraph Workflows**: State machine for conversation flow
- **Multi-Agent System**: Specialized agents for different travel tasks
- **RAG Pipeline**: Vector-based retrieval for personalized recommendations
- **Memory Management**: Conversation and user preference tracking

## Directory Structure

```
ai-travel-concierge/
├── src/
│   ├── agents/              # Specialized AI agents
│   ├── chains/              # LangChain chains
│   ├── graphs/              # LangGraph workflows
│   ├── tools/               # External tools and APIs
│   ├── prompts/             # Prompt templates
│   ├── models/              # Data models
│   ├── memory/              # Memory management
│   ├── retrievers/          # RAG retrievers
│   └── utils/               # Utility functions
├── tests/                   # Test suite
├── config/                  # Configuration files
├── data/                    # Data storage
├── logs/                    # Application logs
└── docs/                    # Documentation

```

## Setup

Using `uv` package manager (recommended):

```bash
# Sync dependencies in the virtual environment
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys (or use the workspace root .env)

# Run the API verification script to verify keys and database access
uv run python scripts/test_keys.py

# Reset and seed the vector database
uv run python scripts/reset_and_init.py

# Run the command line agent interface (CLI)
uv run python src/main.py --cli
```

## Relational DB & LangGraph Checkpointers

The agent is stateful and uses a dual-persistence strategy:
1. **Dynamic Path Resolution**: Config file resolver converts any relative path settings (like `chroma_persist_directory`) into absolute paths relative to the agent folder root. This prevents relative path mismatches between backend service invocations, tests, and CLI runs.
2. **SQLite Checkpointer (Local)**: When running locally, conversation states are written to `ai-travel-concierge/data/checkpoints.db` automatically using `SqliteSaver`.
3. **PostgreSQL Checkpointer (Production)**: When configured with a PostgreSQL URL, the graph automatically switches to `PostgresSaver` and uses a connection pool (`ConnectionPool`) for multi-worker support.

## Key Components

### 1. Agents
- **Travel Planner**: Creates itineraries and trip plans
- **Booking Assistant**: Handles reservations and bookings
- **Recommendation Engine**: Provides personalized suggestions

### 2. LangGraph Workflows
- Conversation state management
- Multi-step planning workflows
- Error handling and retry logic

### 3. RAG System
- Vector store for travel knowledge
- Embedding-based retrieval
- Context-aware responses

## Development

```bash
# Run tests
pytest tests/

# Run with hot reload
python src/main.py --reload

# Check code quality
flake8 src/
black src/
```

## License
[Your License Here]
