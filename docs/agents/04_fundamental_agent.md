# Fundamental Agent Flow

**Location**: `agents/fundamental_agent.py`
**Node Function**: `fundamental_node()` in `graph/nodes.py`
**Agent Class**: `FundamentalAgent`
**Execution Mode**: **Async** (parallel with News and Technical agents)

## Overview

The Fundamental Agent analyzes economic fundamentals using **Gemini LLM** with **Google Search** to fetch real-time economic data. It compares base vs quote currency fundamentals to generate trading outlook.

## Purpose

- Fetch real-time economic data (GDP, inflation, interest rates)
- Compare base currency vs quote currency fundamentals
- Analyze central bank policies
- Generate fundamental score and outlook
- Provide reasoned fundamental analysis

## Flow Diagram

```
┌──────────────────────────────────────────┐
│  Input: pair = "EUR/USD"                 │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  1. Parse pair into base/quote           │
│     EUR/USD → EUR (base), USD (quote)    │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  2. Initialize Gemini 2.5 Flash client   │
│     - Temperature: 0.3                   │
│     - Google Search enabled              │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  3. Build fundamental analysis prompt    │
│     - Search for EUR economic data       │
│     - Search for USD economic data       │
│     - Comparison framework               │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  4. Gemini searches for economic data    │
│     - GDP growth rates                   │
│     - Inflation (CPI)                    │
│     - Central bank interest rates        │
│     - Unemployment rates                 │
│     - Central bank policy statements     │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  5. Compare base vs quote currencies     │
│     - Which has stronger GDP growth?     │
│     - Interest rate differential?        │
│     - Inflation comparison?              │
│     - Policy divergence?                 │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  6. Calculate fundamental score          │
│     - Positive: Favors base (bullish)    │
│     - Negative: Favors quote (bearish)   │
│     - Range: -1.0 to +1.0                │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  7. Return structured result with:       │
│     - base_currency data                 │
│     - quote_currency data                │
│     - comparison metrics                 │
│     - fundamental_score                  │
│     - outlook (bullish/bearish/neutral)  │
│     - reasoning + sources                │
└──────────────────────────────────────────┘
```

## Inputs

**From Node**:
- `pair` (string): Trading pair (e.g., "EUR/USD", "XAU/USD", "BTC/USD")

**From Environment**:
- `GOOGLE_AI_API_KEY`: Gemini API key

**Constructor Options**:
```python
FundamentalAgent(use_llm=True)  # LLM mode vs rule-based
```

## Outputs

### LLM Analysis (Success)

```python
{
    "success": True,
    "agent": "FundamentalAgent",
    "data": {
        "pair": "EUR/USD",

        # Base Currency Fundamentals
        "base_currency": {
            "currency": "EUR",
            "asset_type": "currency",
            "gdp_growth": 1.2,  # Annual %
            "inflation": 2.5,  # CPI annual %
            "interest_rate": 4.0,  # Central bank rate %
            "unemployment": 6.5,  # %
            "recent_data": "ECB holds rates at 4.0%, GDP growth 1.2%...",
            "central_bank": "ECB maintaining restrictive policy, monitoring inflation..."
        },

        # Quote Currency Fundamentals
        "quote_currency": {
            "currency": "USD",
            "asset_type": "currency",
            "gdp_growth": 2.8,  # Annual %
            "inflation": 3.2,  # CPI annual %
            "interest_rate": 5.5,  # Fed funds rate %
            "unemployment": 3.8,  # %
            "recent_data": "Fed holds rates at 5.5%, strong labor market...",
            "central_bank": "Federal Reserve maintaining restrictive stance..."
        },

        # Comparison
        "comparison": {
            "gdp_growth": "quote_stronger",  # USD growing faster
            "interest_rate": "quote_stronger",  # USD has higher rates
            "inflation": "base_stronger",  # EUR has lower inflation
            "unemployment": "quote_stronger",  # USD has lower unemployment
            "overall": "USD has stronger fundamentals across most metrics"
        },

        # Fundamental Score
        "fundamental_score": -0.65,  # Negative = favors quote (USD)

        # Outlook
        "outlook": "bearish",  # bearish for EUR/USD

        # Key Factors
        "key_factors": [
            "Interest rate differential of 150 bps favors USD",
            "Stronger US GDP growth (2.8% vs 1.2%)",
            "Tighter US labor market",
            "Fed maintaining restrictive stance vs ECB uncertainty"
        ],

        # Central Bank Policy
        "central_bank_policy": {
            "base": "ECB holding rates at 4.0%, cautious on inflation",
            "quote": "Fed maintaining 5.5% rates, data-dependent approach",
            "divergence": "Policy divergence supports USD strength"
        },

        # LLM Reasoning
        "analysis": "Fundamental analysis shows USD has superior economic fundamentals. Key drivers include 150 bps interest rate advantage, stronger GDP growth, and tighter labor market.",

        "reasoning": "Bearish outlook based on: 1) Interest rate differential of 150 bps favoring USD, 2) GDP growth divergence (2.8% US vs 1.2% EU), 3) Unemployment advantage (3.8% vs 6.5%), 4) Fed maintaining restrictive stance.",

        "summary": "Strong fundamental case for USD appreciation. Economic data and policy divergence favor USD over EUR.",

        # Metadata
        "analysis_timestamp": "2025-11-06T14:30:00.000Z",
        "data_source": "llm_analysis",
        "search_queries": [
            "EUR GDP growth 2025",
            "ECB interest rate",
            "USD economic data",
            "Federal Reserve policy"
        ],
        "sources": [
            {"title": "ECB maintains rates...", "url": "https://..."},
            {"title": "US GDP grows 2.8%...", "url": "https://..."}
        ]
    }
}
```

## Economic Metrics Explained

### GDP Growth

**What**: Annual economic growth rate
**Range**: Typically -5% to +10% (varies by country)
**Interpretation**:
- Higher growth = stronger economy = stronger currency (usually)
- Negative growth = recession

### Inflation (CPI)

**What**: Consumer Price Index, annual % change
**Range**: Typically 0% to 10% (varies)
**Interpretation**:
- Moderate (2-3%) = healthy
- Too high (>5%) = central bank may raise rates
- Too low (<1%) = deflationary concerns

### Interest Rates

**What**: Central bank policy rate
**Range**: 0% to 10%+ (varies by country)
**Interpretation**:
- Higher rates = stronger currency (capital flows)
- Rate differentials drive forex movements
- "Carry trade": Borrow low-rate currency, invest in high-rate

### Unemployment

**What**: Percentage of workforce unemployed
**Range**: Typically 3% to 15%
**Interpretation**:
- Lower = stronger economy
- Very low (<4%) = tight labor market, wage pressure

### Trade Balance

**What**: Exports minus imports (billions)
**Range**: -$100B to +$100B (varies)
**Interpretation**:
- Surplus (+) = exports > imports, currency demand
- Deficit (-) = imports > exports, currency supply

## Prompt Engineering

### Temperature: 0.3

**Why 0.3?**
- **Factual base**: Need accuracy for economic data
- **Some interpretation**: Allow analysis of trends
- **Balanced**: Not too rigid, not too creative

### Prompt Adaptation by Asset Type

#### For Currency Pairs (EUR/USD)

Searches for:
- GDP growth
- Inflation (CPI)
- Central bank rates
- Unemployment
- Trade balance
- Central bank policy statements

#### For Commodities (XAU/USD)

Searches for:
- Supply/demand fundamentals
- Industrial usage
- Central bank holdings (for gold)
- Inflation hedge status
- Safe haven demand

#### For Cryptocurrencies (BTC/USD)

Searches for:
- Network fundamentals (hash rate, active addresses)
- Adoption trends
- Regulatory environment
- On-chain metrics

## Fundamental Score Calculation

### Score Range: -1.0 to +1.0

```
+1.0 = Strongly favors base currency (very bullish for pair)
+0.5 = Moderately favors base currency (bullish)
 0.0 = Balanced (neutral)
-0.5 = Moderately favors quote currency (bearish)
-1.0 = Strongly favors quote currency (very bearish for pair)
```

### Weighting (LLM determines)

Typical weights:
- **Interest rate differential**: 35% (most important for forex)
- **GDP growth**: 25%
- **Inflation**: 25%
- **Unemployment**: 15%

### Example Calculation

```
EUR/USD:
- Interest rate: USD +150 bps → -35% (favors USD)
- GDP: USD +1.6% → -25% (favors USD)
- Inflation: EUR lower → +10% (favors EUR)
- Unemployment: USD better → -10% (favors USD)

Score = -35% -25% +10% -10% = -60% → -0.60 (bearish)
```

## Outlook Classification

```
fundamental_score > +0.3  → "bullish"
fundamental_score < -0.3  → "bearish"
-0.3 ≤ score ≤ +0.3       → "neutral"
```

## Central Bank Policy Analysis

### Key Policy Stances

| Stance | Description | Currency Impact |
|--------|-------------|-----------------|
| **Hawkish** | Raising rates, fighting inflation | Strengthens currency |
| **Dovish** | Cutting rates, supporting growth | Weakens currency |
| **Neutral** | Data-dependent, no clear direction | Mixed impact |

### Policy Divergence

**Most important for forex trading**:

```
Example: Fed hawkish (raising rates) + ECB dovish (cutting rates)
→ Large interest rate differential
→ USD strengthens vs EUR
→ EUR/USD falls (bearish)
```

## Async Execution

The Fundamental Agent runs in parallel with News and Technical agents:

```python
results = await asyncio.gather(
    news_node(state, config),
    technical_node(state, config),
    fundamental_node(state, config),  # Parallel
    return_exceptions=True
)
```

## Error Handling

### No Economic Data Found

```python
{
    "success": True,
    "data": {
        "base_currency": {..., "recent_data": "data not available"},
        "fundamental_score": 0.0,  # Neutral
        "outlook": "neutral",
        "summary": "Insufficient economic data for comparison"
    }
}
```

### API Failure

```python
{
    "success": False,
    "agent": "FundamentalAgent",
    "error": "API timeout",
    "data": {}
}
```

## Performance Metrics

- **Average latency**: ~3-5 seconds (Google Search + LLM analysis)
- **Token usage**: ~500-700 input + ~500-800 output
- **Cost per analysis**: ~$0.025-0.035
- **Success rate**: ~85-90%

## Integration with Risk Agent

The Fundamental Agent's output is used by the Risk Agent to assess market context:

```python
# In Risk Agent
fundamental_outlook = market_context["fundamental_result"]["data"]["outlook"]

if fundamental_outlook == "bearish" and direction == "BUY":
    risk_warnings.append("Fundamental outlook is bearish, contradicts BUY signal")
```

## Common Issues

### Issue: Stale Economic Data

**Problem**: GDP data from 6 months ago
**Solution**: Prompt emphasizes "recent data is more valuable"

### Issue: Conflicting Indicators

**Problem**: Strong GDP but weak unemployment
**Solution**: LLM weighs by importance, interest rates usually dominate

### Issue: Commodities Return Zero Data

**Problem**: Commodities don't have GDP/unemployment
**Solution**: Prompt adapts to asset type, searches supply/demand instead

## Key Design Decisions

### Why LLM for Fundamental Analysis?

**Traditional Approach**: Connect to FRED API, Trading Economics API, etc.
- ❌ Requires multiple API keys
- ❌ Complex data parsing
- ❌ No interpretation

**LLM Approach**:
- ✅ Single API (Gemini + Google Search)
- ✅ Automatic data extraction
- ✅ Intelligent comparison
- ✅ Natural language explanation

### Why Interest Rate Differential is Most Important?

In forex trading:
- Capital flows follow interest rates
- "Carry trade" is major driver
- Central bank policy is most actionable
- More predictable than GDP/inflation

## Testing

### Test Cases

```python
# Test currency pair
agent = FundamentalAgent(use_llm=True)
result = await agent.analyze("EUR/USD")
assert result["success"] == True
assert "base_currency" in result["data"]
assert "fundamental_score" in result["data"]

# Test commodity
result = await agent.analyze("XAU/USD")
assert result["data"]["base_currency"]["asset_type"] == "commodity"

# Test crypto
result = await agent.analyze("BTC/USD")
assert result["data"]["base_currency"]["asset_type"] == "cryptocurrency"
```

### Validation

- ✅ Fundamental score in range [-1.0, +1.0]
- ✅ Outlook matches score (positive → bullish)
- ✅ Key factors list not empty
- ✅ Comparison includes all main metrics
- ✅ Sources include URLs

## Future Enhancements

1. **Real API Integration**: Connect to FRED, World Bank APIs
2. **Historical Tracking**: Track how fundamentals change over time
3. **Event Calendar**: Integrate upcoming economic releases
4. **Correlation Analysis**: How fundamentals correlate with price moves
5. **Multiple Timeframes**: Short-term vs long-term fundamentals

## Related Files

- `graph/nodes.py` - fundamental_node() wrapper
- `graph/parallel_nodes.py` - Parallel execution
- `graph/state.py` - fundamental_result field
- `agents/risk_agent.py` - Uses fundamental data

## Monitoring & Debugging

### Print Statements

```
💰 Fundamental Agent analyzing EUR/USD...
  ✅ Fundamental analysis complete (outlook: bearish, score: -0.65)
```

### Error Messages

```
  ⚠️  Fundamental Agent error: API timeout
```

## Summary

The Fundamental Agent provides **economic intelligence** using:

**Key Features**:
- ✅ Real-time economic data via Google Search
- ✅ LLM-powered comparison and analysis
- ✅ Fundamental score calculation (-1.0 to +1.0)
- ✅ Central bank policy analysis
- ✅ Outlook generation (bullish/bearish/neutral)
- ✅ Source citations
- ✅ Async execution (parallel)

**Key Metrics**:
- Latency: ~3-5 seconds
- Cost: ~$0.025-0.035 per analysis
- Success Rate: ~85-90%

**Value Proposition**:
Transforms fundamental analysis from manual data collection → automated intelligence with reasoning.
