# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **full-stack LangGraph + Gemini 2.5 Flash + React** multi-agent forex/commodity/crypto trading analysis system. The architecture consists of:

- **Backend**: Python FastAPI with SSE (Server-Sent Events) streaming
- **Frontend**: React + TypeScript + Vite with real-time streaming UI
- **AI Engine**: LangGraph orchestrating specialized agents with Gemini 2.5 Flash
- **Deployment**: Fly.io (backend) + Railway (frontend)

### Key Architecture Concepts

**Multi-Tier Architecture**:
- Backend (Python): LangGraph workflow with parallel agent execution
- Frontend (React): Real-time streaming interface with agent visualization
- API Layer: FastAPI with SSE for live progress updates

**Agent Flow** (Backend):
1. **Query Parser Node** (Gemini) - Converts natural language to structured context
2. **Parallel Analysis Node** - News, Technical, and Fundamental agents run simultaneously (3x faster than v1)
3. **Risk Agent** - Validates trade parameters and position sizing
4. **Synthesis Agent** (Gemini + Google Search) - Final decision with citations

**Critical**: Agents run in parallel using `ThreadPoolExecutor`. This is NOT parallelizable via multi-process due to API I/O-bound operations.

### State Management

**Backend**: LangGraph's `StateGraph` with `ForexAgentState` (defined in `graph/state.py`). State flows through:
- `user_query` (raw input) → `query_context` (parsed JSON) → agent results → final decision

**Frontend**: React hooks (`useForexAnalysis.ts`) manage streaming state with per-agent tracking:
- Connection management via EventSource (SSE)
- Real-time progress updates for each agent
- Automatic reconnection and error handling

**Backwards Compatibility**: The `pair` field is deprecated but maintained for compatibility.

## Common Development Commands

### Setup and Installation

```bash
# Backend setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add GOOGLE_AI_API_KEY from https://aistudio.google.com/app/apikey

# Frontend setup
cd frontend
npm install
cd ..

# Or install everything at once
npm run install:frontend
```

### Running the System

```bash
# Run full stack (backend + frontend)
npm run dev

# Run backend only
python backend/server.py
# OR
uvicorn backend.server:app --reload

# Run frontend only
cd frontend && npm run dev

# Run CLI analysis (no UI)
python main.py "Analyze gold trading"
python main.py EUR/USD
```

### Building and Deployment

```bash
# Build frontend for production
npm run build:frontend

# Preview production build
npm run preview:frontend

# Build with TypeScript check
cd frontend && npm run build:check

# Deploy backend to Fly.io
fly deploy

# Deploy frontend to Railway
# (Automatic on git push with Railway GitHub integration)
```

### Testing

```bash
# Backend tests
python test_basic.py                 # Core workflow validation
python test_streaming_api.py         # API streaming tests
python test_api_auth.py              # API authentication tests
python test_price_api.py             # Price API integration

# Run all Python tests
pytest

# Run with verbose output
pytest -v

# Test streaming API (requires server running)
# Terminal 1:
python backend/server.py
# Terminal 2:
python test_streaming_api.py
```

### Development Workflow

```bash
# Interactive backend testing
python
>>> from system import ForexAgentSystem
>>> system = ForexAgentSystem()
>>> result = system.analyze("EUR/USD")

# Frontend development with hot reload
cd frontend && npm run dev

# Type checking only (no build)
cd frontend && npx tsc --noEmit
```

## Architecture Deep Dive

### Backend: LangGraph Workflow

The workflow is defined in `graph/workflow.py` and uses these nodes:

1. **query_parser** (`graph/query_parser.py`):
   - Transforms natural language → structured JSON
   - Uses Gemini 2.5 Flash with low temperature (0.1)
   - Falls back to regex parsing if API fails
   - Extracts: pair, asset_type, timeframe, user_intent, risk_tolerance

2. **parallel_analysis** (`graph/parallel_nodes.py`):
   - Executes 3 agents simultaneously with `ThreadPoolExecutor`
   - News Agent (`agents/news_agent.py`) - Currently returns mock sentiment data
   - Technical Agent (`agents/technical_agent.py`) - Mock RSI, MACD, moving averages
   - Fundamental Agent (`agents/fundamental_agent.py`) - Mock GDP, interest rates, inflation

3. **risk** (`graph/nodes.py::risk_node`):
   - Uses RiskAgent (`agents/risk_agent.py`) with real LLM-powered analysis
   - Validates stop loss distance (10-100 pips)
   - Calculates position sizing based on account balance
   - Checks risk/reward ratio (minimum 1.5:1)
   - Returns `trade_approved: bool`

4. **synthesis** (`graph/nodes.py::synthesis_node`):
   - Only runs if risk approved (conditional routing)
   - Uses Gemini 2.5 Flash with Google Search grounding
   - Returns structured decision: BUY/SELL/WAIT
   - Includes reasoning, trade parameters, and source citations

### Frontend: React + TypeScript Architecture

**Component Structure** (`frontend/src/components/`):
- `ChatInterface.tsx` - Main query input and analysis trigger
- `AgentCard.tsx` - Individual agent status display
- `ParallelAgentsSection.tsx` - Real-time parallel execution visualization
- `AgentExecutionDetails.tsx` - Detailed agent results with web sources
- `ReasoningTimeline.tsx` - Sequential timeline of analysis steps
- `ComprehensiveReport.tsx` - Final decision and trade parameters
- `SocialMediaShare.tsx` - Social media post generation

**Custom Hooks** (`frontend/src/hooks/`):
- `useForexAnalysis.ts` - Main streaming API hook with:
  - Per-agent state tracking (status, progress, messages)
  - EventSource connection management
  - Automatic reconnection on disconnect
  - Type-safe event parsing

**Key Frontend Patterns**:
- Uses `EventSource` for SSE streaming (not WebSocket)
- State updates are granular per agent for smooth UI transitions
- Framer Motion for timeline animations
- Radix UI components for accessibility
- Tailwind CSS with shadcn/ui design system

### API Layer: FastAPI + SSE Streaming

**Server** (`backend/server.py`):
- FastAPI with CORS middleware for frontend access
- Multiple CORS origins (localhost dev + Railway production)
- Health check endpoint at `/health`
- Streaming endpoint at `/analyze/stream`

**Streaming Adapter** (`backend/streaming_adapter.py`):
- Wraps `ForexAgentSystem` with streaming callbacks
- Emits SSE events: start, query_parsed, agent_update, risk_update, decision, complete, error
- Event format: `event: {type}\ndata: {json}\n\n`

**API Endpoints**:
- `GET /health` - Health check
- `GET /info` - System information
- `POST /analyze` - Non-streaming analysis (returns full result)
- `POST /analyze/stream` - Real-time streaming (SSE)
- `GET /analyze/stream?query=...` - Streaming with GET (preferred for EventSource)

### Conditional Routing

**After Risk Node**:
- `should_continue_after_risk()` checks if `risk_result.data.trade_approved == True`
- If False, workflow ends immediately with WAIT decision
- If True, proceeds to synthesis

### Agent Implementation Pattern

All agents follow this pattern:
```python
class SomeAgent:
    def analyze(self, pair: str, query_context: Dict = None) -> Dict[str, Any]:
        try:
            # Perform analysis
            return {
                "success": True,
                "data": {...},
                "summary": "..."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

**Critical**: Agents must handle exceptions gracefully and return structured responses.

## File Organization

```
fx-agent/
├── agents/                      # Agent implementations
│   ├── news_agent.py           # News/sentiment (mock data)
│   ├── technical_agent.py      # Technical indicators (mock)
│   ├── fundamental_agent.py    # Economic fundamentals (mock)
│   ├── risk_agent.py          # Position sizing (LLM-powered)
│   └── price_service.py       # Real-time price fetching
│
├── graph/                      # LangGraph workflow components
│   ├── state.py               # State definition (ForexAgentState)
│   ├── workflow.py            # Workflow builder and compilation
│   ├── query_parser.py        # Natural language → JSON parser
│   ├── parallel_nodes.py      # Parallel agent execution
│   └── nodes.py               # Individual workflow nodes
│
├── backend/                    # FastAPI streaming API
│   ├── server.py              # Main API server with CORS
│   └── streaming_adapter.py   # Streaming wrapper for ForexAgentSystem
│
├── frontend/                   # React TypeScript application
│   ├── src/
│   │   ├── App.tsx            # Main app component
│   │   ├── components/        # UI components
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── AgentCard.tsx
│   │   │   ├── ParallelAgentsSection.tsx
│   │   │   ├── AgentExecutionDetails.tsx
│   │   │   ├── ReasoningTimeline.tsx
│   │   │   ├── ComprehensiveReport.tsx
│   │   │   └── SocialMediaShare.tsx
│   │   ├── hooks/
│   │   │   └── useForexAnalysis.ts  # Streaming hook
│   │   ├── types/
│   │   │   └── forex-api.ts   # TypeScript types
│   │   └── lib/               # Utilities
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile             # Frontend deployment
│   └── .env.example
│
├── utils/                      # Shared utilities
│   ├── social_formatter.py    # Social media post formatting
│   └── logger.py              # Logging configuration
│
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md        # System architecture details
│   ├── STREAMING_API.md       # API documentation
│   └── agents/                # Agent-specific docs
│
├── system.py                  # Main ForexAgentSystem class
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
├── package.json               # Root package (concurrently scripts)
├── Dockerfile                 # Backend deployment
├── fly.toml                   # Fly.io configuration
└── .env.example              # Environment template
```

## Environment Configuration

### Backend (.env)

**Required**:
- `GOOGLE_AI_API_KEY` - Get from https://aistudio.google.com/app/apikey

**Optional (Price APIs)**:
- `METAL_PRICE_API_KEY` - From https://metalpriceapi.com/ (free tier)
- `FOREX_RATE_API_KEY` - From https://forexrateapi.com/ (free tier)

**Optional (Trading)**:
- `ACCOUNT_BALANCE` - Default: 10000.0
- `MAX_RISK_PER_TRADE` - Default: 0.02 (2%)

**Optional (API Server)**:
- `API_HOST` - Default: 0.0.0.0
- `API_PORT` - Default: 8000
- `API_RELOAD` - Default: true

### Frontend (.env in frontend/)

**Required**:
- `VITE_API_URL` - Backend API URL (e.g., `http://localhost:8000` or `https://your-backend.fly.dev`)

**Note**: Vite requires `VITE_` prefix for environment variables to be exposed to the client.

## Deployment Architecture

### Backend: Fly.io

- **Configuration**: `fly.toml` and `Dockerfile`
- **Health checks**: `/health` endpoint checked every 30s
- **Auto-scaling**: Machines stop when idle, auto-start on request
- **Region**: San Jose (SJC)
- **Resources**: 1 CPU, 1GB RAM

**Deploy Command**:
```bash
fly deploy
```

**Set secrets**:
```bash
fly secrets set GOOGLE_AI_API_KEY=your_key_here
```

### Frontend: Railway

- **Configuration**: `frontend/Dockerfile` with Vite preview server
- **Build**: Multi-stage Docker build with pnpm
- **Root Directory**: Set to `frontend` in Railway dashboard
- **Environment**: `VITE_API_URL` set to Fly.io backend URL

**Important**: Railway must have Root Directory set to `frontend` in service settings.

### CORS Configuration

Backend allows these origins (`backend/server.py`):
- `http://localhost:3000` - Local dev
- `http://localhost:5173` - Vite dev server
- `https://forex-agent-frontend-production.up.railway.app` - Production

Add new origins by updating `allow_origins` in CORS middleware.

## Key Design Decisions

### Why Full-Stack with Separate Deployments?

- **Scalability**: Backend (compute-heavy) and frontend (static) scale independently
- **Cost**: Fly.io auto-stops idle machines; Railway serves static frontend efficiently
- **Development**: Backend and frontend can be developed and deployed separately

### Why SSE Instead of WebSocket?

- **Unidirectional**: Analysis is server → client only (no client → server during stream)
- **Simplicity**: EventSource API is simpler than WebSocket
- **HTTP/2**: Better performance with modern browsers
- **Reconnection**: Built-in automatic reconnection

### Why Parallel Agent Execution?

- News, Technical, and Fundamental agents are independent
- 3x performance improvement (6s → 2s)
- Uses ThreadPoolExecutor (suitable for I/O-bound API calls)

### Why Mock Data in Most Agents?

This is a demonstration project focusing on:
- Agent orchestration architecture
- LangGraph workflow patterns
- Gemini integration with Google Search grounding
- Full-stack streaming implementation

Real data integration is intentionally left as a future enhancement.

### Why Gemini Instead of OpenAI?

- **Google Search Grounding**: Built-in web search with citations
- **Cost**: Flash 2.5 is significantly cheaper than GPT-4
- **Performance**: Fast response times for synthesis
- **Free Tier**: Generous free quota for development

## Extending the System

### Adding a New Agent

1. Create agent class in `agents/new_agent.py`
2. Add node function in `graph/nodes.py` or `graph/parallel_nodes.py`
3. Update `ForexAgentState` in `graph/state.py` to include result field
4. Modify workflow in `graph/workflow.py` to include the new node
5. Update `system.py::_format_result()` to include agent results
6. Add frontend state in `useForexAnalysis.ts` for streaming updates
7. Create React component in `frontend/src/components/` to display results

### Adding Real Data Sources

Replace mock data in agents with real API calls:
- **News**: NewsAPI, Alpha Vantage, Finnhub
- **Technical**: Yahoo Finance, Alpha Vantage, TradingView
- **Fundamental**: FRED API, Trading Economics

**Pattern**: Keep the same return structure (`{success, data, summary}`)

### Modifying Agent Prompts

Agent prompts for LLM-powered agents are in:
- Risk Agent: `agents/risk_agent.py::_build_analysis_prompt()`
- Synthesis Agent: `graph/nodes.py::synthesis_node()`

### Adding Frontend Features

1. **New Component**: Create in `frontend/src/components/`
2. **Use Streaming State**: Import `useForexAnalysis` hook
3. **Type Definitions**: Update `frontend/src/types/forex-api.ts`
4. **Styling**: Use Tailwind classes and shadcn/ui components

Example:
```typescript
import { useForexAnalysis } from '../hooks/useForexAnalysis';

function MyComponent() {
  const { state, analyze } = useForexAnalysis({
    apiUrl: import.meta.env.VITE_API_URL
  });

  // Access state.agents.news, state.decision, etc.
}
```

### Testing Changes

Always run after backend changes:
```bash
python test_basic.py          # Core workflow
python test_streaming_api.py  # Streaming API
```

Always run after frontend changes:
```bash
cd frontend && npx tsc --noEmit  # Type checking
cd frontend && npm run build     # Production build test
```

## Common Gotchas

### Backend

1. **API Keys in Environment**: The system loads `.env` at startup. Changes to `.env` require restarting the server.

2. **Parallel vs Sequential**: Do NOT modify `parallel_analysis_node` to run sequentially. The 3x performance gain is critical.

3. **State Immutability**: LangGraph nodes return state updates, they don't modify state directly. Always return a dict with changed fields.

4. **Error Handling**: Agents should NEVER raise exceptions. They must return `{success: False, error: "..."}` to allow the workflow to continue.

5. **Query Context**: New code should use `query_context` from state, not just `pair`. The `pair` field is deprecated.

6. **CORS**: When deploying to new domains, update `allow_origins` in `backend/server.py`.

### Frontend

1. **Environment Variables**: Must use `VITE_` prefix. Changes require restart of dev server.

2. **EventSource Connection**: Always close EventSource when component unmounts to prevent memory leaks. The `useForexAnalysis` hook handles this.

3. **API URL**: Must match backend deployment. For local dev: `http://localhost:8000`. For production: full Fly.io URL.

4. **SSE Event Types**: Event names must match backend emitter. See `backend/streaming_adapter.py` for event types.

5. **TypeScript Types**: Keep `frontend/src/types/forex-api.ts` synchronized with backend response structure.

### Deployment

1. **Fly.io Secrets**: Use `fly secrets set` for sensitive values, not environment variables in `fly.toml`.

2. **Railway Root Directory**: Must be set to `frontend` in Railway dashboard. Default root won't work.

3. **Build Errors**: Frontend build fails if types don't match. Run `npx tsc --noEmit` locally first.

4. **CORS Origins**: Production URLs must be added to backend CORS configuration before deployment.

## Cost Considerations

### Per Analysis (~$0.095 total)

- Query Parser: ~$0.001 (Gemini 2.5 Flash, low tokens)
- Agent Execution: FREE (mock data, no API calls)
- Risk Agent: ~$0.002 (Gemini 2.5 Flash)
- Synthesis: ~$0.080 (Gemini 2.5 Flash + longer context)
- Google Search Grounding: ~$0.015 (included with Gemini)

100 analyses/day = ~$9.50/day = $285/month

### Infrastructure

- **Fly.io**: ~$0-5/month (auto-stops when idle)
- **Railway**: ~$5-10/month (static frontend)
- **Total**: ~$5-15/month + API costs

**Optimization**: Use caching for repeated queries, implement rate limiting.

## Social Media Integration

The system includes social media post formatting via `utils/social_formatter.py`:

```python
from utils.social_formatter import format_for_twitter, format_for_telegram, format_for_facebook

result = system.analyze("EUR/USD")

twitter_post = format_for_twitter(result)  # 280 char limit
telegram_post = format_for_telegram(result, channel_name="FX Signals")
facebook_post = format_for_facebook(result, educational_context=True)
```

Features:
- Platform-specific formatting and character limits
- Automatic disclaimers (NFA, DYOR)
- Conditional trade parameters (only for BUY/SELL)
- Professional trader voice

## Version History

**v1 (Initial)**: Sequential execution, exact pair format only, CLI only
**v2 (Current)**: Parallel execution, natural language queries, 3x faster, streaming API, React frontend

See `docs/ARCHITECTURE.md` for detailed v1 → v2 evolution.
