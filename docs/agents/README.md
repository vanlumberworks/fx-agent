# Agent Flow Documentation

Comprehensive documentation for all agents and components in the VibeTrade Claude trading analysis system.

**Last Updated**: November 6, 2025
**System Version**: v2 (Parallel Execution + Natural Language Queries)

## Overview

This system uses **LangGraph** to orchestrate multiple specialized agents that analyze trading opportunities. Each agent has a specific role, and they work together in a structured workflow.

## System Architecture

```
User Query → Query Parser → [News + Technical + Fundamental] → Risk → Synthesis → Final Decision
                            └──────── Parallel ────────┘        │
                                                           Gatekeeper
```

### Workflow Phases

1. **Query Parsing** (500ms): Transform natural language → structured context
2. **Parallel Analysis** (2s): News, Technical, and Fundamental agents run simultaneously
3. **Risk Validation** (500ms): Calculate position sizing, validate trade parameters
4. **Synthesis** (5s): Make final decision with Google Search verification

**Total Time**: ~8 seconds per analysis

## Agent Documentation

### Core Agents

#### [1. Query Parser Agent](./01_query_parser.md)
**Role**: Entry point - parses natural language queries

**Key Features**:
- Transforms "Analyze gold" → `{"pair": "XAU/USD", "asset_type": "commodity"}`
- Uses Gemini 2.5 Flash with low temperature (0.1)
- Regex fallback for reliability
- Backwards compatible with v1

**Performance**:
- Latency: ~300-800ms
- Cost: ~$0.001
- Success Rate: >95%

**[Read detailed documentation →](./01_query_parser.md)**

---

#### [2. News Agent](./02_news_agent.md)
**Role**: Analyze market news and sentiment

**Key Features**:
- Real-time headlines via Google Search (not mock!)
- Sentiment analysis (-1.0 to +1.0)
- Impact assessment (high/medium/low)
- Source citations
- Async execution (parallel)

**Performance**:
- Latency: ~2-4 seconds
- Cost: ~$0.015-0.025
- Success Rate: >90%

**[Read detailed documentation →](./02_news_agent.md)**

---

#### [3. Technical Agent](./03_technical_agent.md)
**Role**: Technical analysis with LLM reasoning

**Key Features**:
- Real-time prices from Price Service
- Historical context (24h change, OHLC)
- LLM-powered analysis (not just math)
- Support/resistance calculation
- Trading signals (BUY/SELL/HOLD)
- Optional Google Search for technical insights
- Async execution (parallel)

**Performance**:
- Latency: ~2-4 seconds (LLM mode)
- Cost: ~$0.020-0.030
- Success Rate: >90%

**[Read detailed documentation →](./03_technical_agent.md)**

---

#### [4. Fundamental Agent](./04_fundamental_agent.md)
**Role**: Economic fundamental analysis

**Key Features**:
- Real-time economic data via Google Search
- Compare base vs quote currency fundamentals
- Fundamental score (-1.0 to +1.0)
- Central bank policy analysis
- Outlook (bullish/bearish/neutral)
- Async execution (parallel)

**Performance**:
- Latency: ~3-5 seconds
- Cost: ~$0.025-0.035
- Success Rate: ~85-90%

**[Read detailed documentation →](./04_fundamental_agent.md)**

---

#### [5. Risk Agent](./05_risk_agent.md)
**Role**: GATEKEEPER - validates trades and calculates position sizing

**Key Features**:
- Mathematical position sizing
- Trade validation (4 rules: risk pips, R:R ratio, etc.)
- Can REJECT trades (stops workflow)
- Optional LLM enhancement for market context
- Conditional workflow routing

**Performance**:
- Latency: ~10-50ms (rule-based), ~2-4s (LLM-enhanced)
- Cost: $0 (rule-based), ~$0.025 (LLM)
- Success Rate: ~98%

**Critical**: If Risk Agent rejects trade, workflow ends immediately with WAIT decision.

**[Read detailed documentation →](./05_risk_agent.md)**

---

#### [6. Synthesis Agent](./06_synthesis_agent.md)
**Role**: DECISION MAKER - final BUY/SELL/WAIT decision

**Key Features**:
- Synthesizes all agent outputs
- Verifies mock data against real-time web sources
- Google Search grounding for confidence
- Comprehensive reasoning with citations
- Conservative bias (WAIT when uncertain)

**Performance**:
- Latency: ~4-6 seconds (longest node)
- Cost: ~$0.080-0.120 (80% of total cost)
- Success Rate: ~95%

**Decision Distribution**: ~30% BUY, ~30% SELL, ~40% WAIT

**[Read detailed documentation →](./06_synthesis_agent.md)**

---

### Supporting Components

#### [7. Price Service](./07_price_service.md)
**Role**: Fetch real-time price data

**Key Features**:
- Multi-API support (Metal Price API + Forex Rate API)
- Automatic routing by asset type
- Enriched price data (current + historical + OHLC)
- Smart caching (1-minute TTL)
- Singleton pattern

**Performance**:
- Latency: ~300-800ms (uncached), ~1-5ms (cached)
- Cache Speedup: Up to 500x

**[Read detailed documentation →](./07_price_service.md)**

---

#### [8. Parallel Execution](./08_parallel_execution.md)
**Role**: Run News, Technical, and Fundamental agents simultaneously

**Key Features**:
- Asyncio-based concurrent execution
- 3x speedup (6s → 2s)
- Resilient to individual agent failures
- State merging and error aggregation

**Performance**:
- Analysis Phase: 6000ms → 2000ms (3x faster)
- Overall Speedup: 1.5x (12s → 8s)

**[Read detailed documentation →](./08_parallel_execution.md)**

---

## Quick Links

| Document | Description |
|----------|-------------|
| [Query Parser](./01_query_parser.md) | Natural language query parsing |
| [News Agent](./02_news_agent.md) | Market news and sentiment analysis |
| [Technical Agent](./03_technical_agent.md) | Technical analysis with LLM |
| [Fundamental Agent](./04_fundamental_agent.md) | Economic fundamentals |
| [Risk Agent](./05_risk_agent.md) | Position sizing and trade validation |
| [Synthesis Agent](./06_synthesis_agent.md) | Final decision making |
| [Price Service](./07_price_service.md) | Real-time price data fetching |
| [Parallel Execution](./08_parallel_execution.md) | Concurrent agent execution |

## Agent Details (Legacy)

### 1. News Agent

**File**: `agents/news_agent.py`

**Purpose**: Analyze market news and sentiment for a trading pair

**Technology**: Gemini 2.5 Flash + Google Search grounding

**Execution**: Async

**Input**:
```python
pair = "EUR/USD"
query_context = {"asset_type": "forex", "timeframe": "short_term"}
```

**Output**:
```json
{
  "success": true,
  "agent": "NewsAgent",
  "data": {
    "headlines": [
      {
        "title": "ECB Holds Rates Steady",
        "date": "2025-11-05",
        "sentiment": "neutral",
        "source": "Reuters",
        "impact": "medium"
      }
    ],
    "overall_sentiment": "neutral",
    "sentiment_score": 0.0,
    "market_impact": "medium",
    "news_count": 4,
    "sources": [
      {"title": "...", "url": "https://..."}
    ],
    "search_queries": ["EUR/USD forex news", "EUR central bank"],
    "data_source": "google_search"
  },
  "summary": "Neutral market sentiment with moderate impact..."
}
```

**Key Features**:
- ✅ Real headlines from Google Search
- ✅ Sentiment analysis (bullish/bearish/neutral)
- ✅ Market impact assessment (high/medium/low)
- ✅ Source citations for transparency
- ✅ Async execution for performance

**Usage**:
```python
from agents.news_agent import NewsAgent
import asyncio

agent = NewsAgent()
result = await agent.analyze("EUR/USD")
print(result["data"]["sentiment"])  # "bullish"
```

**Cost**: ~$0.015 per analysis (Google Search)

---

### 2. Technical Agent

**File**: `agents/technical_agent.py`

**Purpose**: Analyze price data, technical indicators, and trading signals

**Technology**: Gemini 2.5 Flash + Price APIs + Historical Data

**Execution**: Sync (calls Price Service)

**Data Sources**:
- Metal Price API (commodities)
- Forex Rate API (forex + crypto)
- Historical rates and OHLC data

**Input**:
```python
pair = "XAU/USD"
use_real_prices = True  # Enable real price fetching
use_llm = True  # Enable LLM analysis
```

**Output**:
```json
{
  "success": true,
  "agent": "TechnicalAgent",
  "data": {
    "current_price": 2641.50,
    "price_source": "real",
    "bid": 2641.00,
    "ask": 2642.00,
    "trend": "uptrend",
    "trend_strength": "medium",
    "support": 2620.00,
    "resistance": 2680.00,
    "indicators": {
      "rsi": 65,
      "macd": "bullish",
      "ma_position": "above_50ma"
    },
    "signals": {
      "buy": "strong",
      "sell": "weak",
      "overall": "BUY",
      "confidence": 0.75
    },
    "stop_loss": 2600.00,
    "take_profit": 2700.00,
    "historical": {
      "yesterday_rate": 2628.00,
      "price_change": 13.50,
      "price_change_pct": 0.51
    },
    "ohlc": {
      "open": 2628.00,
      "high": 2650.00,
      "low": 2620.00,
      "close": 2641.50,
      "date": "yesterday"
    },
    "analysis": "Technical analysis shows strong uptrend...",
    "reasoning": "Buy signal based on..."
  },
  "summary": "BUY signal with 75% confidence..."
}
```

**Key Features**:
- ✅ Real-time price data
- ✅ Historical context (24h change, OHLC)
- ✅ LLM analyzes technical patterns
- ✅ Support/resistance calculation
- ✅ Trading signals with confidence scores
- ✅ Fallback to mock data if APIs unavailable

**Usage**:
```python
from agents.technical_agent import TechnicalAgent

# With real prices and LLM
agent = TechnicalAgent(use_real_prices=True, use_llm=True)
result = agent.analyze("XAU/USD")

print(f"Price: ${result['data']['current_price']}")
print(f"Signal: {result['data']['signals']['overall']}")
print(f"Source: {result['data']['price_source']}")  # "real" or "mock"
```

**Cost**: ~$0.002 per analysis (Gemini only, Price APIs are free tier)

---

### 3. Fundamental Agent

**File**: `agents/fundamental_agent.py`

**Purpose**: Analyze economic fundamentals for base and quote currencies

**Technology**: Gemini 2.5 Flash + Google Search grounding

**Execution**: Async

**Input**:
```python
pair = "EUR/USD"
query_context = {"asset_type": "forex"}
```

**Output**:
```json
{
  "success": true,
  "agent": "FundamentalAgent",
  "data": {
    "base_currency": {
      "currency": "EUR",
      "gdp_growth": 1.8,
      "inflation": 2.8,
      "interest_rate": 4.0,
      "unemployment": 6.5,
      "central_bank": "ECB maintaining current policy stance...",
      "recent_events": ["ECB meeting", "EU economic report"]
    },
    "quote_currency": {
      "currency": "USD",
      "gdp_growth": 2.5,
      "inflation": 3.2,
      "interest_rate": 5.25,
      "unemployment": 3.8,
      "central_bank": "Fed maintaining restrictive policy..."
    },
    "comparison": {
      "gdp_growth": "quote_stronger",
      "inflation": "quote_higher",
      "interest_rate": "quote_stronger",
      "overall": "USD has stronger fundamentals"
    },
    "fundamental_score": -0.35,
    "outlook": "bearish",
    "key_factors": [
      "Interest rate differential of 125 bps favors USD",
      "Stronger GDP growth in US",
      "Central bank policy divergence"
    ],
    "analysis": "Fundamental analysis shows USD has superior economic indicators...",
    "reasoning": "Bearish outlook for EUR/USD based on...",
    "sources": [
      {"title": "...", "url": "https://..."}
    ],
    "search_queries": ["EUR economy", "USD economy", "EUR USD interest rates"],
    "data_source": "google_search"
  },
  "summary": "Bearish outlook (-0.35) due to USD strength..."
}
```

**Key Features**:
- ✅ Real economic data from Google Search
- ✅ GDP, inflation, interest rates, unemployment
- ✅ Central bank policy analysis
- ✅ Base vs quote currency comparison
- ✅ Fundamental score (-1.0 to +1.0)
- ✅ Supports forex, commodities, and crypto
- ✅ Source citations

**Usage**:
```python
from agents.fundamental_agent import FundamentalAgent
import asyncio

agent = FundamentalAgent()
result = await agent.analyze("EUR/USD")

print(f"Score: {result['data']['fundamental_score']}")  # -0.35
print(f"Outlook: {result['data']['outlook']}")  # "bearish"
```

**Cost**: ~$0.015 per analysis (Google Search)

---

### 4. Risk Agent

**File**: `agents/risk_agent.py`

**Purpose**: Validate trade parameters and calculate position sizing

**Technology**: Gemini 2.5 Flash

**Execution**: Sync

**Input**:
```python
pair = "EUR/USD"
entry_price = 1.0850
stop_loss = 1.0780
take_profit = 1.0980
account_balance = 10000.0
max_risk_per_trade = 0.02  # 2%
```

**Output**:
```json
{
  "success": true,
  "agent": "RiskAgent",
  "data": {
    "trade_approved": true,
    "position_size": 0.20,
    "stop_loss": 1.0780,
    "take_profit": 1.0980,
    "risk_amount": 200.00,
    "risk_percent": 2.0,
    "reward_amount": 300.00,
    "risk_reward_ratio": 1.5,
    "stop_loss_pips": 70,
    "take_profit_pips": 130,
    "max_loss": 200.00,
    "max_gain": 300.00,
    "reasoning": "Trade meets all risk parameters. Stop loss at 70 pips, take profit at 130 pips. Risk/reward ratio of 1.5:1 is acceptable. Position size calculated to risk exactly 2% of account balance.",
    "validation": {
      "stop_loss_valid": true,
      "risk_reward_valid": true,
      "position_size_valid": true
    }
  },
  "summary": "Trade approved. Risk: $200 (2.0%), Position: 0.20 lots"
}
```

**Key Features**:
- ✅ LLM-powered risk analysis
- ✅ Position sizing based on account balance
- ✅ Stop loss validation (10-100 pips)
- ✅ Risk/reward ratio check (minimum 1.5:1)
- ✅ Maximum risk per trade enforcement
- ✅ Detailed reasoning for approval/rejection

**Usage**:
```python
from agents.risk_agent import RiskAgent

agent = RiskAgent(
    account_balance=10000.0,
    max_risk_per_trade=0.02  # 2%
)

result = agent.validate_trade(
    pair="EUR/USD",
    entry_price=1.0850,
    stop_loss=1.0780,
    take_profit=1.0980
)

if result["data"]["trade_approved"]:
    print(f"Position size: {result['data']['position_size']} lots")
else:
    print(f"Rejected: {result['data']['rejection_reason']}")
```

**Cost**: ~$0.002 per analysis

---

### 5. Synthesis Agent

**File**: `graph/nodes.py::synthesis_node()`

**Purpose**: Make final trading decision based on all agent inputs

**Technology**: Gemini 2.5 Flash + Google Search grounding

**Execution**: Async

**Input**: All agent results from state
- News result
- Technical result
- Fundamental result
- Risk result

**Output**:
```json
{
  "action": "BUY",
  "confidence": 0.82,
  "reasoning": {
    "summary": "Strong BUY signal based on technical uptrend, positive fundamentals, and neutral news sentiment.",
    "web_verification": "Google Search confirms current market conditions support upward movement.",
    "key_factors": [
      "Technical: Uptrend with 75% confidence",
      "Fundamental: Positive economic indicators",
      "News: Neutral to slightly bullish sentiment",
      "Risk: Trade parameters validated"
    ],
    "risks": [
      "Market volatility remains elevated",
      "Economic data releases pending"
    ]
  },
  "trade_parameters": {
    "entry_price": 1.0850,
    "stop_loss": 1.0780,
    "take_profit": 1.0980,
    "position_size": 0.20
  },
  "grounding_metadata": {
    "search_queries": [
      "EUR/USD live price",
      "EUR/USD forecast",
      "EUR/USD technical analysis"
    ],
    "sources": [
      {"title": "...", "url": "https://..."}
    ]
  }
}
```

**Key Features**:
- ✅ Synthesizes all agent outputs
- ✅ Google Search for real-time verification
- ✅ Structured decision (BUY/SELL/WAIT)
- ✅ Confidence score (0.0-1.0)
- ✅ Detailed reasoning
- ✅ Trade parameters from Risk Agent
- ✅ Source citations

**Cost**: ~$0.015 per analysis (Google Search)

---

## Agent Communication Pattern

### State-Based Communication

Agents don't communicate directly. They communicate through **LangGraph state**:

```python
# Query Parser updates state
state["query_context"] = {"pair": "EUR/USD", ...}
state["pair"] = "EUR/USD"

# News Agent reads state, updates with result
state["news_result"] = news_agent.analyze(state["pair"])

# Technical Agent reads state, updates with result
state["technical_result"] = technical_agent.analyze(state["pair"])

# Risk Agent reads all results
risk_result = risk_agent.validate(
    state["technical_result"]["data"]["stop_loss"],
    state["technical_result"]["data"]["take_profit"]
)
state["risk_result"] = risk_result

# Synthesis Agent reads all results
synthesis_result = synthesis_agent.decide(
    news=state["news_result"],
    technical=state["technical_result"],
    fundamental=state["fundamental_result"],
    risk=state["risk_result"]
)
state["decision"] = synthesis_result
```

### Return Format Standard

All agents follow this pattern:

```python
{
    "success": bool,          # True if agent completed successfully
    "agent": str,             # Agent name for debugging
    "data": dict,             # Agent-specific data
    "summary": str,           # Human-readable summary
    "error": str (optional)   # Error message if success=False
}
```

## Agent Execution Order

### 1. Sequential Phase
```
Query Parser → Parallel Analysis → Risk Assessment
```

### 2. Parallel Phase
```
News Agent     ]
Technical Agent  } asyncio.gather() - simultaneous execution
Fundamental Agent]
```

### 3. Conditional Phase
```
Risk Agent → [If approved] → Synthesis Agent
           → [If rejected] → END (WAIT decision)
```

## Adding a New Agent

To add a new agent to the system:

1. **Create Agent Class** (`agents/new_agent.py`):
```python
class NewAgent:
    async def analyze(self, pair: str, query_context: dict = None) -> dict:
        try:
            # Perform analysis
            return {
                "success": True,
                "agent": "NewAgent",
                "data": {...},
                "summary": "..."
            }
        except Exception as e:
            return {
                "success": False,
                "agent": "NewAgent",
                "error": str(e)
            }
```

2. **Update State** (`graph/state.py`):
```python
class ForexAgentState(TypedDict):
    # ... existing fields ...
    new_agent_result: Optional[Dict[str, Any]]
```

3. **Create Node Function** (`graph/nodes.py`):
```python
async def new_agent_node(state, config):
    agent = NewAgent()
    result = await agent.analyze(state["pair"], state.get("query_context"))
    return {"new_agent_result": result}
```

4. **Update Workflow** (`graph/workflow.py`):
```python
workflow.add_node("new_agent", new_agent_node)
workflow.add_edge("parallel_analysis", "new_agent")
workflow.add_edge("new_agent", "risk")
```

5. **Update System** (`system.py`):
```python
def _format_result(self, state):
    return {
        # ... existing fields ...
        "agent_results": {
            # ... existing agents ...
            "new_agent": state.get("new_agent_result")
        }
    }
```

6. **Document Agent** (this README):
- Add agent to status table
- Create detailed section
- Add usage example
- Document cost impact

## Testing Agents

### Individual Agent Testing

```python
# Test News Agent
from agents.news_agent import NewsAgent
import asyncio

agent = NewsAgent()
result = await asyncio.run(agent.analyze("EUR/USD"))
assert result["success"] == True

# Test Technical Agent
from agents.technical_agent import TechnicalAgent

agent = TechnicalAgent(use_real_prices=True)
result = agent.analyze("XAU/USD")
assert result["data"]["price_source"] == "real"

# Test Fundamental Agent
from agents.fundamental_agent import FundamentalAgent

agent = FundamentalAgent()
result = await asyncio.run(agent.analyze("EUR/USD"))
assert "fundamental_score" in result["data"]

# Test Risk Agent
from agents.risk_agent import RiskAgent

agent = RiskAgent(account_balance=10000, max_risk_per_trade=0.02)
result = agent.validate_trade("EUR/USD", 1.0850, 1.0780, 1.0980)
assert "trade_approved" in result["data"]
```

### Full System Testing

```bash
# Run all tests
python test_basic.py

# Test specific agent
python test_async_news.py        # News Agent
python test_price_api.py         # Technical Agent (price service)
python test_historical_price.py  # Technical Agent (historical data)
```

## Performance Optimization

### Async Best Practices
- Use `await` for all I/O-bound operations
- Use `asyncio.gather()` for parallel execution
- Include `return_exceptions=True` for graceful failures

### Caching Strategies
- Price data: 60-second cache
- News headlines: Consider 5-minute cache
- Economic data: Consider 1-hour cache

### Cost Optimization
- Minimize Google Search queries
- Use cached prices when possible
- Batch similar analyses
- Monitor API quotas

## Related Documentation

- [System Architecture](../architecture/SYSTEM_ARCHITECTURE.md) - Overall system design
- [Agent Optimization](AGENT_OPTIMIZATION.md) - LLM-powered agent implementation details
- [Price API Integration](../integration/PRICE_API.md) - Price service documentation

---

**For agent implementation details, see [AGENT_OPTIMIZATION.md](AGENT_OPTIMIZATION.md).**
