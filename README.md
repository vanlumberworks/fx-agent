# 🚀 Forex Agent System - LangGraph + Gemini

A production-ready multi-agent forex trading analysis system using **LangGraph** for agent orchestration and **Gemini 2.5 Flash** with **Google Search grounding** for intelligent synthesis.

## 🎯 Features

- **Multi-Agent Architecture**: 4 specialized agents + 1 synthesis agent
  - 📰 **News Agent**: Analyzes market news and sentiment
  - 📊 **Technical Agent**: Performs technical analysis (RSI, MACD, Moving Averages)
  - 💰 **Fundamental Agent**: Analyzes economic fundamentals (GDP, interest rates, inflation)
  - ⚖️ **Risk Agent**: Calculates position sizing and validates trades
  - 🤖 **Synthesis Agent**: Uses Gemini + Google Search for final decision

- **LangGraph Orchestration**: Stateful, intelligent workflow with conditional routing
- **Real-Time Data**: Google Search grounding for up-to-date market information
- **Source Citations**: Every decision includes web sources
- **Risk Management**: Built-in position sizing and risk validation
- **Production-Ready**: Proper error handling, logging, and structure

## 📋 Architecture

```
Input: Currency Pair (e.g., EUR/USD)
    ↓
┌───────────────┐
│  News Agent   │ → Mock news sentiment
└───────┬───────┘
        ↓
┌───────────────┐
│ Technical     │ → Mock technical indicators
│ Agent         │
└───────┬───────┘
        ↓
┌───────────────┐
│ Fundamental   │ → Mock economic data
│ Agent         │
└───────┬───────┘
        ↓
┌───────────────┐
│  Risk Agent   │ → Validates trade risk
└───────┬───────┘
        ↓
    Risk OK?
        ↓ Yes
┌───────────────────────────────┐
│  Synthesis Agent (Gemini)     │
│  + Google Search Grounding    │ → Real-time verification
└───────────────┬───────────────┘
                ↓
        BUY / SELL / WAIT
        + Citations
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/vanlumberworks/vibecode_claude.git
cd vibecode_claude

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Google AI API key
# Get your key from: https://aistudio.google.com/app/apikey
```

Your `.env` file should look like:
```
GOOGLE_AI_API_KEY=your_api_key_here
ACCOUNT_BALANCE=10000.0
MAX_RISK_PER_TRADE=0.02
```

### 3. Run Analysis

```bash
# Analyze EUR/USD
python main.py EUR/USD

# Or just use default (EUR/USD)
python main.py
```

## 💻 Usage Examples

### Basic Analysis

```python
from system import ForexAgentSystem

# Initialize system
system = ForexAgentSystem()

# Analyze a currency pair
result = system.analyze("EUR/USD")

# Get decision
decision = result["decision"]
print(f"Action: {decision['action']}")  # BUY, SELL, or WAIT
print(f"Confidence: {decision['confidence']:.0%}")
```

### Custom Account Settings

```python
# Initialize with custom settings
system = ForexAgentSystem(
    account_balance=50000.0,   # $50k account
    max_risk_per_trade=0.01     # 1% risk per trade
)

result = system.analyze("GBP/USD")
```

### Multiple Pairs

```python
system = ForexAgentSystem()

pairs = ["EUR/USD", "GBP/USD", "USD/JPY"]
for pair in pairs:
    result = system.analyze(pair, verbose=False)
    print(f"{pair}: {result['decision']['action']}")
```

### Access Agent Results

```python
result = system.analyze("EUR/USD")

# News data
news_data = result["agent_results"]["news"]["data"]
print(f"Sentiment: {news_data['sentiment']}")

# Technical data
tech_data = result["agent_results"]["technical"]["data"]
print(f"Trend: {tech_data['trend']}")
print(f"RSI: {tech_data['indicators']['rsi']}")

# Risk data
risk_data = result["agent_results"]["risk"]["data"]
print(f"Position Size: {risk_data['position_size']} lots")

# Web sources
sources = result["decision"]["grounding_metadata"]["sources"]
for source in sources:
    print(f"{source['title']}: {source['url']}")
```

## 📁 Project Structure

```
vibecode_claude/
├── agents/                  # Individual agent implementations
│   ├── news_agent.py       # News and sentiment analysis
│   ├── technical_agent.py  # Technical indicators
│   ├── fundamental_agent.py # Economic fundamentals
│   └── risk_agent.py       # Position sizing and risk
│
├── graph/                   # LangGraph components
│   ├── state.py            # State definition
│   ├── nodes.py            # Node functions
│   └── workflow.py         # Workflow builder
│
├── examples/                # Usage examples
│   └── basic_usage.py      # Example scripts
│
├── system.py               # Main ForexAgentSystem class
├── main.py                 # CLI entry point
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

- `GOOGLE_AI_API_KEY` (required): Your Google AI API key
- `ACCOUNT_BALANCE` (optional): Trading account balance (default: 10000.0)
- `MAX_RISK_PER_TRADE` (optional): Max risk per trade as decimal (default: 0.02 = 2%)

### System Parameters

```python
system = ForexAgentSystem(
    account_balance=10000.0,     # Account size in USD
    max_risk_per_trade=0.02,     # 2% risk per trade
    api_key="your_key_here"      # Or from .env
)
```

## 📊 Output Format

The system returns a structured result:

```python
{
    "pair": "EUR/USD",
    "decision": {
        "action": "BUY|SELL|WAIT",
        "confidence": 0.0-1.0,
        "reasoning": {
            "summary": "...",
            "web_verification": "...",
            "key_factors": ["factor1", "factor2"],
            "risks": ["risk1", "risk2"]
        },
        "trade_parameters": {
            "entry_price": 1.0850,
            "stop_loss": 1.0800,
            "take_profit": 1.0950,
            "position_size": 0.20
        },
        "grounding_metadata": {
            "search_queries": ["EUR/USD live", ...],
            "sources": [
                {"title": "...", "url": "..."},
                ...
            ]
        }
    },
    "agent_results": {
        "news": {...},
        "technical": {...},
        "fundamental": {...},
        "risk": {...}
    }
}
```

## 🎓 How It Works

### 1. Agent Execution

Each agent analyzes the currency pair from its perspective:

- **News Agent**: Sentiment analysis from headlines
- **Technical Agent**: Price patterns and indicators
- **Fundamental Agent**: Economic data comparison
- **Risk Agent**: Position sizing and validation

### 2. Risk Validation

The Risk Agent validates:
- Stop loss distance (10-100 pips)
- Risk/reward ratio (minimum 1.5:1)
- Position size based on account balance
- Maximum risk per trade (default 2%)

If validation fails, the workflow ends with `WAIT`.

### 3. Synthesis with Gemini

The Synthesis Agent:
1. Receives all agent outputs (mock data)
2. Uses Google Search for real-time verification
3. Synthesizes information into a final decision
4. Provides reasoning and citations

### 4. LangGraph Orchestration

LangGraph provides:
- **State Management**: Passes data between agents
- **Conditional Routing**: Skips synthesis if risk rejected
- **Error Handling**: Graceful failure of individual agents
- **Visualization**: See the workflow graph

## 🔍 Visualize Workflow

```python
from system import ForexAgentSystem

system = ForexAgentSystem()
system.visualize()  # Requires IPython
```

Or get workflow info:
```python
info = system.get_info()
print(info["workflow"])
```

## 💰 Cost Analysis

Per analysis:
- Agent execution: FREE (local mock data)
- Gemini synthesis: ~$0.080
- Google Search grounding: ~$0.015
- **Total: ~$0.095 per analysis**

With 100 analyses/day: $9.50/day = $285/month

## 🚧 Limitations & Future Work

### Current Limitations

1. **Mock Data**: News, technical, and fundamental agents use mock data
   - Future: Connect to real APIs (NewsAPI, Yahoo Finance, FRED)

2. **Simple Risk Model**: Basic position sizing
   - Future: Advanced risk models (Kelly Criterion, Monte Carlo)

3. **No Trade Execution**: Analysis only
   - Future: Integration with brokers (OANDA, Interactive Brokers)

### Planned Enhancements

- [ ] Real data integration (APIs)
- [ ] Historical backtesting
- [ ] Portfolio management
- [ ] Human-in-the-loop approval
- [ ] Real-time monitoring
- [ ] Performance tracking
- [ ] Multi-timeframe analysis
- [ ] Correlation analysis

## 🤝 Contributing

This is a demonstration project. Feel free to:
- Fork and modify
- Add real data sources
- Improve risk models
- Add new agents
- Enhance the synthesis prompt

## ⚠️ Disclaimer

**This software is for educational purposes only.**

- NOT financial advice
- NOT suitable for real trading without modifications
- USE AT YOUR OWN RISK
- Always do your own research
- Never risk more than you can afford to lose

The creators are not responsible for any financial losses incurred using this software.

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **LangGraph**: Agent orchestration framework
- **Google Gemini**: LLM synthesis
- **Google Search**: Real-time data grounding

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Built with ❤️ using LangGraph + Gemini**
