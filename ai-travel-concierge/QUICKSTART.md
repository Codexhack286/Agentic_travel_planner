# Quick Start Guide

## Get Up and Running in 5 Minutes

### 1. Install Dependencies

```bash
cd ai-travel-concierge
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key (minimum required):
```
OPENAI_API_KEY=sk-your-key-here
```

### 3. Initialize Vector Database

```bash
python scripts/init_vectordb.py
```

### 4. Run the Application

**CLI Mode (Interactive):**
```bash
python src/main.py --cli
```

**Example Usage:**
```
You: I want to plan a 5-day trip to Paris
Assistant: [Provides itinerary suggestions]

You: What are the best areas to stay in Paris?
Assistant: [Gives accommodation recommendations]

You: exit
```

## Example Conversations

### Planning a Trip
```
You: Plan a 3-day cultural trip to Tokyo for 2 people
Assistant: I'll help you plan a cultural trip to Tokyo...
```

### Getting Recommendations
```
You: Recommend budget hotels in Bali near the beach
Assistant: Here are some great budget-friendly beach hotels...
```

### Asking Questions
```
You: What's the best time to visit Paris?
Assistant: Spring (April-June) and fall (September-November)...
```

## Key Features

✅ **Intelligent Trip Planning** - Creates day-by-day itineraries
✅ **Personalized Recommendations** - Flights, hotels, activities
✅ **RAG-Powered Answers** - Knowledge base of travel information
✅ **Multi-Agent System** - Specialized agents for different tasks
✅ **State Management** - Maintains context throughout conversation

## Architecture at a Glance

```
User Input
    ↓
LangGraph State Machine
    ↓
Intent Classification
    ↓
Information Check → RAG Retrieval
    ↓
Specialized Agents
    ├─ Travel Planner
    ├─ Recommender
    └─ Booking Assistant
    ↓
Response Generation
```

## Next Steps

1. **Explore the Code**: Start with `src/main.py` and `src/graphs/workflows/`
2. **Read Documentation**: Check `docs/` for detailed guides
3. **Customize Agents**: Modify agent prompts in `src/agents/`
4. **Add Your Data**: Enhance vector store with your travel knowledge
5. **Integrate APIs**: Connect real travel APIs in `src/tools/`

## Troubleshooting

**Issue**: Import errors
```bash
pip install -r requirements.txt --force-reinstall
```

**Issue**: Vector store errors
```bash
python scripts/init_vectordb.py
```

**Issue**: API errors
- Check your `.env` file has valid API keys
- Ensure OpenAI API key starts with `sk-`

## Common Commands

```bash
# Run tests
make test

# Format code
make format

# Run linting
make lint

# Clean generated files
make clean
```

## Support

- 📚 [Full Documentation](docs/)
- 🏗️ [Architecture Guide](docs/architecture/SYSTEM_DESIGN.md)
- 💻 [Development Guide](docs/guides/DEVELOPMENT.md)
- 🐛 [Report Issues](link-to-issues)

Happy Coding! 🚀
