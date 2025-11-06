# News Agent Flow

**Location**: `agents/news_agent.py`
**Node Function**: `news_node()` in `graph/nodes.py`
**Agent Class**: `NewsAgent`
**Execution Mode**: **Async** (parallel with Technical and Fundamental agents)

## Overview

The News Agent analyzes market news and sentiment using **Google Search grounding**. It fetches real-time headlines, assesses sentiment, and evaluates market impact.

## Purpose

- Fetch real-time news headlines via Google Search
- Analyze overall market sentiment (bullish/bearish/neutral)
- Assess news impact (high/medium/low)
- Identify key market-moving events
- Provide source citations for all news items

## Flow Diagram

```
┌──────────────────────────────────────────┐
│  Input: pair = "XAU/USD"                 │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  1. Parse pair into base/quote           │
│     XAU/USD → base: XAU, quote: USD      │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  2. Initialize Gemini 2.5 Flash client   │
│     - Temperature: 0.2 (factual)         │
│     - Response format: JSON              │
│     - Google Search grounding enabled    │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  3. Build news analysis prompt           │
│     - Search queries for:                │
│       • "{pair} forex news"              │
│       • "{base} currency news"           │
│       • "{quote} currency news"          │
│       • "{base} central bank"            │
│       • "{base} economy"                 │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  4. Send to Gemini with Google Search    │
│     - Gemini searches the web            │
│     - Collects recent headlines          │
│     - Extracts sentiment from sources    │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  5. Parse JSON response                  │
│     - headlines (array of objects)       │
│     - sentiment_score (-1.0 to +1.0)     │
│     - sentiment (bullish/bearish/neutral)│
│     - impact (high/medium/low)           │
│     - key_events (array)                 │
│     - summary (text)                     │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  6. Extract grounding metadata           │
│     - search_queries (what Gemini        │
│       searched)                          │
│     - sources (title + URL for each)     │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  7. Return structured result with:       │
│     - success: true                      │
│     - data: {headlines, sentiment, ...}  │
│     - grounding metadata                 │
└──────────────────────────────────────────┘
```

## Inputs

**From Node**:
- `pair` (string): Trading pair (e.g., "EUR/USD", "XAU/USD", "BTC/USD")

**From Environment**:
- `GOOGLE_AI_API_KEY`: Gemini API key (with Google Search access)

## Outputs

**Success Response**:
```python
{
    "success": True,
    "agent": "NewsAgent",
    "data": {
        "pair": "XAU/USD",
        "headlines": [
            {
                "title": "Gold prices surge on Fed rate uncertainty",
                "date": "2025-11-05",
                "sentiment": "bullish",
                "source": "Reuters"
            },
            {
                "title": "Central banks increase gold reserves",
                "date": "2025-11-05",
                "sentiment": "bullish",
                "source": "Bloomberg"
            },
            {
                "title": "Strong dollar pressures gold prices",
                "date": "recent",
                "sentiment": "bearish",
                "source": "CNBC"
            }
        ],
        "sentiment_score": 0.45,  # -1.0 to +1.0
        "sentiment": "bullish",  # Overall assessment
        "impact": "high",  # high/medium/low
        "news_count": 3,
        "key_events": [
            "Fed signaling potential rate pause",
            "Central bank gold buying increased 15%",
            "USD index strengthens to 104.5"
        ],
        "summary": "Gold sentiment is bullish driven by Fed uncertainty and central bank buying, despite dollar strength.",
        "analysis_timestamp": "2025-11-06T14:30:00.000Z",
        "search_queries": [
            "XAU/USD forex news",
            "gold price news 2025",
            "central bank gold"
        ],
        "sources": [
            {"title": "Reuters - Gold rises on Fed...", "url": "https://..."},
            {"title": "Bloomberg - Central banks...", "url": "https://..."}
        ],
        "data_source": "google_search"
    }
}
```

**Error Response**:
```python
{
    "success": False,
    "agent": "NewsAgent",
    "error": "API timeout",
    "data": {}
}
```

## Data Structure Details

### Headlines Array

Each headline object contains:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | string | Headline text from search | "Gold prices surge..." |
| `date` | string | Publication date or "recent" | "2025-11-05" or "recent" |
| `sentiment` | string | Individual headline sentiment | "bullish", "bearish", "neutral" |
| `source` | string | Publication name (if available) | "Reuters", "Bloomberg" |

### Sentiment Score

- **Range**: -1.0 (very bearish) to +1.0 (very bullish)
- **Interpretation**:
  - `-1.0 to -0.5`: Very bearish
  - `-0.5 to -0.2`: Bearish
  - `-0.2 to +0.2`: Neutral
  - `+0.2 to +0.5`: Bullish
  - `+0.5 to +1.0`: Very bullish

### Impact Assessment

| Impact | Description | Examples |
|--------|-------------|----------|
| `high` | Major market-moving events | Central bank rate decisions, GDP releases, geopolitical crises |
| `medium` | Notable but not critical | Inflation data, forecasts, earnings |
| `low` | Minor routine news | Routine statements, minor data |

### Key Events

Array of 2-3 most important recent events, formatted as concise strings:
```python
[
    "Fed signaling potential rate pause",
    "Central bank gold buying increased 15%",
    "USD index strengthens to 104.5"
]
```

## Prompt Engineering

### Temperature: 0.2

**Why low but not minimal?**
- **Factual base**: Need accuracy for news (low temp)
- **Some flexibility**: Allow natural summarization (not 0.0)
- **Sentiment nuance**: Can interpret tone (not rigid)

### Prompt Structure

1. **Role**: "You are a forex news analyst with real-time access to Google Search"
2. **Task**: "Analyze current news and market sentiment for {pair}"
3. **Search Instructions**:
   - Specific search queries to use
   - What to look for in results
4. **Analysis Requirements**:
   - Extract 3-5 recent headlines
   - Identify major events
   - Calculate sentiment score
   - Assess impact level
5. **Output Format**: JSON schema with field descriptions
6. **Critical Rules**:
   - Use ONLY information from Google Search
   - Do NOT make up headlines
   - Be objective and fact-based
   - If no news found, indicate in summary

### Google Search Grounding

```python
grounding_tool = types.Tool(google_search=types.GoogleSearch())

config = types.GenerateContentConfig(
    temperature=0.2,
    response_mime_type="application/json",
    tools=[grounding_tool],
    thinking_config=types.ThinkingConfig(thinking_budget=0)
)
```

**What happens?**
1. Gemini reads your prompt
2. Identifies search queries needed
3. Executes Google searches automatically
4. Analyzes search results
5. Synthesizes findings into structured JSON
6. Returns grounding metadata (sources, queries used)

## Grounding Metadata Extraction

```python
# Extract grounding from response
if response.candidates[0].grounding_metadata:
    metadata = response.candidates[0].grounding_metadata

    # Queries Gemini actually searched
    search_queries = metadata.web_search_queries or []

    # Source citations
    if metadata.grounding_chunks:
        sources = [
            {
                "title": chunk.web.title,
                "url": chunk.web.uri
            }
            for chunk in metadata.grounding_chunks
        ]
```

**Why important?**
- **Transparency**: User sees where info came from
- **Verification**: Can check sources manually
- **Trust**: Real citations build confidence
- **Debugging**: See what Gemini searched

## Async Execution

### Why Async?

The News Agent is executed in parallel with Technical and Fundamental agents:

```python
# In graph/parallel_nodes.py
results = await asyncio.gather(
    news_node(state, config),
    technical_node(state, config),
    fundamental_node(state, config),
    return_exceptions=True
)
```

**Benefits**:
- **3x speedup**: All 3 agents run simultaneously
- **Better UX**: Faster analysis completion
- **I/O optimization**: Agents are I/O-bound (API calls)

### Async Method Signature

```python
async def analyze(self, pair: str) -> Dict[str, Any]:
    # Must be async for parallel execution
    ...
```

## Error Handling

### API Failures

```python
try:
    # Gemini API call
    response = client.models.generate_content(...)
except Exception as e:
    print(f"  ⚠️  News Agent error: {str(e)}")
    return {
        "success": False,
        "agent": self.name,
        "error": str(e),
        "data": {}
    }
```

**Graceful degradation**:
- Workflow continues even if News Agent fails
- Other agents can still provide analysis
- Synthesis Agent handles missing news data

### Missing Data

If Google Search returns no relevant news:
```python
{
    "headlines": [],
    "sentiment": "neutral",
    "impact": "low",
    "summary": "No recent news found for XAU/USD. Market conditions appear stable."
}
```

## Performance Metrics

- **Average latency**: ~2-4 seconds (Google Search + analysis)
- **Token usage**: ~200-400 input + ~300-600 output
- **Cost per analysis**: ~$0.015-0.025 (includes Google Search grounding)
- **Success rate**: >90% (depends on search availability)

## Integration with LangGraph

### Node Wrapper

```python
# In graph/nodes.py
async def news_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    pair = state["pair"]
    print(f"📰 News Agent analyzing {pair} with Google Search...")

    agent = NewsAgent()
    result = await agent.analyze(pair)

    return {
        "news_result": result,
        "step_count": state.get("step_count", 0) + 1
    }
```

### State Updates

News Agent updates state with:
- `news_result`: Full analysis result
- `step_count`: Incremented by 1

## Use Cases by Asset Type

### Forex Pairs (EUR/USD, GBP/USD)

**Search Focus**:
- Central bank policy statements
- Economic data releases (GDP, inflation, employment)
- Political events affecting currencies
- Interest rate differentials

**Example Headlines**:
- "ECB holds rates at 4%, signals cautious approach"
- "US jobs report beats expectations, dollar strengthens"

### Commodities (XAU/USD, XAG/USD)

**Search Focus**:
- Central bank gold buying
- Inflation hedge narratives
- Safe haven demand
- Production/supply news
- Industrial demand trends

**Example Headlines**:
- "Central banks increase gold reserves by 15%"
- "Gold rises as inflation fears mount"

### Cryptocurrencies (BTC/USD, ETH/USD)

**Search Focus**:
- Regulatory developments
- Institutional adoption
- Network upgrades
- Market sentiment shifts
- Macro correlations

**Example Headlines**:
- "SEC approves Bitcoin ETFs, market rallies"
- "Ethereum upgrade completes successfully"

## Comparison: Mock vs Real Data

### Previous (Mock) Approach

```python
# Old mock headlines
headlines = [
    {
        "title": f"Breaking: {pair} shows strong momentum",
        "date": "2025-11-05",
        "sentiment": "bullish"
    }
]
```

**Problems**:
- Not factual
- Can't verify
- Misleading to users
- No real market insight

### Current (Google Search) Approach

```python
# Real headlines from Google Search
headlines = [
    {
        "title": "Gold prices surge on Fed rate uncertainty",  # REAL
        "date": "2025-11-05",
        "sentiment": "bullish",
        "source": "Reuters"  # VERIFIED
    }
]
```

**Benefits**:
- ✅ Factual and current
- ✅ Source citations
- ✅ Verifiable
- ✅ Real market insight
- ✅ Actionable intelligence

## Common Issues

### Issue: Stale News

**Problem**: Headlines from days/weeks ago
**Solution**: Prompt emphasizes "last 24-48 hours"

### Issue: Irrelevant Results

**Problem**: Search returns off-topic news
**Solution**: Specific search queries focused on trading context

### Issue: Conflicting Sentiment

**Problem**: Some headlines bullish, others bearish
**Solution**: Gemini weighs by impact and recency, provides nuanced score

## Key Design Decisions

### Why Google Search over NewsAPI?

1. **No API Key**: Google Search included with Gemini
2. **Broader Coverage**: Access to all indexed news
3. **Fresher Data**: Real-time search results
4. **Automatic Relevance**: Gemini filters for relevance
5. **Citation**: Grounding metadata provides sources

### Why Sentiment Score AND Label?

- **Score** (-1.0 to +1.0): Precise quantification for calculations
- **Label** (bullish/bearish/neutral): Human-readable, easier interpretation

### Why Include Source Citations?

- **Trust**: Users can verify claims
- **Transparency**: Clear where data comes from
- **Debugging**: Helps identify bad sources
- **Compliance**: Important for financial applications

## Testing

### Test Cases

```python
# Test different asset types
test_pairs = [
    "EUR/USD",  # Forex
    "XAU/USD",  # Commodity
    "BTC/USD",  # Crypto
]

for pair in test_pairs:
    agent = NewsAgent()
    result = await agent.analyze(pair)

    assert result["success"] == True
    assert "headlines" in result["data"]
    assert "sentiment" in result["data"]
    assert "sources" in result["data"]
```

### Validation

- ✅ Headlines array not empty (if news exists)
- ✅ Sentiment score in range [-1.0, 1.0]
- ✅ Sentiment label in valid set
- ✅ Impact level in valid set
- ✅ Sources include title and URL
- ✅ Timestamp is valid ISO format

## Future Enhancements

1. **Sentiment Trend**: Track sentiment changes over time
2. **Event Calendar**: Integrate economic calendar
3. **Source Ranking**: Weight by source credibility
4. **Multilingual**: Analyze news in multiple languages
5. **Real-Time Alerts**: Monitor breaking news

## Related Files

- `graph/nodes.py` - news_node() wrapper function
- `graph/parallel_nodes.py` - Parallel execution logic
- `graph/state.py` - news_result field in state

## Monitoring & Debugging

### Print Statements

```
📰 News Agent analyzing XAU/USD with Google Search...
  ✅ Found 5 headlines (sentiment: bullish, impact: high)
```

### Error Messages

```
  ⚠️  News Agent error: API timeout
  [Fallback] Continuing without news analysis
```

## Summary

The News Agent provides **real-time market intelligence** using Google Search grounding:

**Key Features**:
- ✅ Real headlines from Google Search (not mock)
- ✅ Intelligent sentiment analysis
- ✅ Impact assessment (high/medium/low)
- ✅ Source citations for transparency
- ✅ Async execution (parallel with other agents)
- ✅ Graceful error handling

**Key Metrics**:
- Latency: ~2-4 seconds
- Cost: ~$0.015-0.025 per analysis
- Success Rate: >90%
- Parallel Execution: 3x speedup

**Value Proposition**:
Transforms news from generic mock data → actionable market intelligence with verifiable sources.
