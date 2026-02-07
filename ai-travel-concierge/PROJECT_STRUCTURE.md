# AI Travel Concierge - Complete Project Structure

```
ai-travel-concierge/
│
├── README.md                          # Project overview and documentation
├── QUICKSTART.md                      # Quick start guide
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
├── Makefile                          # Common development commands
├── pytest.ini                        # Pytest configuration
│
├── src/                              # Source code
│   ├── __init__.py
│   ├── main.py                       # Application entry point
│   │
│   ├── agents/                       # Specialized AI agents
│   │   ├── __init__.py
│   │   ├── travel_planner/
│   │   │   ├── __init__.py
│   │   │   └── planner_agent.py     # Itinerary creation agent
│   │   ├── recommendation_engine/
│   │   │   ├── __init__.py
│   │   │   └── recommender_agent.py # Recommendation agent
│   │   └── booking_assistant/
│   │       ├── __init__.py
│   │       └── booking_agent.py      # Booking management agent
│   │
│   ├── chains/                       # LangChain chains (for custom workflows)
│   │   └── __init__.py
│   │
│   ├── graphs/                       # LangGraph workflows
│   │   ├── __init__.py
│   │   ├── workflows/
│   │   │   ├── __init__.py
│   │   │   └── travel_concierge_graph.py  # Main graph workflow
│   │   ├── nodes/
│   │   │   ├── __init__.py
│   │   │   └── graph_nodes.py        # Node functions
│   │   ├── edges/
│   │   │   ├── __init__.py
│   │   │   └── graph_edges.py        # Edge routing logic
│   │   └── state/
│   │       ├── __init__.py
│   │       └── conversation_state.py # State definitions
│   │
│   ├── tools/                        # External tools and APIs
│   │   ├── __init__.py
│   │   ├── external_apis/
│   │   │   └── __init__.py          # Travel API integrations
│   │   ├── search/
│   │   │   └── __init__.py
│   │   ├── validation/
│   │   │   └── __init__.py
│   │   └── formatting/
│   │       └── __init__.py
│   │
│   ├── prompts/                      # Prompt templates
│   │   └── __init__.py
│   │
│   ├── models/                       # Data models
│   │   └── __init__.py
│   │
│   ├── memory/                       # Memory management
│   │   ├── __init__.py
│   │   ├── conversation/
│   │   │   └── __init__.py          # Conversation history
│   │   ├── user_preferences/
│   │   │   └── __init__.py          # User preferences storage
│   │   └── trip_context/
│   │       └── __init__.py          # Active trip context
│   │
│   ├── retrievers/                   # RAG components
│   │   ├── __init__.py
│   │   ├── vector_stores/
│   │   │   └── __init__.py
│   │   ├── embeddings/
│   │   │   └── __init__.py
│   │   └── rag/
│   │       ├── __init__.py
│   │       └── travel_retriever.py   # Main RAG retriever
│   │
│   └── utils/                        # Utility functions
│       ├── __init__.py
│       ├── config.py                # Configuration management
│       └── logger.py                # Logging utilities
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── unit/                        # Unit tests
│   │   ├── __init__.py
│   │   └── test_planner_agent.py
│   ├── integration/                 # Integration tests
│   │   └── __init__.py
│   └── e2e/                        # End-to-end tests
│       └── __init__.py
│
├── config/                          # Configuration files
│   ├── agents/                     # Agent configurations
│   ├── models/                     # Model configurations
│   ├── apis/                       # API configurations
│   └── prompts/                    # Prompt configurations
│
├── data/                           # Data storage
│   ├── vector_db/                 # Vector database (ChromaDB)
│   ├── user_data/                 # User information
│   ├── travel_data/               # Travel knowledge base
│   └── cache/                     # Cached responses
│
├── logs/                          # Application logs
│
├── docs/                          # Documentation
│   ├── architecture/
│   │   └── SYSTEM_DESIGN.md      # System architecture
│   ├── api/                      # API documentation
│   └── guides/
│       └── DEVELOPMENT.md        # Development guide
│
└── scripts/                      # Utility scripts
    └── init_vectordb.py         # Initialize vector database
```

## Key Files Explained

### Core Application
- **src/main.py**: Entry point, initializes graph and handles CLI
- **src/graphs/workflows/travel_concierge_graph.py**: Main LangGraph workflow

### State Management
- **src/graphs/state/conversation_state.py**: State definitions (TypedDict)
- **src/graphs/nodes/graph_nodes.py**: Node functions that process state
- **src/graphs/edges/graph_edges.py**: Routing logic between nodes

### Agents
- **src/agents/travel_planner/planner_agent.py**: Creates itineraries
- **src/agents/recommendation_engine/recommender_agent.py**: Provides recommendations
- **src/agents/booking_assistant/booking_agent.py**: Handles bookings

### RAG System
- **src/retrievers/rag/travel_retriever.py**: Vector store retrieval
- **data/vector_db/**: ChromaDB persistence

### Configuration
- **.env.example**: Template for environment variables
- **src/utils/config.py**: Configuration loader
- **config/**: Various configuration files

### Testing
- **tests/unit/**: Unit tests for individual components
- **tests/integration/**: Integration tests for workflows
- **tests/e2e/**: End-to-end user journey tests

### Documentation
- **README.md**: Project overview
- **QUICKSTART.md**: Getting started guide
- **docs/architecture/**: System design documentation
- **docs/guides/**: Development guides

## Module Dependencies

```
main.py
    └── TravelConciergeGraph
            ├── GraphNodes
            │   ├── TravelPlannerAgent
            │   ├── RecommenderAgent
            │   ├── BookingAgent
            │   └── TravelRetriever
            ├── GraphEdges
            └── ConversationState
```

## Data Flow

```
User Input
    ↓
[main.py] Create/Load ConversationState
    ↓
[travel_concierge_graph.py] Execute Graph
    ↓
[graph_nodes.py] Process Nodes
    ├── [planner_agent.py] Create Itinerary
    ├── [recommender_agent.py] Get Recommendations
    ├── [booking_agent.py] Process Booking
    └── [travel_retriever.py] Retrieve Context
    ↓
[conversation_state.py] Update State
    ↓
[main.py] Return Response
```

## Configuration Files

All configuration is managed through:
1. `.env` file for secrets (API keys)
2. `config/` directory for structured configs
3. `src/utils/config.py` for loading and validation

## Testing Strategy

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test agent workflows and tool integrations
- **E2E Tests**: Test complete user conversations

## Development Workflow

1. Modify code in `src/`
2. Add tests in `tests/`
3. Run `make test`
4. Run `make lint`
5. Run `make format`
6. Test with `make run-cli`
