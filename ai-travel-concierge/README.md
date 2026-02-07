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

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize vector database
python scripts/init_vectordb.py

# Run the application
python src/main.py
```

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
