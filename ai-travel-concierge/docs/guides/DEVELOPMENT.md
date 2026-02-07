# Development Guide

## Getting Started

### Prerequisites
- Python 3.10+
- pip or conda
- Redis (optional, for caching)
- API keys (OpenAI, travel APIs)

### Installation

1. **Clone and navigate to project:**
```bash
cd ai-travel-concierge
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Initialize vector database:**
```bash
python scripts/init_vectordb.py
```

## Project Structure

```
src/
├── agents/              # Specialized AI agents
│   ├── travel_planner/      # Itinerary creation
│   ├── recommendation_engine/  # Travel recommendations
│   └── booking_assistant/      # Booking management
├── graphs/              # LangGraph workflows
│   ├── workflows/           # Main graph definitions
│   ├── nodes/              # Node functions
│   ├── edges/              # Edge routing logic
│   └── state/              # State definitions
├── tools/               # External API integrations
├── retrievers/          # RAG components
├── memory/              # Memory management
├── utils/               # Utilities
└── main.py              # Application entry point
```

## Development Workflow

### 1. Adding a New Agent

```python
# src/agents/my_agent/my_agent.py
from langchain.agents import AgentExecutor, create_openai_functions_agent

class MyAgent:
    def __init__(self, config):
        self.llm = ChatOpenAI(model=config["model_name"])
        self.tools = [MyTool()]
        self.agent = self._create_agent()
    
    def _create_agent(self):
        prompt = ChatPromptTemplate.from_messages([...])
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools)
```

### 2. Adding a New Graph Node

```python
# src/graphs/nodes/graph_nodes.py
async def my_node(state: ConversationState) -> ConversationState:
    """My custom node function."""
    # Process state
    # Call agents or tools
    # Update state
    return state
```

### 3. Adding a New Tool

```python
# src/tools/my_tool.py
from langchain.tools import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "Description of what the tool does"
    
    async def _arun(self, query: str) -> dict:
        # Tool implementation
        return {"result": "data"}
```

### 4. Modifying State

```python
# src/graphs/state/conversation_state.py
class ConversationState(TypedDict):
    # Add new fields as needed
    my_new_field: Optional[str]
```

## Testing

### Unit Tests
```bash
# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_planner_agent.py

# Run with coverage
pytest --cov=src tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/
```

### End-to-End Tests
```bash
pytest tests/e2e/
```

## Running the Application

### CLI Mode
```bash
python src/main.py --cli
```

### Development Mode (with hot reload)
```bash
python src/main.py --reload
```

### Production Mode
```bash
python src/main.py
```

## Debugging

### Enable Verbose Logging
```python
# In .env
LOG_LEVEL=DEBUG
```

### LangSmith Tracing
```python
# In .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
```

### Debug Specific Agent
```python
agent = TravelPlannerAgent(config)
result = await agent.create_itinerary(state)
print(result)
```

## Code Style

### Formatting
```bash
# Format code
black src/

# Check formatting
black --check src/
```

### Linting
```bash
# Run flake8
flake8 src/

# Run mypy (type checking)
mypy src/
```

## Common Tasks

### Adding a New Skill to Vector Store
```python
from src.retrievers.rag.travel_retriever import TravelRetriever

retriever = TravelRetriever(config)
retriever.add_texts(
    texts=["Paris is known for..."],
    metadatas=[{"destination": "Paris", "category": "overview"}]
)
```

### Modifying Prompts
```python
# Edit prompts in src/prompts/
# Or directly in agent initialization
prompt = ChatPromptTemplate.from_messages([
    ("system", "Your system prompt here"),
    ("human", "{input}")
])
```

### Visualizing Graph
```python
from src.graphs.workflows.travel_concierge_graph import TravelConciergeGraph

graph = TravelConciergeGraph(config)
graph.visualize("travel_graph.png")
```

## Performance Optimization

### Caching
- Use Redis for frequently accessed data
- Cache vector store results
- Cache API responses

### Async Operations
- Use `async/await` for I/O operations
- Batch API calls when possible
- Parallel tool execution

### Token Management
- Monitor token usage
- Truncate long conversations
- Use cheaper models for simple tasks

## Troubleshooting

### Common Issues

**Issue**: "Vector store not found"
```bash
# Solution: Initialize vector store
python scripts/init_vectordb.py
```

**Issue**: "API key not found"
```bash
# Solution: Check .env file
cat .env | grep API_KEY
```

**Issue**: "Import errors"
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Best Practices

1. **Always use async/await** for agent and tool calls
2. **Validate state** before passing to agents
3. **Handle errors gracefully** with try/catch
4. **Log important events** for debugging
5. **Test thoroughly** before deploying
6. **Use type hints** for better IDE support
7. **Document complex logic** with comments
8. **Keep prompts modular** and reusable

## Contributing

1. Create a feature branch
2. Make changes
3. Add tests
4. Run linting and formatting
5. Submit pull request

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Project Wiki](link-to-wiki)
