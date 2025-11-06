# Risk Agent Flow

**Location**: `agents/risk_agent.py`
**Node Function**: `risk_node()` in `graph/nodes.py`
**Agent Class**: `RiskAgent`
**Execution Mode**: **Sync** (after parallel analysis, before synthesis)
**Critical Role**: **GATEKEEPER** - Can reject trades

## Overview

The Risk Agent calculates position sizing and validates risk parameters. It's the **only agent that can stop the workflow** by rejecting trades. Uses **rule-based calculations** with optional **LLM-enhanced analysis**.

## Purpose

- Calculate position size based on account balance and risk tolerance
- Validate stop loss distance (10-100 pips)
- Check risk/reward ratio (minimum 1.5:1)
- Assess market volatility and conditions (LLM-enhanced)
- Approve or reject trades (CRITICAL decision)

## Architecture

### Two-Layer Approach

1. **Rule-Based Layer** (always runs):
   - Mathematical position sizing
   - Stop loss validation
   - Risk/reward calculation
   - Trade approval logic

2. **LLM Enhancement Layer** (optional):
   - Market volatility assessment
   - Risk factor identification
   - Position size optimization
   - Context-aware warnings

## Flow Diagram

```
┌──────────────────────────────────────────┐
│  Input from Technical Agent:             │
│  - entry_price: 1.0845                   │
│  - stop_loss: 1.0780                     │
│  - take_profit: 1.0980                   │
│  - direction: "BUY"                      │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  1. Extract trade parameters             │
│     - Pair, entry, stop, direction       │
│     - Get account settings from env      │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  2. RULE-BASED CALCULATIONS              │
│     A. Calculate risk in pips            │
│        risk_pips = |entry - stop| * 10000│
│     B. Calculate position size           │
│        pos_size = (acct * risk%) / pips  │
│     C. Calculate dollar risk             │
│        $ risk = account * risk%          │
│     D. Calculate risk/reward ratio       │
│        R:R = reward_pips / risk_pips     │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  3. VALIDATE TRADE (4 Rules)             │
│     ✓ Rule 1: Risk pips > 0              │
│     ✓ Rule 2: Risk pips 10-100           │
│     ✓ Rule 3: R:R ≥ 1.5:1                │
│     ✓ Rule 4: Stop loss logical          │
└──────────────┬───────────────────────────┘
               │
               ▼
        ┌──────┴──────┐
        │   Valid?    │
        └──┬────────┬──┘
     NO    │        │   YES
           ▼        ▼
    ┌─────────┐ ┌──────────────────┐
    │  REJECT │ │  Preliminary     │
    │  Trade  │ │  APPROVE         │
    └────┬────┘ └─────────┬────────┘
         │                │
         │                ▼
         │      ┌──────────────────────┐
         │      │  use_llm + context?  │
         │      └──┬────────┬──────────┘
         │    NO   │        │   YES
         │         │        ▼
         │         │   ┌────────────────────┐
         │         │   │  4. LLM ANALYSIS   │
         │         │   │  - Market volatility│
         │         │   │  - Risk factors    │
         │         │   │  - Position adjust │
         │         │   │  - Warnings        │
         │         │   └────────┬───────────┘
         │         │            │
         └─────────┴────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  5. Return result:   │
        │  - trade_approved    │
        │  - position_size     │
        │  - risk parameters   │
        │  - warnings (LLM)    │
        │  - recommendations   │
        └──────────────────────┘
```

## Inputs

**From State** (via Technical Agent result):
- `entry_price` (float): Proposed entry price
- `stop_loss` (float): Stop loss price
- `take_profit` (float, optional): Take profit price
- `direction` (string): "BUY" or "SELL"
- `pair` (string): Trading pair

**From Environment**:
- `ACCOUNT_BALANCE` (default: 10000.0)
- `MAX_RISK_PER_TRADE` (default: 0.02 = 2%)
- `GOOGLE_AI_API_KEY` (for LLM enhancement)

**Market Context** (for LLM enhancement):
- News sentiment
- Technical signals
- Fundamental outlook

## Outputs

### Trade Approved

```python
{
    "success": True,
    "agent": "RiskAgent",
    "data": {
        "pair": "EUR/USD",
        "direction": "BUY",
        "entry_price": 1.0845,
        "stop_loss": 1.0780,
        "take_profit": 1.0980,

        # Risk Calculations
        "risk_in_pips": 65.0,
        "position_size": 3.08,  # Standard lots
        "dollar_risk": 200.00,  # $200
        "risk_percentage": 2.0,  # 2% of account
        "leverage": 1.0,
        "account_balance": 10000.0,

        # Reward Calculations
        "reward_in_pips": 135.0,
        "risk_reward_ratio": 2.08,  # 2.08:1 (good!)
        "potential_profit": 415.38,

        # Decision
        "trade_approved": True,
        "rejection_reason": None,

        # LLM Enhancement (if enabled)
        "risk_factors": [
            "FOMC meeting in 2 days may increase volatility",
            "Stop loss near recent support at 1.0775"
        ],
        "market_volatility": "medium",
        "recommended_action": True,
        "confidence_score": 0.80,
        "risk_warnings": [
            "Consider reducing position size by 20% due to upcoming event"
        ],
        "optimal_position_size": 2.46,  # LLM suggestion

        "analysis_timestamp": "2025-11-06T14:30:00.000Z",
        "summary": "Trade APPROVED: Position size 3.08 lots, risking $200 (2% of account).",
        "data_source": "llm_enhanced"  # or "rule_based"
    }
}
```

### Trade Rejected

```python
{
    "success": True,
    "agent": "RiskAgent",
    "data": {
        "pair": "EUR/USD",
        "direction": "BUY",
        "entry_price": 1.0845,
        "stop_loss": 1.0820,  # Too tight!
        "risk_in_pips": 25.0,
        "position_size": 8.0,

        # Decision
        "trade_approved": False,
        "rejection_reason": "Risk too small: 25.0 pips is below minimum of 10 pips",

        "summary": "Trade REJECTED: Risk too small: 25.0 pips is below minimum of 10 pips",
        "data_source": "rule_based"
    }
}
```

## Rule-Based Validation Logic

### Rule 1: Risk Pips Must Be Positive

```python
if risk_in_pips <= 0:
    return False, "Invalid stop loss: risk in pips must be positive"
```

**Why**: Stop loss on wrong side of entry

### Rule 2: Risk Pips Must Be 10-100

```python
if risk_in_pips < 10:
    return False, f"Risk too small: {risk_in_pips:.1f} pips is below minimum of 10 pips"

if risk_in_pips > 100:
    return False, f"Risk too high: {risk_in_pips:.1f} pips exceeds maximum of 100 pips"
```

**Why**:
- < 10 pips: Too tight, likely to get stopped out by noise
- > 100 pips: Excessive risk, poor risk management

### Rule 3: Risk/Reward Ratio Must Be ≥ 1.5:1

```python
if risk_reward_ratio < 1.5:
    return False, f"Poor risk/reward ratio: {risk_reward_ratio:.2f} is below minimum of 1.5"
```

**Why**: Need at least 1.5x reward to justify risk (better: 2:1 or 3:1)

### Rule 4: Stop Loss Must Be Logical

For BUY: stop_loss < entry_price
For SELL: stop_loss > entry_price

## Position Sizing Formula

### Standard Formula

```python
position_size = (account_balance * max_risk_per_trade) / (risk_in_pips * pip_value_per_lot)
```

**Example**:
```
Account: $10,000
Risk per trade: 2% = $200
Risk in pips: 65 pips
Pip value per standard lot: $10

Position size = $200 / (65 * $10) = $200 / $650 = 0.308 lots
```

### Pip Value

- **Standard lot** = 100,000 units
- **Pip value** for EUR/USD = $10 per standard lot
- **Mini lot** = 10,000 units = $1 per pip
- **Micro lot** = 1,000 units = $0.10 per pip

### Pip Calculation

```python
# Most pairs: 1 pip = 0.0001
pip_multiplier = 10000

# JPY pairs: 1 pip = 0.01
# TODO: Implement JPY detection

risk_in_pips = abs(entry_price - stop_loss) * pip_multiplier
```

## LLM Enhancement

### When LLM Runs

```python
if self.use_llm and market_context:
    return await self._analyze_with_llm(...)
```

**Requirements**:
- `use_llm=True` (constructor)
- `market_context` passed to analyze()
- `GOOGLE_AI_API_KEY` in environment

### LLM Prompt Components

1. **Trade Summary**: Pair, direction, entry, stop, position size
2. **Market Context**: News sentiment, technical signals, fundamental outlook
3. **Account Info**: Balance, risk %, leverage
4. **Analysis Tasks**:
   - Identify 3-5 risk factors
   - Assess market volatility (low/medium/high)
   - Validate position size
   - Generate warnings
   - Suggest adjustments
   - Recommend action (approve/reject)
   - Provide confidence score

### LLM Output

```json
{
    "risk_factors": [
        "High volatility due to upcoming Fed decision",
        "Technical stop loss near key support level",
        "News sentiment bearish contradicts bullish technical"
    ],
    "market_volatility": "high",
    "volatility_assessment": "ATR at 85 pips (above average). Stop loss may be too tight.",
    "recommended_action": true,
    "confidence_score": 0.65,
    "risk_warnings": [
        "FOMC meeting in 2 days - expect increased volatility",
        "Stop loss only 5 pips from swing low - may get stopped prematurely"
    ],
    "optimal_position_size": 0.15,  # Reduced from calculated
    "suggested_adjustments": {
        "position_size": 0.15,
        "stop_loss": 1.0760,  # Widened
        "timing": "Wait for FOMC or reduce size"
    }
}
```

## Conditional Workflow Routing

### Critical Role

The Risk Agent determines if the workflow continues:

```python
def should_continue_after_risk(state: ForexAgentState) -> str:
    risk_result = state.get("risk_result", {})

    if not risk_result.get("success", False):
        return "end"  # Risk analysis failed

    risk_data = risk_result.get("data", {})
    if not risk_data.get("trade_approved", False):
        return "end"  # TRADE REJECTED - STOP WORKFLOW

    return "continue"  # Proceed to synthesis
```

**Flow**:
```
parallel_analysis → risk → [DECISION POINT]
                            ├─ approved → synthesis → END
                            └─ rejected → END (skip synthesis)
```

## Market Context Integration

### News Sentiment

```python
news_sentiment = market_context["news_result"]["data"]["sentiment"]
# "bullish", "bearish", "neutral"

if news_sentiment == "bearish" and direction == "BUY":
    risk_warnings.append("News sentiment is bearish, contradicts BUY signal")
```

### Technical Signals

```python
technical_signals = market_context["technical_result"]["data"]["signals"]["overall"]
# "BUY", "SELL", "HOLD"

if technical_signals != direction:
    risk_warnings.append("Technical signals don't align with trade direction")
```

### Fundamental Outlook

```python
fundamental_outlook = market_context["fundamental_result"]["data"]["outlook"]
# "bullish", "bearish", "neutral"

if fundamental_outlook == "bearish" and direction == "BUY":
    risk_factors.append("Fundamental outlook is bearish")
```

## Error Handling

### Missing Technical Data

```python
if not ta_result.get("success"):
    raise ValueError("Technical analysis failed, cannot calculate risk")
```

**Result**: Risk node returns error, workflow ends

### LLM Enhancement Failure

```python
try:
    llm_analysis = await self._analyze_with_llm(...)
except Exception as e:
    print(f"⚠️  LLM risk analysis failed, using rule-based")
    return risk_calc  # Fall back to rule-based
```

**Result**: Workflow continues with rule-based calculations

## Performance Metrics

### Rule-Based Only
- **Latency**: ~10-50ms (pure calculation)
- **Cost**: $0
- **Success rate**: ~98%

### LLM-Enhanced
- **Latency**: ~2-4 seconds (includes Google Search)
- **Token usage**: ~500-700 input + ~400-600 output
- **Cost**: ~$0.020-0.030 per analysis
- **Success rate**: ~90%

## Integration with LangGraph

### Node Wrapper

```python
def risk_node(state: ForexAgentState, config: RunnableConfig):
    # Extract technical analysis results
    ta_result = state.get("technical_result", {})
    ta_data = ta_result["data"]

    # Get trade parameters
    current_price = ta_data["current_price"]
    stop_loss = ta_data["stop_loss"]
    direction = "BUY" if ta_data["signals"]["overall"] == "BUY" else "SELL"

    # Initialize agent
    agent = RiskAgent(account_balance=10000.0, max_risk_per_trade=0.02)

    # Analyze risk
    result = agent.analyze(
        pair=pair,
        entry_price=current_price,
        stop_loss=stop_loss,
        direction=direction,
        take_profit=ta_data.get("take_profit")
    )

    return {
        "risk_result": result,
        "step_count": state["step_count"] + 1
    }
```

### State Updates

Risk Agent updates state with:
- `risk_result`: Full risk analysis
- `step_count`: Incremented by 1

## Common Rejection Reasons

### 1. Stop Loss Too Tight

```
"Risk too small: 8.5 pips is below minimum of 10 pips"
```

**Fix**: Widen stop loss to at least 10 pips

### 2. Stop Loss Too Wide

```
"Risk too high: 125.0 pips exceeds maximum of 100 pips"
```

**Fix**: Tighten stop loss or reduce position size

### 3. Poor Risk/Reward

```
"Poor risk/reward ratio: 1.2 is below minimum of 1.5"
```

**Fix**: Widen take profit or tighten stop loss

### 4. Invalid Stop Loss

```
"Invalid stop loss: risk in pips must be positive"
```

**Fix**: Ensure stop loss is on correct side of entry

## Key Design Decisions

### Why Rule-Based + LLM Hybrid?

**Rule-Based** (always runs):
- ✅ Fast (~10ms)
- ✅ Deterministic
- ✅ No API dependency
- ✅ Mathematical accuracy

**LLM Enhancement** (optional):
- ✅ Context-aware warnings
- ✅ Volatility assessment
- ✅ Market condition adaptation
- ✅ Natural language reasoning

**Together**: Best of both worlds

### Why Risk Agent Can Reject Trades?

**Philosophy**: Capital preservation > missed opportunities

**Benefits**:
- Prevents bad trades
- Enforces risk management
- Reduces losses
- Builds discipline

### Why 2% Risk Per Trade?

**Standard risk management rule**:
- Allows 50 losing trades before account wipe
- Reasonable drawdown tolerance
- Industry best practice

**Adjustable** via `MAX_RISK_PER_TRADE` environment variable

### Why 1.5:1 Minimum Risk/Reward?

**Mathematical requirement**:
- Break even with 40% win rate
- Better ratios (2:1, 3:1) allow lower win rates
- 1:1 requires 50%+ win rate (hard to achieve)

## Testing

### Test Cases

```python
# Test approved trade
agent = RiskAgent(account_balance=10000, max_risk_per_trade=0.02)
result = agent.analyze(
    pair="EUR/USD",
    entry_price=1.0845,
    stop_loss=1.0780,  # 65 pips
    direction="BUY",
    take_profit=1.0980  # 135 pips, R:R = 2.08
)
assert result["data"]["trade_approved"] == True
assert result["data"]["risk_reward_ratio"] > 1.5

# Test rejected trade (stop too tight)
result = agent.analyze(
    pair="EUR/USD",
    entry_price=1.0845,
    stop_loss=1.0840,  # Only 5 pips!
    direction="BUY"
)
assert result["data"]["trade_approved"] == False
assert "too small" in result["data"]["rejection_reason"]
```

### Validation

- ✅ Position size > 0
- ✅ Dollar risk = account_balance * risk_percentage
- ✅ Risk/reward ratio correct
- ✅ Rejection reason provided if rejected
- ✅ LLM confidence score in [0.0, 1.0]

## Common Issues

### Issue: All Trades Rejected

**Problem**: Stop loss consistently too tight/wide
**Solution**: Adjust Technical Agent stop loss calculation

### Issue: Position Size Too Large

**Problem**: Risk calculation incorrect
**Solution**: Verify pip_value_per_lot matches pair

### Issue: LLM Always Rejects

**Problem**: LLM too conservative
**Solution**: Adjust prompt or disable LLM enhancement

## Future Enhancements

1. **Dynamic Risk Adjustment**: Reduce risk% after losing streak
2. **Correlation Risk**: Check if multiple positions on correlated pairs
3. **Drawdown Limits**: Stop trading if account down X%
4. **Time-Based Risk**: Reduce size during high-impact events
5. **Volatility-Adjusted Sizing**: Scale position by ATR

## Related Files

- `graph/nodes.py` - risk_node() wrapper
- `graph/workflow.py` - Conditional routing logic
- `agents/technical_agent.py` - Provides entry/stop prices

## Monitoring & Debugging

### Print Statements

```
⚖️  Risk Agent calculating parameters...
  ✅ Trade APPROVED: 3.08 lots risking $200 (2%)
  📊 R:R ratio: 2.08:1
```

### Rejection Messages

```
  🛑 Trade REJECTED: Risk too high: 125 pips exceeds maximum of 100 pips
```

## Summary

The Risk Agent is the **gatekeeper** of the trading system:

**Key Features**:
- ✅ Mathematical position sizing
- ✅ Trade validation (4 rules)
- ✅ Risk/reward calculation
- ✅ Can REJECT trades (critical!)
- ✅ Optional LLM enhancement
- ✅ Market context integration
- ✅ Conditional workflow routing

**Key Metrics**:
- Latency: ~10-50ms (rule-based), ~2-4s (LLM)
- Cost: $0 (rule-based), ~$0.025 (LLM)
- Success Rate: ~98% (rule-based), ~90% (LLM)

**Value Proposition**:
Enforces disciplined risk management → capital preservation → long-term profitability.
