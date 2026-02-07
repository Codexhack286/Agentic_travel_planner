# AI Travel Concierge: complete project plan for Track B

**A zero-budget, 8-week implementation plan for a 4-person student team building an advanced AI travel concierge agent using LangGraph, free-tier APIs, and modern deployment infrastructure.** This document covers every dimension of the project — from architecture and sprint-level task checklists to risk mitigation and progress templates — so the team can begin executing immediately on February 6, 2026.

---

## Scope, objectives, and what success looks like

The AI Travel Concierge is a conversational agent that helps users plan trips end-to-end: searching flights, finding hotels, checking weather, converting currencies, discovering restaurants and attractions, and providing destination information including visa requirements. The agent uses a **supervisor multi-agent architecture** built on LangGraph, powered by free-tier LLMs, and deployed on free-tier cloud platforms.

**Primary objectives** are to deliver a working MVP by Week 4 (March 6) and a polished product by Week 8 (April 3). The MVP handles at least 3 travel tools in a single conversational flow. The final product integrates **6+ travel APIs**, includes persistent memory, streaming responses, and a polished React UI.

**Success criteria** break down into five measurable categories:

- **Functional completeness**: Agent correctly invokes ≥6 travel tools, handles multi-turn conversations with context retention, and provides synthesized trip plans combining flight + hotel + weather + currency data
- **Technical quality**: ≥80% unit test coverage on tool functions, all CI checks passing, <3 second response time for cached queries, graceful fallback when any single API or LLM is rate-limited
- **User experience**: Streaming responses visible within 1 second, mobile-responsive UI, conversation history persisted across sessions, destination images displayed for searched locations
- **Infrastructure**: Automated CI/CD pipeline, monitoring with trace visibility, zero-downtime deployment, all services running on genuinely free tiers
- **Documentation**: Architecture diagram, API documentation, setup guide that lets a new developer run the project locally in <15 minutes

---

## Roles for four generalist students

Rather than rigid specializations, each team member owns a **domain** while contributing across the stack. Everyone writes tests for their domain and participates in code review.

| Role | Primary domain | Key responsibilities | Secondary duties |
|------|---------------|---------------------|-----------------|
| **Agent Architect** (Team Lead) | LangGraph core, LLM integration | Builds supervisor agent, state management, LLM provider routing with fallback, prompt engineering. Owns `agents/` directory | Architecture decisions, sprint planning, code review |
| **API Integration Engineer** | Travel API tools | Implements all 6+ tool wrappers (Amadeus, Open-Meteo, Frankfurter, REST Countries, Unsplash, visa APIs). Owns `tools/` directory | Caching layer (Upstash Redis), rate-limit handling, API response normalization |
| **Full-Stack Developer** | Frontend + Backend API | Builds Next.js chat UI with streaming, FastAPI endpoints, WebSocket connections, database models. Owns `frontend/` and `routers/` | Supabase/Neon schema design, auth if needed, responsive design |
| **DevOps & Quality Engineer** | CI/CD, testing, deployment, monitoring | Sets up GitHub Actions, Render/Vercel deployment, LangSmith tracing, writes test infrastructure. Owns `.github/`, `tests/` infrastructure | Performance optimization, Dockerfile, documentation |

**Rotation policy**: Every sprint, each member reviews at least 2 PRs outside their domain. The Team Lead runs a 15-minute daily standup async in a shared Slack/Discord channel.

---

## Technical stack: every component justified

### Core framework

| Layer | Technology | Why this choice |
|-------|-----------|----------------|
| Agent orchestration | **LangGraph v1.0+** | Stateful graph-based agent execution with checkpointing, streaming, and human-in-the-loop. Production-grade, used by LinkedIn/Uber |
| LLM framework | **LangChain** (via `langchain-google-genai`, `langchain-groq`) | Unified tool-calling interface across LLM providers. Seamless LangGraph integration |
| Backend | **FastAPI** (Python 3.11) | Async-native, automatic OpenAPI docs, excellent for streaming responses via SSE |
| Frontend | **Next.js 14** (React, TypeScript) | Best free Vercel deployment story, SSR capabilities, strong ecosystem |
| Database | **Neon** (PostgreSQL) | 100 CU-hours/month free, scale-to-zero, no 30-day expiry (unlike Render), 20 projects |
| Cache | **Upstash** (Redis) | **500K commands/month** free, HTTP-based API ideal for serverless, 256 MB storage |
| Monitoring | **LangSmith** (Developer plan) | Native LangGraph integration, 5K traces/month free, zero-config setup |

### LLM provider strategy with automatic fallback

The project uses a **three-tier LLM routing strategy** to maximize availability on free tiers:

| Tier | Provider | Model | Free limits | Use case |
|------|----------|-------|-------------|----------|
| Primary | **Google Gemini** | Gemini 2.5 Flash | **10 RPM, 250 RPD**, 250K TPM | All main agent conversations. Best quality-to-volume ratio on free tier. 1M token context window |
| Fast fallback | **Groq** | Llama 4 Scout 17B | **30 RPM, 1K RPD**, 30K TPM | Speed-critical queries, Gemini rate-limit overflow. 300+ tokens/sec inference |
| Emergency fallback | **OpenRouter** | Free models (Llama 4, DeepSeek, Mistral) | 20 RPM, 50 RPD | When both primary providers are exhausted. 30+ free models available |

All three providers support **tool/function calling**, which is critical for the agent to invoke travel API tools. The provider abstraction layer detects 429 rate-limit errors and automatically cascades to the next tier. A combined daily capacity of roughly **1,300 requests/day** across all three providers is sufficient for development, demos, and moderate usage.

**Critical warning**: Google cut Gemini free-tier quotas by 50-80% in December 2025, and Gemini 2.0 Flash retires March 31, 2026. Build the abstraction layer from day one so switching providers is a config change, not a code rewrite.

### Travel API integrations: the six core tools

| # | API | Data provided | Free tier | Auth | Priority |
|---|-----|--------------|-----------|------|----------|
| 1 | **Amadeus for Developers** | Flight search, hotel search, POIs, airport lookup | 2K-10K calls/month per endpoint (test environment) | OAuth2 bearer token | Critical — core travel data |
| 2 | **Open-Meteo** | Weather forecasts (16-day), historical weather, air quality | **10K calls/day, no API key needed** | None | Critical — no-friction weather |
| 3 | **REST Countries** | Country info: currency, language, timezone, capital, flag, population | **Unlimited, no API key** | None | Critical — destination context |
| 4 | **Frankfurter** | Currency exchange rates (ECB data, 30+ currencies) | **Unlimited, no API key** | None | Critical — zero-friction currency |
| 5 | **Unsplash** | High-resolution destination photos (3M+ images) | 50 req/hr (demo), 5K/hr (production approved) | API key (Client-ID header) | High — visual UX differentiator |
| 6 | **Passport Visa API** or **TuGo** | Visa requirements between any two countries, travel advisories | Free with registration | API key | Medium — travel planning value |

**Bonus APIs** to add if time permits: Google Travel Impact Model (flight CO₂ emissions, completely free), Foursquare Places (10K basic calls/month for restaurant/attraction search), and OpenWeatherMap (1M calls/month for weather alerts and air quality alongside Open-Meteo).

**Key Amadeus gotcha**: The test environment uses **cached/limited data** — not all airports or routes exist. This is acceptable for a student project but means some queries will return empty results. Document this limitation clearly in the UI.

---

## Architecture and data model

### System architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js on Vercel)              │
│  Chat UI ←→ SSE Stream ←→ /api/chat endpoint (proxy)        │
│  Trip Dashboard │ Destination Cards │ Conversation History   │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTPS / SSE
┌──────────────────────────▼───────────────────────────────────┐
│                  BACKEND (FastAPI on Render)                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ /api/chat   │  │ /api/trips   │  │ /api/health        │  │
│  │ (streaming) │  │ (CRUD)       │  │ (monitoring)       │  │
│  └──────┬──────┘  └──────────────┘  └────────────────────┘  │
│         │                                                     │
│  ┌──────▼──────────────────────────────────────────────────┐ │
│  │           LANGGRAPH SUPERVISOR AGENT                     │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │ │
│  │  │ Flight   │ │ Hotel    │ │ Weather  │ │ Currency  │  │ │
│  │  │ Tool     │ │ Tool     │ │ Tool     │ │ Tool      │  │ │
│  │  │(Amadeus) │ │(Amadeus) │ │(Open-    │ │(Frank-    │  │ │
│  │  │          │ │          │ │ Meteo)   │ │ furter)   │  │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────────┐    │ │
│  │  │ Dest.    │ │ Visa     │ │ Image Tool           │    │ │
│  │  │ Info     │ │ Tool     │ │ (Unsplash)           │    │ │
│  │  │(REST     │ │(Passport │ │                      │    │ │
│  │  │Countries)│ │ API)     │ │                      │    │ │
│  │  └──────────┘ └──────────┘ └──────────────────────┘    │ │
│  └─────────────────────────────────────────────────────────┘ │
│         │                    │                                │
│  ┌──────▼──────┐    ┌───────▼────────┐                      │
│  │ Neon        │    │ Upstash Redis  │                      │
│  │ PostgreSQL  │    │ (API cache,    │                      │
│  │ (sessions,  │    │  rate-limit    │                      │
│  │  trip data) │    │  tracking)     │                      │
│  └─────────────┘    └────────────────┘                      │
└──────────────────────────────────────────────────────────────┘
         │
┌────────▼─────────────────┐
│ LangSmith (Monitoring)   │
│ 5K traces/month free     │
└──────────────────────────┘
```

### LangGraph agent design

The agent evolves across sprints. **Sprint 1-2 (MVP)**: Single ReAct agent with 3-4 tools. **Sprint 3-4 (Final)**: Supervisor pattern with specialized sub-agents.

**State schema** (TypedDict with annotated fields):

```python
from typing import TypedDict, Annotated, Optional, List
from langgraph.graph import MessagesState
import operator

class TravelState(MessagesState):
    """Extended state for travel concierge agent."""
    messages: Annotated[list, operator.add]        # Conversation history
    destination: Optional[str]                       # Current destination
    travel_dates: Optional[dict]                     # {start, end}
    budget: Optional[float]                          # User's budget
    travelers: Optional[int]                         # Number of travelers
    trip_plan: Optional[dict]                        # Accumulated trip plan
    current_tool_results: Optional[dict]             # Latest API results
    user_preferences: Optional[dict]                 # Long-term preferences
```

**Supervisor routing logic**: The supervisor LLM receives the conversation state and decides which specialized tool to invoke next. It uses conditional edges to route to the appropriate tool node, then returns to the supervisor for synthesis or further tool calls. A maximum of **5 tool calls per turn** prevents infinite loops.

### Database schema (Neon PostgreSQL)

```sql
-- Core tables for the travel concierge
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    preferences JSONB DEFAULT '{}'
);

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    title VARCHAR(255),
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'tool'
    content TEXT NOT NULL,
    tool_calls JSONB,           -- For assistant messages with tool invocations
    tool_name VARCHAR(100),     -- For tool response messages
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE trip_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    destination VARCHAR(255),
    start_date DATE,
    end_date DATE,
    budget DECIMAL(10,2),
    plan_data JSONB,            -- Full structured trip plan
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);
CREATE INDEX idx_conversations_user ON conversations(user_id, updated_at DESC);
```

The schema fits comfortably within Neon's **500 MB free storage**. The `JSONB` columns provide flexibility for evolving tool responses and trip plan structures without schema migrations.

### Caching strategy (Upstash Redis)

Cache travel API responses aggressively to stay within free-tier limits and improve response times:

| Data type | Cache TTL | Rationale |
|-----------|-----------|-----------|
| Flight search results | 1 hour | Prices change frequently but not per-minute |
| Hotel availability | 2 hours | Availability is semi-stable |
| Weather forecasts | 6 hours | Weather data updates every few hours on free tier |
| Currency rates | 24 hours | ECB updates once per business day |
| Country info | 7 days | Static data, rarely changes |
| Destination images | 24 hours | Unsplash images are static content |

With a **500K commands/month** Upstash limit, the team can execute ~16K cache operations per day — more than sufficient. Each API call should first check Redis, and only call the external API on cache miss.

---

## Milestone timeline: four 2-week sprints

### Sprint 1 (Feb 6–Feb 20): Foundation and first tool

**Goal**: Project scaffolding, CI/CD pipeline, first working tool, basic chat UI.

| Day | Task | Owner | Done criteria |
|-----|------|-------|--------------|
| 1-2 | Monorepo setup: `backend/` (FastAPI) + `frontend/` (Next.js) + `pyproject.toml` + `package.json` | Full-Stack Dev | Both apps run locally, README with setup instructions |
| 1-2 | GitHub repo, branch protection (`main` requires 1 review + passing CI), issue templates | DevOps Engineer | Protection rules active, issue board created |
| 2-3 | GitHub Actions CI: `backend-ci.yml` with pytest + ruff + mypy, `frontend-ci.yml` with Vitest + ESLint + tsc | DevOps Engineer | CI runs on every PR, both workflows pass |
| 2-3 | Neon PostgreSQL provisioned, schema applied, SQLAlchemy/asyncpg models | Full-Stack Dev | Database accessible, migrations run |
| 3-4 | Upstash Redis provisioned, caching utility functions | API Engineer | Redis connected, get/set with TTL working |
| 3-5 | Gemini API integration with LangChain, fallback to Groq, provider abstraction layer | Agent Architect | Can call Gemini and Groq with identical interface, auto-fallback on 429 |
| 4-6 | First LangGraph agent: single ReAct agent with 1 tool (Open-Meteo weather) | Agent Architect | `agent.invoke("What's the weather in Paris?")` returns real weather data |
| 5-7 | FastAPI `/api/chat` endpoint with SSE streaming | Full-Stack Dev | `curl` to endpoint returns streaming response |
| 5-7 | Amadeus API wrapper: flight search tool with caching | API Engineer | Tool returns flight results from Amadeus test environment |
| 7-10 | Basic Next.js chat interface with streaming display | Full-Stack Dev | User can type message, see streaming response in browser |
| 8-10 | Unit tests for weather tool and flight tool (mocked API responses) | DevOps Engineer | ≥5 tests per tool, all passing in CI |
| 10 | LangSmith connected, traces visible in dashboard | DevOps Engineer | Agent invocations appear in LangSmith with tool call details |
| 10-14 | Deploy: Vercel (frontend) + Render (backend) | DevOps Engineer | Both accessible via public URLs, auto-deploy on merge to main |

**Sprint 1 deliverable**: A deployed chat interface where users can ask about weather and flights, receiving real API data through a LangGraph agent with streaming responses.

### Sprint 2 (Feb 20–Mar 6): MVP with 4+ tools

**Goal**: Expand to 4+ working tools, multi-turn conversation memory, polished MVP.

| Day | Task | Owner | Done criteria |
|-----|------|-------|--------------|
| 1-3 | Currency conversion tool (Frankfurter API) | API Engineer | Tool converts between any supported currency pair |
| 1-3 | Destination info tool (REST Countries API) | API Engineer | Tool returns country details: capital, language, timezone, currency, flag |
| 2-4 | Agent expanded to 4 tools with improved system prompt | Agent Architect | Agent correctly selects appropriate tool based on user query |
| 3-5 | Conversation memory: InMemorySaver checkpointer → Neon PostgreSQL checkpointer | Agent Architect | Multi-turn conversations maintain context (remembers destination from earlier messages) |
| 4-6 | Unsplash image tool + destination card component in UI | API Engineer + Full-Stack Dev | Destination queries display beautiful photos alongside text |
| 5-7 | Hotel search tool (Amadeus) | API Engineer | Tool returns hotel options for a destination + dates |
| 6-8 | Improved chat UI: conversation sidebar, message formatting, loading states | Full-Stack Dev | Polished chat experience with Markdown rendering, tool result cards |
| 7-9 | Visa requirements tool (Passport API or TuGo) | API Engineer | Tool returns visa status between two countries |
| 8-10 | Integration tests: FastAPI endpoints with mocked agent, multi-turn conversation tests | DevOps Engineer | ≥10 integration tests passing in CI |
| 9-10 | Error handling: graceful degradation when APIs fail or rate-limit | Agent Architect | Agent responds helpfully even when a tool fails ("I couldn't check flights right now, but here's what I know...") |
| 10-14 | MVP demo preparation, bug fixes, README update | All | End-to-end demo: "Plan a trip to Tokyo" → flights + hotel + weather + currency + destination info |

**Sprint 2 deliverable (MVP)**: A functional travel concierge handling **6 tools** (flights, hotels, weather, currency, destination info, visa/images), with conversation memory and a polished chat UI. Deployed and accessible.

### Sprint 3 (Mar 6–Mar 20): Advanced features and supervisor architecture

**Goal**: Evolve to supervisor multi-agent pattern, add trip planning synthesis, user preferences.

| Day | Task | Owner | Done criteria |
|-----|------|-------|--------------|
| 1-4 | Refactor to supervisor pattern: separate flight, hotel, info, and utility sub-agents | Agent Architect | Supervisor correctly delegates to specialized agents, synthesizes results |
| 2-5 | Trip plan synthesis: agent combines multiple tool results into a structured trip plan | Agent Architect | "Plan a 5-day trip to Barcelona" produces a day-by-day itinerary with flights, hotel, weather, activities |
| 3-5 | Trip plan persistence: save/load trip plans from PostgreSQL | Full-Stack Dev | Users can save trip plans and revisit them |
| 4-6 | User preferences: long-term memory store for budget range, travel style, dietary preferences | Agent Architect | Agent remembers preferences across conversations |
| 5-7 | Trip dashboard UI: visual trip plan display with cards for each component | Full-Stack Dev | Trip plan rendered as an attractive dashboard, not just chat text |
| 6-8 | Comparison feature: agent can compare 2-3 destination options side-by-side | Agent Architect | "Compare Paris vs Barcelona for a March trip" returns structured comparison |
| 7-9 | Advanced caching: smart cache invalidation, pre-warming for popular routes | API Engineer | Cache hit rate >60% for repeated queries |
| 8-10 | Comprehensive error handling: circuit breaker pattern for failing APIs, user-friendly error messages | API Engineer | No uncaught exceptions in production, graceful degradation visible in LangSmith traces |
| 9-12 | Playwright E2E tests for critical user flows | DevOps Engineer | ≥5 E2E tests: send message, multi-turn conversation, trip planning, error handling |
| 12-14 | Performance optimization: response time profiling via LangSmith, caching tuning | DevOps Engineer | P95 response time <5 seconds for cached queries |

**Sprint 3 deliverable**: Supervisor multi-agent architecture, trip plan synthesis with visual dashboard, user preferences, and comparison capabilities.

### Sprint 4 (Mar 20–Apr 3): Polish, testing, documentation, presentation

**Goal**: Production-quality polish, comprehensive testing, documentation, demo preparation.

| Day | Task | Owner | Done criteria |
|-----|------|-------|--------------|
| 1-3 | UI polish: animations, responsive design, dark mode, accessibility audit | Full-Stack Dev | Lighthouse score ≥80 for accessibility, works on mobile |
| 1-3 | Test coverage push: reach ≥80% unit test coverage on tool functions | DevOps Engineer | Coverage report shows ≥80%, all tests green |
| 2-4 | Prompt optimization: refine system prompts based on LangSmith evaluation data | Agent Architect | Agent response quality improved (measured by manual evaluation of 20 test queries) |
| 3-5 | LLM evaluation dataset: 20+ test cases with expected behaviors in LangSmith | Agent Architect + DevOps | Automated evaluation suite runs weekly |
| 4-6 | Security audit: ensure no API keys in client code, rate limiting on endpoints, input sanitization | DevOps Engineer | No secrets in frontend bundle, FastAPI rate limiting active |
| 5-7 | Documentation: architecture diagram, API docs (auto-generated from FastAPI), setup guide, user guide | All | New developer can run project locally in <15 minutes following README |
| 6-8 | Load testing: verify free-tier limits are not exceeded under demo load | API Engineer | 10 concurrent users sustained for 30 minutes without rate-limit failures |
| 8-10 | Demo script preparation: 3-minute live demo showcasing key features | All | Demo script tested 3 times, fallback plan for failures |
| 10-12 | Final bug fixes, edge case handling, README final review | All | Zero known critical bugs |
| 12-14 | Final presentation preparation, project submission | All | Presentation slides, live demo, and project report complete |

**Sprint 4 deliverable**: Production-quality application with comprehensive tests, documentation, evaluation suite, and polished presentation.

---

## Risk assessment and mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Gemini free tier further reduced or eliminated** | Medium | High | Three-tier LLM fallback already designed. Groq + OpenRouter provide combined ~1,050 RPD backup. Provider abstraction makes switching a config change |
| **Amadeus test data too limited** (missing routes/cities) | High | Medium | Document limitations clearly in UI. Implement fallback responses: "Flight data unavailable for this route — here are alternative suggestions." Consider adding Skyscanner via RapidAPI free tier as backup |
| **Render free tier sleep causes bad UX** (15-min cold start) | High | Medium | Use UptimeRobot (free) to ping the backend every 14 minutes. Alternatively, accept cold starts and show a loading spinner with explanatory text |
| **Exceeding Upstash 500K commands/month** | Low | Medium | Aggressive caching with longer TTLs. Monitor usage via Upstash dashboard. Batch Redis operations where possible |
| **Team member drops or becomes unavailable** | Medium | High | Cross-training through PR reviews. Each domain documented well enough for another member to take over. Core architecture decisions documented in ADRs |
| **LangGraph breaking changes** | Low | Medium | Pin exact version in `requirements.txt`. Follow LangChain blog for migration guides. LangGraph v1.0 was a stability release |
| **Neon database auto-scales beyond free tier** | Low | Low | Set compute budget alerts in Neon dashboard. 100 CU-hours/month is generous — a 0.25 CU instance runs ~400 hours/month |
| **Scope creep delays MVP** | Medium | High | MVP is strictly defined: 3-4 tools + basic chat. No feature additions until MVP is deployed. Use GitHub issues with sprint milestones to enforce scope |

---

## Deployment plan

### Infrastructure provisioning (Day 1-2 of Sprint 1)

| Service | Platform | Setup steps |
|---------|----------|-------------|
| Frontend | **Vercel** (Hobby plan) | Connect GitHub repo → auto-detects Next.js → configure build settings → auto-deploy on push to `main`. Free: 100 GB bandwidth, unlimited deployments |
| Backend | **Render** (Free tier) | New Web Service → connect GitHub → set build command: `pip install -r requirements.txt` → set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Free: 750 hrs/month, 512 MB RAM, sleeps after 15 min |
| Database | **Neon** (Free tier) | Create project → copy connection string → configure in FastAPI settings. Free: 100 CU-hours/month, 500 MB storage, scale-to-zero |
| Cache | **Upstash** (Free tier) | Create Redis database → copy REST URL and token → configure in FastAPI. Free: 500K commands/month, 256 MB |
| Monitoring | **LangSmith** (Developer plan) | Sign up → create project → set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` in environment. Free: 5K traces/month |

### Environment variables (stored in Render dashboard + GitHub Secrets)

```
# LLM Providers
GOOGLE_API_KEY=<gemini-api-key>
GROQ_API_KEY=<groq-api-key>
OPENROUTER_API_KEY=<openrouter-api-key>

# Travel APIs
AMADEUS_API_KEY=<key>
AMADEUS_API_SECRET=<secret>
UNSPLASH_ACCESS_KEY=<key>

# Infrastructure
DATABASE_URL=<neon-postgres-connection-string>
UPSTASH_REDIS_REST_URL=<url>
UPSTASH_REDIS_REST_TOKEN=<token>

# Monitoring
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<langsmith-key>
LANGCHAIN_PROJECT=ai-travel-concierge

# App Config
ENVIRONMENT=production
CORS_ORIGINS=https://your-app.vercel.app
```

### Keep-alive strategy for Render free tier

Render's free tier sleeps after 15 minutes of inactivity, causing **30-60 second cold starts**. Mitigation:

1. Sign up for **UptimeRobot** (free, 50 monitors) — ping `https://your-backend.onrender.com/api/health` every 14 minutes
2. Implement a lightweight `/api/health` endpoint that returns immediately without loading the full agent
3. Add a frontend loading state that displays "Waking up the server..." if the first request takes >5 seconds

---

## CI/CD setup with GitHub Actions

### Workflow architecture

The project uses **four workflow files** with path-based triggers to minimize wasted build minutes:

```
.github/workflows/
├── backend-ci.yml       # Runs on backend/ changes: ruff, mypy, pytest
├── frontend-ci.yml      # Runs on frontend/ changes: ESLint, tsc, Vitest
├── deploy-backend.yml   # Triggers Render deploy on merge to main
└── deploy-frontend.yml  # (Optional — Vercel auto-deploys via GitHub integration)
```

**Key CI configuration details**: The repo should be **public** to get unlimited free GitHub Actions minutes (private repos get only 2,000 min/month). Every workflow uses `concurrency` groups with `cancel-in-progress: true` to avoid redundant builds when pushing multiple commits. Python CI caches pip dependencies, Node CI caches `node_modules` via `actions/setup-node`'s built-in cache. Jobs set `timeout-minutes: 15` to prevent runaway builds.

The **backend CI** runs Ruff (linting + formatting check), mypy (type checking), and pytest (unit + integration tests with coverage reporting). The **frontend CI** runs ESLint, TypeScript compiler in check mode, Vitest for unit tests, and a build verification step.

### Branch strategy and protection

The team follows a **simplified Git flow**: feature branches → PRs to `develop` → periodic merges to `main` for production deployment. Branch protection on `main` requires 1 approving review, all CI status checks passing, and conversation resolution before merging. **Squash merges** keep the commit history clean.

### Pre-commit hooks

Python uses the `pre-commit` framework with Ruff for linting/formatting and basic file checks. JavaScript uses Husky + lint-staged for ESLint and Prettier. Both are installed during project setup and catch issues before they reach CI, saving build minutes and review time.

### Secrets management

All API keys are stored in GitHub repository secrets (Settings → Secrets → Actions) and referenced as `${{ secrets.SECRET_NAME }}` in workflow files. Environment-level secrets separate staging from production values. GitHub automatically masks secret values in logs.

---

## Testing strategy

### Testing pyramid for the travel concierge

The project follows a modified testing pyramid adapted for AI agent applications:

**Unit tests (60% of test effort)** form the foundation. Every tool function gets thorough unit tests using `pytest` with mocked external API responses. Tests verify correct parsing of API responses, error handling for failures and rate limits, edge cases like empty results or malformed data, and cache key generation. The `unittest.mock.patch` decorator replaces HTTP calls with predetermined responses, making tests fast and deterministic. Each tool should have **≥5 unit tests** covering happy path, empty results, API error, timeout, and malformed response scenarios.

**Integration tests (25% of test effort)** verify that components work together. FastAPI endpoint tests use `httpx.AsyncClient` with `ASGITransport` for async testing. Agent flow tests use LangChain's `GenericFakeChatModel` to create deterministic LLM responses, verifying that the agent selects the correct tool for each query type and handles multi-turn conversations correctly. VCR cassettes (via `pytest-recording`) record real API interactions once and replay them in CI for deterministic, fast integration tests.

**End-to-end tests (15% of test effort)** use Playwright to verify critical user journeys: sending a message and receiving a response, multi-turn conversation with context retention, trip planning flow from query to structured plan, and error handling when the backend is slow or returns errors. E2E tests run only on merge to `main` (not on every PR) to conserve build minutes.

### LLM-specific testing approaches

Non-deterministic LLM outputs require adapted testing strategies. Tests assert on **semantic properties** rather than exact text — checking that responses contain relevant keywords, that the correct tools were invoked, and that the response structure matches expectations. **Trajectory match evaluators** from the `agentevals` package verify tool-call sequences deterministically without requiring LLM calls. Prompt snapshot tests catch unintended prompt changes. The LangSmith pytest integration (`@pytest.mark.langsmith`) logs test results to LangSmith for longitudinal tracking of agent quality across code changes.

### Test commands and markers

```bash
# Fast local development
pytest -m unit                          # ~10 seconds
# PR CI pipeline
pytest -m "unit or integration"         # ~60 seconds
# Merge to main
pytest                                  # All tests including slow ones
# Manual evaluation
pytest -m llm                           # Tests hitting real LLM APIs
```

---

## Monitoring and observability

**LangSmith** serves as the primary monitoring tool with its native LangGraph integration. Setting two environment variables (`LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY`) automatically captures every agent invocation with full trace visibility: which tools were called, what arguments were passed, LLM token usage, latency per step, and error details. The **5,000 free traces/month** covers roughly 170 agent invocations per day — sufficient for development and demo usage.

Key metrics to monitor in LangSmith: **average response latency** (target: <5 seconds), **tool call success rate** (target: >95%), **LLM provider distribution** (tracking how often fallback providers are used), and **token usage per conversation** (to project free-tier runway).

If the team exceeds LangSmith's free tier, **Langfuse** (open-source, self-hostable) provides unlimited tracing. It integrates with LangGraph via a `CallbackHandler` and can be deployed as a Docker container alongside the main application.

---

## MVP pathway: what to build if time runs short

If the team falls behind schedule, the MVP is the non-negotiable minimum viable delivery:

- **3 tools minimum**: Weather (Open-Meteo), destination info (REST Countries), currency conversion (Frankfurter) — all require zero API keys and have unlimited free usage
- **Single ReAct agent** (no supervisor pattern needed for MVP)
- **Basic chat UI**: Text input, message display with streaming, no trip dashboard
- **Gemini only** (no fallback providers)
- **Local SQLite** instead of Neon PostgreSQL
- **No Redis caching** (direct API calls are fine at MVP scale)
- **Manual deployment** (no CI/CD — just push to Vercel/Render)

This stripped-down MVP can be built by **2 people in 2 weeks** and still demonstrates the core value proposition: a conversational AI agent that integrates multiple travel data sources.

---

## Stakeholder questions checklist

Before each sprint begins, the team should resolve these questions:

**Sprint 1 kickoff questions:**
- [ ] Has every team member successfully run both frontend and backend locally?
- [ ] Are all free-tier accounts created? (Google AI Studio, Groq, Amadeus, Neon, Upstash, Render, Vercel, LangSmith, Unsplash)
- [ ] Is the GitHub repo created with branch protection enabled?
- [ ] Have we agreed on communication cadence? (Daily async standup, weekly sync?)
- [ ] Who is the primary contact for questions/blockers with the instructor/advisor?

**Sprint 2 kickoff questions:**
- [ ] Is the MVP deployed and accessible via public URL?
- [ ] Are we on track with free-tier usage? Check Gemini, Amadeus, and Upstash dashboards
- [ ] Are there any tools that consistently return empty/poor results from Amadeus test data?
- [ ] Do we need to adjust the tool priority list based on Sprint 1 learnings?

**Sprint 3 kickoff questions:**
- [ ] Has the MVP been demoed to at least one person outside the team for feedback?
- [ ] Is the supervisor pattern refactor justified, or does the single ReAct agent work well enough?
- [ ] Are we hitting any free-tier limits that require architectural changes?
- [ ] What features from Sprint 3-4 can we cut if behind schedule?

**Sprint 4 kickoff questions:**
- [ ] Is the application stable enough for a live demo?
- [ ] Do we have a backup demo plan if the live API fails during presentation?
- [ ] Is all documentation written and reviewed?
- [ ] Has the evaluation dataset been finalized and all test cases verified?

---

## Progress update template

Use this template for weekly progress updates (posted to team channel every Friday):

```markdown
## Week [N] Progress Update — [Date]

### 🎯 Sprint [N] Goal: [One-line sprint goal]

### ✅ Completed this week
- [Task]: [Who] — [One-line description of what was delivered]
- [Task]: [Who] — [One-line description]

### 🔄 In progress
- [Task]: [Who] — [Expected completion date] — [% complete]
- [Task]: [Who] — [Expected completion date] — [% complete]

### 🚫 Blocked
- [Blocker description] — [Who is affected] — [What's needed to unblock]

### 📊 Key metrics
- Free-tier usage: Gemini [X/250 RPD], Amadeus [X/2K calls], Upstash [X/500K cmds]
- Test coverage: Backend [X%], Frontend [X%]
- Open PRs: [N], Open issues: [N]
- Deployed: [Yes/No] — Last deploy: [date]

### 🔮 Next week priorities
1. [Highest priority task]
2. [Second priority]
3. [Third priority]

### ⚠️ Risks or concerns
- [Any new risks identified this week]
```

---

## Conclusion: three keys to shipping on time

This project is achievable within 8 weeks precisely because the free-tier ecosystem in 2026 is remarkably capable. **Open-Meteo, REST Countries, and Frankfurter require zero authentication** and provide unlimited calls — the team can have three working tools before writing a single line of auth code. The biggest technical risk is not the tools themselves but **LLM rate limits**: with Gemini capped at 250 requests/day, every unnecessary LLM call burns runway. Aggressive caching through Upstash Redis and a robust three-tier provider fallback are not nice-to-haves — they are architectural necessities.

The second key is **ruthless scope management**. The supervisor multi-agent pattern is elegant but unnecessary for the MVP. Start with a single ReAct agent, ship it by Week 4, and only refactor to the supervisor pattern in Sprint 3 if the single agent is struggling with tool selection accuracy. If it works well with 6 tools, skip the refactor and invest that time in UI polish and testing instead.

The third key is **deploying on Day 10, not Day 50**. The moment the first tool works, deploy it. Render and Vercel take under 10 minutes to configure. Early deployment surfaces integration issues (CORS, environment variables, cold starts) that are trivial to fix early but painful to debug in the final week. The keep-alive ping for Render's sleep behavior, the Gemini EU restriction, and Amadeus's limited test data are all surprises that are better discovered in Sprint 1 than Sprint 4.