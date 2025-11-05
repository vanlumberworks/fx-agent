"""Technical Agent - Performs intelligent technical analysis using Gemini."""

import os
import json
from typing import Dict, Any
from datetime import datetime


class TechnicalAgent:
    """
    Performs technical analysis using Gemini LLM for intelligent reasoning.

    Now powered by:
    - Real-time prices from external APIs
    - Gemini LLM for technical analysis reasoning
    - Optional Google Search for additional technical insights
    - Structured JSON output for better LangGraph integration

    Architecture:
    1. Fetch real price (from Price Service)
    2. Use Gemini to analyze technical patterns
    3. Generate trading signals with reasoning
    4. Return structured JSON
    """

    def __init__(self, use_real_prices: bool = True, use_llm: bool = True):
        self.name = "TechnicalAgent"
        self.use_real_prices = use_real_prices
        self.use_llm = use_llm

    async def analyze(self, pair: str) -> Dict[str, Any]:
        """
        Perform technical analysis with LLM reasoning.

        Args:
            pair: Currency pair (e.g., "EUR/USD", "XAU/USD", "BTC/USD")

        Returns:
            Dict with structured technical analysis results
        """
        try:
            # Get current price with historical context
            price_data, price_source = self._get_price(pair)

            # Extract current price
            current_price = price_data["price"] if isinstance(price_data, dict) else price_data

            if self.use_llm:
                # Use Gemini for intelligent analysis
                return await self._analyze_with_llm(pair, price_data, price_source)
            else:
                # Fallback to rule-based analysis
                return self._analyze_rule_based(pair, current_price, price_source)

        except Exception as e:
            print(f"  ⚠️  Technical Agent error: {str(e)}")
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "data": {},
            }

    async def _analyze_with_llm(self, pair: str, price_data: Dict[str, Any], price_source: str) -> Dict[str, Any]:
        """Use Gemini LLM for intelligent technical analysis."""
        from google import genai
        from google.genai import types

        # Get API key
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_AI_API_KEY not found")

        # Initialize Gemini
        client = genai.Client(api_key=api_key)

        # Extract price information
        current_price = price_data["price"] if isinstance(price_data, dict) else price_data

        # Build analysis prompt with historical context
        prompt = self._build_technical_prompt(pair, price_data, price_source)

        # Configure Gemini (with optional Google Search for technical insights)
        tools = []
        if price_source == "real":
            # Only use Google Search if we have real prices
            # This adds technical analysis context from the web
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            tools.append(grounding_tool)

        config = types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json",
            tools=tools if tools else None,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )

        # Generate analysis
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=config
        )

        # Parse response
        analysis = json.loads(response.text)

        # Extract grounding if available
        sources = []
        search_queries = []
        if response.candidates[0].grounding_metadata:
            metadata = response.candidates[0].grounding_metadata
            search_queries = metadata.web_search_queries or []
            if metadata.grounding_chunks:
                sources = [{"title": c.web.title, "url": c.web.uri} for c in metadata.grounding_chunks]

        # Build structured result
        return {
            "success": True,
            "agent": self.name,
            "data": {
                "pair": pair,
                "current_price": current_price,
                "price_source": price_source,
                # Technical analysis from LLM
                "trend": analysis.get("trend", "unknown"),
                "trend_strength": analysis.get("trend_strength", "medium"),
                "support": analysis.get("support"),
                "resistance": analysis.get("resistance"),
                "indicators": analysis.get("indicators", {}),
                "signals": analysis.get("signals", {}),
                "stop_loss": analysis.get("stop_loss"),
                "take_profit": analysis.get("take_profit"),
                # LLM reasoning
                "analysis": analysis.get("analysis", ""),
                "reasoning": analysis.get("reasoning", ""),
                "key_levels": analysis.get("key_levels", []),
                # Metadata
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "summary": analysis.get("summary", ""),
                "data_source": "llm_analysis",
                "search_queries": search_queries,
                "sources": sources,
            },
        }

    def _analyze_rule_based(self, pair: str, current_price: float, price_source: str) -> Dict[str, Any]:
        """Fallback rule-based analysis (original logic)."""
        import random

        # Simple rule-based indicators
        indicators = {
            "rsi": round(random.uniform(30, 70), 2),
            "macd": round(random.uniform(-0.01, 0.01), 4),
            "moving_avg_50": round(current_price * random.uniform(0.98, 1.02), 5),
            "moving_avg_200": round(current_price * random.uniform(0.95, 1.05), 5),
        }

        # Simple trend
        trend = "uptrend" if indicators["rsi"] > 50 else "downtrend" if indicators["rsi"] < 50 else "sideways"

        # Simple levels
        support = round(current_price * 0.98, 5)
        resistance = round(current_price * 1.02, 5)

        # Simple signals
        signals = {
            "buy": "moderate" if indicators["rsi"] < 40 else "weak",
            "sell": "moderate" if indicators["rsi"] > 60 else "weak",
            "overall": "BUY" if indicators["rsi"] < 40 else "SELL" if indicators["rsi"] > 60 else "HOLD",
        }

        return {
            "success": True,
            "agent": self.name,
            "data": {
                "pair": pair,
                "current_price": current_price,
                "price_source": price_source,
                "trend": trend,
                "support": support,
                "resistance": resistance,
                "indicators": indicators,
                "signals": signals,
                "stop_loss": round(support * 0.995, 5),
                "take_profit": round(resistance * 1.005, 5),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "summary": f"Technical analysis shows {trend} with {signals['overall']} signal.",
                "data_source": "rule_based",
            },
        }

    def _get_price(self, pair: str) -> tuple:
        """Get current price for the pair with historical context."""
        if self.use_real_prices:
            from agents.price_service import get_price_service

            price_service = get_price_service()
            price_data = price_service.get_enriched_price(pair)

            if price_data:
                print(f"     💰 Real price: ${price_data['price']} from {price_data['source']}")

                # Show historical context if available
                if "historical" in price_data and price_data["historical"]["price_change_pct"] is not None:
                    change_pct = price_data["historical"]["price_change_pct"]
                    direction = "📈" if change_pct > 0 else "📉"
                    print(f"     {direction} 24h change: {change_pct:+.2f}%")

                return price_data, "real"
            else:
                print(f"     ⚠️  Failed to get real price, using mock")

        # Fallback to mock
        mock_price = self._get_mock_price(pair)
        mock_data = {"price": mock_price, "historical": None, "ohlc": None}
        return mock_data, "mock"

    def _get_mock_price(self, pair: str) -> float:
        """Get mock price for testing."""
        import random
        price_ranges = {
            "EUR/USD": (1.05, 1.12),
            "GBP/USD": (1.20, 1.30),
            "USD/JPY": (140.0, 152.0),
            "XAU/USD": (2600.0, 2700.0),
            "BTC/USD": (90000.0, 100000.0),
        }
        range_vals = price_ranges.get(pair, (1.0, 1.5))
        return round(random.uniform(range_vals[0], range_vals[1]), 2)

    def _build_technical_prompt(self, pair: str, price_data: Dict[str, Any], price_source: str) -> str:
        """Build the technical analysis prompt for Gemini with historical context."""

        # Extract price information
        current_price = price_data["price"] if isinstance(price_data, dict) else price_data

        # Build price context with historical data
        price_context = ""
        if price_source == "real":
            price_context = f"You have access to REAL-TIME price data via Google Search.\n\n"
            price_context += f"**Current Price**: ${current_price}\n"

            # Add historical context if available
            if isinstance(price_data, dict) and "historical" in price_data and price_data["historical"]:
                hist = price_data["historical"]
                if hist["yesterday_rate"]:
                    price_context += f"**Yesterday's Price**: ${hist['yesterday_rate']}\n"
                if hist["price_change_pct"] is not None:
                    direction = "UP" if hist["price_change_pct"] > 0 else "DOWN"
                    price_context += f"**24h Change**: {hist['price_change_pct']:+.2f}% ({direction})\n"

            # Add OHLC data if available
            if isinstance(price_data, dict) and "ohlc" in price_data and price_data["ohlc"]:
                ohlc = price_data["ohlc"]
                price_context += f"\n**Yesterday's OHLC**:\n"
                price_context += f"- Open: ${ohlc['open']}\n"
                price_context += f"- High: ${ohlc['high']}\n"
                price_context += f"- Low: ${ohlc['low']}\n"
                price_context += f"- Close: ${ohlc['close']}\n"
        else:
            price_context = f"Current price: ${current_price} (simulated for testing)"

        return f"""You are an expert technical analyst for forex, commodities, and cryptocurrency markets.

TASK: Perform technical analysis for {pair}

{price_context}

ANALYSIS REQUIREMENTS:

1. **Trend Analysis**
   - Identify current trend: uptrend, downtrend, or sideways
   - Assess trend strength: strong, medium, weak
   - Consider: moving averages, price action, momentum

2. **Support & Resistance**
   - Calculate key support level (price floor)
   - Calculate key resistance level (price ceiling)
   - Base on: recent price action, round numbers, historical levels

3. **Technical Indicators** (estimate based on current price)
   - RSI (0-100): Overbought (>70) or oversold (<30)?
   - MACD: Bullish or bearish crossover?
   - Moving Averages: Price above or below key MAs?
   - Momentum: Increasing or decreasing?

4. **Trading Signals**
   - Buy signal strength: strong, moderate, weak, none
   - Sell signal strength: strong, moderate, weak, none
   - Overall signal: BUY, SELL, or HOLD
   - Confidence level (0.0-1.0)

5. **Risk Levels**
   - Stop loss: Price level to limit losses
   - Take profit: Price target for profit
   - Risk/reward ratio estimate

6. **Key Technical Levels**
   - List 3-5 important price levels to watch

REASONING:
- Provide clear analysis of why you chose these levels
- Explain the technical setup
- Note any patterns or formations
- Mention key factors influencing the analysis

OUTPUT FORMAT (JSON):
{{
  "trend": "uptrend|downtrend|sideways",
  "trend_strength": "strong|medium|weak",
  "support": 1.0800,
  "resistance": 1.0950,
  "indicators": {{
    "rsi": 65,
    "macd": "bullish",
    "ma_position": "above_50ma",
    "momentum": "increasing"
  }},
  "signals": {{
    "buy": "moderate",
    "sell": "weak",
    "overall": "BUY",
    "confidence": 0.75
  }},
  "stop_loss": 1.0780,
  "take_profit": 1.0980,
  "key_levels": [
    "1.0800 - Strong support",
    "1.0850 - Current price",
    "1.0900 - Resistance zone",
    "1.0950 - Major resistance"
  ],
  "analysis": "Technical analysis shows a clear uptrend with price above key moving averages. RSI at 65 indicates bullish momentum without being overbought.",
  "reasoning": "Buy signal based on: 1) Price above 50-day MA, 2) RSI in bullish zone, 3) Support holding at 1.0800",
  "summary": "Bullish technical setup with BUY signal. Enter near support with stop below 1.0780."
}}

CRITICAL:
- Be realistic and objective
- Base analysis on actual technical principles
- Don't be overly bullish or bearish
- If uncertain, use moderate signals
- Price levels must be logical (support < current < resistance)

Analyze now: {pair} at ${current_price}
"""
