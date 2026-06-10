# AI Travel Concierge - Architecture Documentation

## System Overview

The AI Travel Concierge is a sophisticated conversational AI system built using LangGraph and LangChain for orchestrating multi-agent workflows with RAG capabilities.

## Core Components

### 1. LangGraph Workflow (`src/graphs/`)

The heart of the system is a state machine that manages conversation flow:

```
User Input → Intent Classification → Information Check → Context Retrieval → Agent Routing → Response
```

#### State Management
- **ConversationState**: Maintains all context throughout the conversation
- **State Transitions**: Handled via conditional edges based on intent and completeness

#### Graph Nodes
- `classify_intent_node`: Determines user intent (plan, recommend, book, question)
- `retrieve_context_node`: Fetches relevant knowledge from vector store
- `plan_trip_node`: Generates itineraries
- `recommend_node`: Provides travel recommendations
- `booking_node`: Processes bookings
- `clarification_node`: Requests missing information

#### Edge Routing
- Intent-based routing
- Information completeness checks
- Error handling and retry logic

### 2. Multi-Agent System (`src/agents/`)

Specialized agents for different travel tasks:

#### Travel Planner Agent
- **Purpose**: Creates detailed day-by-day itineraries
- **Tools**: Places API, Weather API
- **Capabilities**: 
  - Activity scheduling
  - Route optimization
  - Preference-based recommendations

#### Recommendation Engine Agent
- **Purpose**: Finds and ranks travel options
- **Tools**: Flights API, Hotels API, Activities API
- **Capabilities**:
  - Multi-criteria comparison
  - Price-based filtering
  - Review aggregation

#### Booking Assistant Agent
- **Purpose**: Handles reservations and payments
- **Tools**: Booking APIs
- **Capabilities**:
  - Verification before booking
  - Payment processing coordination
  - Confirmation management

### 3. RAG System (`src/retrievers/`)

Retrieval-Augmented Generation for travel knowledge:

#### Components
- **Vector Store**: ChromaDB for semantic search
- **Embeddings**: OpenAI embeddings (text-embedding-3-small)
- **Chunking**: Recursive text splitter with 1000 token chunks

#### Retrieval Process
1. User query → Embed query
2. Similarity search in vector store
3. Filter by metadata (destination, interests)
4. Return top-k relevant documents
5. Inject into agent context

### 4. Memory Management (`src/memory/`)

Conversation and user preference tracking:

- **Conversation History**: Full message history per session
- **User Preferences**: Persistent preferences across sessions
- **Trip Context**: Active trip planning state

### 5. External Tools (`src/tools/`)

Integration with external services:

- **Flight Search**: Amadeus API
- **Hotel Search**: Booking.com API / Custom aggregator
- **Places**: Google Places API
- **Weather**: Weather API
- **Activities**: GetYourGuide API / Viator

## Data Flow

```
1. User Input
   ↓
2. Add to ConversationState
   ↓
3. Classify Intent (LLM)
   ↓
4. Check Information Completeness
   ↓
5. Retrieve Context (RAG)
   ↓
6. Route to Appropriate Agent
   ↓
7. Agent Executes with Tools
   ↓
8. Update State
   ↓
9. Return Response
   ↓
10. Wait for Next Input (or End)
```

## Technology Stack

### Core Framework
- **LangChain**: Agent framework and tool integration
- **LangGraph**: Stateful workflow orchestration with checkpointer support
- **Groq Chat Model**: Llama-based chat model endpoint with `openai/gpt-oss-120b` as primary LLM

### Storage
- **ChromaDB**: Local vector database with automatic absolute path resolving logic to prevent relative run failures
- **Relational Databases**: SQLite locally (`backend.db`), transitioning to PostgreSQL (Neon) in production
- **LangGraph Checkpointer**: `SqliteSaver` locally (`checkpoints.db`), transitioning to `PostgresSaver` with connection pooling in production for stateless active state persistence

### APIs
- **OpenAI**: LLM and embeddings
- **Amadeus**: Flight data
- **Google Maps**: Places and directions
- **Custom APIs**: Hotels, activities, weather

## Design Patterns

### 1. State Machine Pattern
LangGraph manages conversation as a state machine with defined transitions.

### 2. Agent Pattern
Specialized agents with focused responsibilities and tool access.

### 3. RAG Pattern
External knowledge retrieval augments LLM responses.

### 4. Tool Use Pattern
Agents use structured tools for external API calls.

### 5. Memory Pattern
- **Conversational Memory**: Relational SQL tables storing complete query/response messages
- **LangGraph Checkpoint Memory**: Persistent sqlite/postgres saver checkpointer that tracks graph node checkpoints, compiled user preferences, and internal routing states across requests
- **Active Memory Playback**: Lifespan startup or request hook parses previous messages from the database and checks thread checkpoint states to seamlessly resume active conversation memory

## Scalability Considerations

### Horizontal Scaling
- **Stateless API Host**: FastAPI backend instances can scale horizontally behind load balancers with zero server affinity
- **Centralized Checkpointing**: Multi-instance servers leverage PostgreSQL pool-based checkpoints (`PostgresSaver`) to share user execution states dynamically
- **Serverless PostgreSQL**: Neon cluster automatically manages database capacity and scales compute threads independently

### Caching
- Redis for frequent queries
- Vector store result caching
- API response caching

### Rate Limiting
- API call throttling
- Token budget management
- Concurrent request limits

## Security

### API Key Management
- Environment variables for secrets
- Key rotation support
- Separate keys per environment

### Data Privacy
- User data encryption
- PII handling compliance
- Conversation data retention policies

### Input Validation
- Query sanitization
- Budget limit enforcement
- Booking verification

## Monitoring

### LangSmith Integration
- Request tracing
- Performance metrics
- Error tracking

### Custom Metrics
- Agent execution time
- Tool call success rates
- User satisfaction scores

## Future Enhancements

1. **Multi-modal Support**: Image-based queries
2. **Voice Interface**: Speech-to-text integration
3. **Real-time Collaboration**: Multi-user trip planning
4. **Advanced Personalization**: ML-based preference learning
5. **Integration Hub**: Connect to more travel services
