"""Fundamental Agent - Performs intelligent fundamental analysis using Gemini."""

import os
import json
from typing import Dict, Any
from datetime import datetime


class FundamentalAgent:
    """
    Performs fundamental economic analysis using Gemini LLM for intelligent reasoning.

    Now powered by:
    - Google Search for real-time economic data
    - Gemini LLM for fundamental analysis reasoning
    - Structured JSON output for better LangGraph integration

    Architecture:
    1. Use Gemini + Google Search to fetch real economic data
    2. Analyze GDP, inflation, interest rates, central bank policy
    3. Compare base vs quote currency fundamentals
    4. Generate trading outlook with reasoning
    5. Return structured JSON
    """

    def __init__(self, use_llm: bool = True):
        self.name = "FundamentalAgent"
        self.use_llm = use_llm

    async def analyze(self, pair: str) -> Dict[str, Any]:
        """
        Perform fundamental analysis with LLM reasoning and Google Search.

        Args:
            pair: Currency pair (e.g., "EUR/USD", "XAU/USD", "BTC/USD")

        Returns:
            Dict with structured fundamental analysis results
        """
        try:
            if self.use_llm:
                # Use Gemini + Google Search for intelligent analysis
                return await self._analyze_with_llm(pair)
            else:
                # Fallback to rule-based analysis
                return self._analyze_rule_based(pair)

        except Exception as e:
            print(f"  ⚠️  Fundamental Agent error: {str(e)}")
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "data": {},
            }

    async def _analyze_with_llm(self, pair: str) -> Dict[str, Any]:
        """Use Gemini LLM + Google Search for intelligent fundamental analysis."""
        from google import genai
        from google.genai import types

        # Get API key
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_AI_API_KEY not found")

        # Initialize Gemini
        client = genai.Client(api_key=api_key)

        # Build analysis prompt
        prompt = self._build_fundamental_prompt(pair)

        # Configure Gemini with Google Search for real economic data
        grounding_tool = types.Tool(google_search=types.GoogleSearch())

        config = types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json",
            tools=[grounding_tool],
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
                # Base currency fundamentals
                "base_currency": analysis.get("base_currency", {}),
                # Quote currency fundamentals
                "quote_currency": analysis.get("quote_currency", {}),
                # Comparison
                "comparison": analysis.get("comparison", {}),
                "fundamental_score": analysis.get("fundamental_score", 0.0),
                "outlook": analysis.get("outlook", "neutral"),
                # LLM reasoning
                "analysis": analysis.get("analysis", ""),
                "reasoning": analysis.get("reasoning", ""),
                "key_factors": analysis.get("key_factors", []),
                "central_bank_policy": analysis.get("central_bank_policy", {}),
                # Metadata
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "summary": analysis.get("summary", ""),
                "data_source": "llm_analysis",
                "search_queries": search_queries,
                "sources": sources,
            },
        }

    def _analyze_rule_based(self, pair: str) -> Dict[str, Any]:
        """Fallback rule-based analysis (original logic)."""
        import random

        try:
            # Extract currencies
            base, quote = pair.split("/")

            # Get mock economic data
            base_data = self._get_mock_economic_data(base)
            quote_data = self._get_mock_economic_data(quote)

            # Compare fundamentals
            comparison = self._compare_fundamentals(base_data, quote_data)

            # Calculate fundamental score
            fundamental_score = self._calculate_score(comparison)

            return {
                "success": True,
                "agent": self.name,
                "data": {
                    "pair": pair,
                    "base_currency": {
                        "currency": base,
                        "data": base_data,
                    },
                    "quote_currency": {
                        "currency": quote,
                        "data": quote_data,
                    },
                    "comparison": comparison,
                    "fundamental_score": fundamental_score,
                    "outlook": self._get_outlook(fundamental_score),
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "summary": self._generate_summary(base, quote, fundamental_score),
                    "data_source": "rule_based",
                },
            }

        except Exception as e:
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "data": {},
            }

    def _get_mock_economic_data(self, currency: str) -> Dict[str, Any]:
        """Get mock economic data for testing."""
        import random

        # Currency-specific base values (realistic ranges)
        data_ranges = {
            "EUR": {"gdp_growth": (1.0, 2.5), "inflation": (2.0, 4.0), "interest_rate": (3.5, 4.5)},
            "USD": {"gdp_growth": (2.0, 3.5), "inflation": (2.5, 4.5), "interest_rate": (4.5, 5.5)},
            "GBP": {"gdp_growth": (0.5, 2.0), "inflation": (3.0, 5.0), "interest_rate": (4.5, 5.5)},
            "JPY": {"gdp_growth": (0.5, 1.5), "inflation": (1.0, 3.0), "interest_rate": (0.0, 0.5)},
            "AUD": {"gdp_growth": (1.5, 3.0), "inflation": (2.5, 4.5), "interest_rate": (3.5, 4.5)},
            "XAU": {"gdp_growth": (0.0, 0.0), "inflation": (0.0, 0.0), "interest_rate": (0.0, 0.0)},  # Commodity
            "BTC": {"gdp_growth": (0.0, 0.0), "inflation": (0.0, 0.0), "interest_rate": (0.0, 0.0)},  # Crypto
        }

        ranges = data_ranges.get(currency, {"gdp_growth": (1.0, 3.0), "inflation": (2.0, 4.0), "interest_rate": (2.0, 5.0)})

        return {
            "gdp_growth": round(random.uniform(*ranges["gdp_growth"]), 2),
            "inflation": round(random.uniform(*ranges["inflation"]), 2),
            "interest_rate": round(random.uniform(*ranges["interest_rate"]), 2),
            "unemployment": round(random.uniform(3.5, 7.0), 1),
            "trade_balance": round(random.uniform(-50, 50), 1),
            "debt_to_gdp": round(random.uniform(60, 120), 1),
        }

    def _compare_fundamentals(self, base_data: Dict, quote_data: Dict) -> Dict[str, str]:
        """Compare fundamental metrics between currencies."""
        comparison = {}

        # GDP Growth
        if base_data["gdp_growth"] > quote_data["gdp_growth"] * 1.1:
            comparison["gdp_growth"] = "base_stronger"
        elif quote_data["gdp_growth"] > base_data["gdp_growth"] * 1.1:
            comparison["gdp_growth"] = "quote_stronger"
        else:
            comparison["gdp_growth"] = "neutral"

        # Interest Rate (higher is typically better for currency strength)
        if base_data["interest_rate"] > quote_data["interest_rate"] + 0.5:
            comparison["interest_rate"] = "base_stronger"
        elif quote_data["interest_rate"] > base_data["interest_rate"] + 0.5:
            comparison["interest_rate"] = "quote_stronger"
        else:
            comparison["interest_rate"] = "neutral"

        # Inflation (lower is better)
        if base_data["inflation"] < quote_data["inflation"] * 0.9:
            comparison["inflation"] = "base_stronger"
        elif quote_data["inflation"] < base_data["inflation"] * 0.9:
            comparison["inflation"] = "quote_stronger"
        else:
            comparison["inflation"] = "neutral"

        # Unemployment (lower is better)
        if base_data["unemployment"] < quote_data["unemployment"] * 0.9:
            comparison["unemployment"] = "base_stronger"
        elif quote_data["unemployment"] < base_data["unemployment"] * 0.9:
            comparison["unemployment"] = "quote_stronger"
        else:
            comparison["unemployment"] = "neutral"

        return comparison

    def _calculate_score(self, comparison: Dict[str, str]) -> float:
        """Calculate overall fundamental score."""
        weights = {
            "gdp_growth": 0.25,
            "interest_rate": 0.35,
            "inflation": 0.25,
            "unemployment": 0.15,
        }

        score = 0.0
        for metric, weight in weights.items():
            if comparison.get(metric) == "base_stronger":
                score += weight
            elif comparison.get(metric) == "quote_stronger":
                score -= weight

        return round(score, 2)

    def _get_outlook(self, score: float) -> str:
        """Get outlook based on fundamental score."""
        if score > 0.3:
            return "bullish"
        elif score < -0.3:
            return "bearish"
        else:
            return "neutral"

    def _generate_summary(self, base: str, quote: str, score: float) -> str:
        """Generate fundamental analysis summary."""
        outlook = self._get_outlook(score)

        if outlook == "bullish":
            return f"Fundamental analysis favors {base} over {quote}. Economic indicators suggest {base} strength."
        elif outlook == "bearish":
            return f"Fundamental analysis favors {quote} over {base}. Economic indicators suggest {quote} strength."
        else:
            return f"Fundamental analysis shows balanced conditions between {base} and {quote}."

    def _build_fundamental_prompt(self, pair: str) -> str:
        """Build the fundamental analysis prompt for Gemini."""

        # Parse pair to identify base and quote
        try:
            base, quote = pair.split("/")
        except:
            base, quote = "EUR", "USD"

        # Determine asset types
        commodities = ["XAU", "XAG", "XPT", "XPD"]
        crypto = ["BTC", "ETH", "XRP", "ADA"]

        base_type = "commodity" if base in commodities else "cryptocurrency" if base in crypto else "currency"
        quote_type = "commodity" if quote in commodities else "cryptocurrency" if quote in crypto else "currency"

        return f"""You are an expert fundamental analyst for forex, commodities, and cryptocurrency markets.

TASK: Perform fundamental economic analysis for {pair}

ASSET TYPES:
- Base ({base}): {base_type}
- Quote ({quote}): {quote_type}

ANALYSIS REQUIREMENTS:

1. **Economic Data Collection** (Use Google Search for real data)

   For currencies (EUR, USD, GBP, JPY, etc.):
   - Current GDP growth rate (annual %)
   - Inflation rate (CPI annual %)
   - Central bank interest rate (%)
   - Unemployment rate (%)
   - Trade balance (billions)
   - Government debt-to-GDP (%)
   - Recent central bank policy statements

   For commodities (XAU, XAG, etc.):
   - Supply/demand fundamentals
   - Industrial usage trends
   - Central bank holdings (for gold)
   - Production levels
   - Macroeconomic factors (inflation hedge, safe haven status)

   For cryptocurrencies (BTC, ETH, etc.):
   - Network fundamentals (hash rate, active addresses)
   - Adoption trends
   - Regulatory environment
   - On-chain metrics
   - Market sentiment

2. **Comparative Analysis**
   Compare {base} vs {quote} across key metrics:
   - Which has stronger economic fundamentals?
   - Interest rate differential (if applicable)
   - Growth prospects
   - Inflation outlook
   - Policy divergence

3. **Fundamental Score** (-1.0 to +1.0)
   - Positive score: Favors {base} (bullish for {pair})
   - Negative score: Favors {quote} (bearish for {pair})
   - Consider all factors with appropriate weights

4. **Outlook**: bullish, bearish, or neutral

5. **Key Factors**
   List 3-5 critical fundamental factors influencing this pair

6. **Central Bank Policy**
   Current stance and expected changes (if applicable)

REASONING:
- Provide clear analysis of economic data
- Explain why one currency/asset is fundamentally stronger
- Note any diverging policies or trends
- Mention upcoming events (rate decisions, GDP releases, etc.)

OUTPUT FORMAT (JSON):
{{
  "base_currency": {{
    "currency": "{base}",
    "asset_type": "{base_type}",
    "gdp_growth": 2.5,
    "inflation": 3.2,
    "interest_rate": 5.25,
    "unemployment": 4.1,
    "recent_data": "Latest economic indicators...",
    "central_bank": "Federal Reserve maintaining restrictive policy..."
  }},
  "quote_currency": {{
    "currency": "{quote}",
    "asset_type": "{quote_type}",
    "gdp_growth": 1.8,
    "inflation": 2.8,
    "interest_rate": 4.0,
    "unemployment": 5.2,
    "recent_data": "Latest economic indicators...",
    "central_bank": "ECB signaling potential cuts..."
  }},
  "comparison": {{
    "gdp_growth": "base_stronger",
    "interest_rate": "base_stronger",
    "inflation": "neutral",
    "unemployment": "base_stronger",
    "overall": "base has stronger fundamentals across most metrics"
  }},
  "fundamental_score": 0.65,
  "outlook": "bullish",
  "key_factors": [
    "Interest rate differential of 125 bps favors base currency",
    "Stronger GDP growth in base economy",
    "Central bank policy divergence - base tightening, quote easing",
    "Base currency showing lower unemployment",
    "Trade balance improving for base"
  ],
  "central_bank_policy": {{
    "base": "Maintaining restrictive policy to combat inflation, rates likely on hold",
    "quote": "Signaling potential rate cuts due to slowing growth",
    "divergence": "Growing policy divergence supports base currency strength"
  }},
  "analysis": "Fundamental analysis shows {base} has superior economic fundamentals compared to {quote}. Key drivers include stronger GDP growth, higher interest rates attracting capital flows, and more hawkish central bank policy. The 125 basis point rate differential is particularly significant.",
  "reasoning": "Bullish outlook based on: 1) Interest rate advantage of 125 bps, 2) Stronger economic growth at 2.5% vs 1.8%, 3) Central bank policy divergence with base maintaining restrictive stance while quote signals easing, 4) Lower unemployment indicating healthier labor market",
  "summary": "Strong fundamental case for {base} appreciation. Economic data and policy divergence favor {base} over {quote}. Monitor upcoming central bank meetings for policy shifts."
}}

CRITICAL:
- Use REAL economic data from Google Search
- Be objective and data-driven
- Consider both short-term and long-term fundamentals
- For commodities/crypto, adapt analysis to relevant metrics
- If data is unavailable, state "data not available" rather than guessing
- Recent data is more valuable than historical averages

Analyze now: {pair}
"""
