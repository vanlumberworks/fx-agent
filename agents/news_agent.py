"""News Agent - Analyzes market news and sentiment using Google Search."""

import os
import json
from typing import Dict, Any
from datetime import datetime


class NewsAgent:
    """
    Analyzes news and market sentiment for a currency pair using Google Search.

    Now powered by:
    - Gemini 2.5 Flash with Google Search grounding
    - Real-time news headlines from the web
    - Actual sentiment analysis based on current events
    - Source citations for all news items

    Previously: Used mock/template headlines
    Now: Uses real Google Search results!
    """

    def __init__(self):
        self.name = "NewsAgent"

    async def analyze(self, pair: str) -> Dict[str, Any]:
        """
        Analyze news for the given currency pair using Google Search.

        Args:
            pair: Currency pair (e.g., "EUR/USD", "XAU/USD")

        Returns:
            Dict with analysis results including real headlines and sources
        """
        try:
            from google import genai
            from google.genai import types

            # Get API key
            api_key = os.getenv("GOOGLE_AI_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_AI_API_KEY not found in environment")

            # Initialize Gemini client
            client = genai.Client(api_key=api_key)

            # Extract currencies for better search
            base, quote = self._parse_pair(pair)

            # Build search-powered analysis prompt
            prompt = self._build_news_prompt(pair, base, quote)

            # Configure Google Search grounding
            grounding_tool = types.Tool(google_search=types.GoogleSearch())

            config_gemini = types.GenerateContentConfig(
                temperature=0.2,  # Low temperature for factual news analysis
                response_mime_type="application/json",
                tools=[grounding_tool],
                thinking_config=types.ThinkingConfig(thinking_budget=0),  # Speed over thinking
            )

            # Generate analysis with Google Search
            response = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt], config=config_gemini)

            # Parse response
            analysis = json.loads(response.text)

            # Extract grounding metadata (sources)
            sources = []
            search_queries = []

            if response.candidates[0].grounding_metadata:
                metadata = response.candidates[0].grounding_metadata

                # Get search queries used
                search_queries = metadata.web_search_queries or []

                # Get source citations
                if metadata.grounding_chunks:
                    sources = [{"title": c.web.title, "url": c.web.uri} for c in metadata.grounding_chunks]

            # Build result with grounding metadata
            return {
                "success": True,
                "agent": self.name,
                "data": {
                    "pair": pair,
                    "headlines": analysis.get("headlines", []),
                    "sentiment_score": analysis.get("sentiment_score", 0.0),
                    "sentiment": analysis.get("sentiment", "neutral"),
                    "impact": analysis.get("impact", "medium"),
                    "news_count": len(analysis.get("headlines", [])),
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "summary": analysis.get("summary", "No summary available"),
                    "key_events": analysis.get("key_events", []),
                    # Grounding metadata
                    "search_queries": search_queries,
                    "sources": sources,
                    "data_source": "google_search",  # Indicates real data
                },
            }

        except Exception as e:
            # Fallback to basic error response
            print(f"  ⚠️  News Agent error: {str(e)}")
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "data": {},
            }

    def _parse_pair(self, pair: str) -> tuple:
        """Parse trading pair into base and quote currencies."""
        if "/" in pair:
            base, quote = pair.split("/")
        else:
            # Assume format like "EURUSD"
            base = pair[:3]
            quote = pair[3:]
        return base.upper(), quote.upper()

    def _build_news_prompt(self, pair: str, base: str, quote: str) -> str:
        """Build the news analysis prompt for Gemini with Google Search."""
        return f"""You are a forex news analyst with real-time access to Google Search.

TASK: Analyze current news and market sentiment for {pair} ({base}/{quote})

Use Google Search to find:
1. Recent news headlines (last 24-48 hours) about:
   - "{pair} forex news"
   - "{base} currency news"
   - "{quote} currency news"
   - "{base} central bank"
   - "{base} economy"

2. Major events affecting the currencies:
   - Central bank decisions
   - Economic data releases
   - Geopolitical events
   - Market sentiment shifts

ANALYSIS REQUIREMENTS:

1. **Headlines** (3-5 most relevant)
   - Extract ACTUAL recent headlines from search results
   - Include publication date/time if available
   - Focus on market-moving news

2. **Sentiment Analysis**
   - Analyze overall market sentiment from headlines
   - Score: -1.0 (very bearish) to +1.0 (very bullish)
   - Consider: tone, events, analyst opinions

3. **Impact Assessment**
   - high: Major events (rate decisions, GDP, crises)
   - medium: Notable events (inflation data, forecasts)
   - low: Minor events (routine statements)

4. **Key Events**
   - List 2-3 most important recent events
   - Include dates and brief descriptions

OUTPUT FORMAT (JSON):
{{
  "headlines": [
    {{
      "title": "Actual headline from search results",
      "date": "2025-11-05" (if available, else "recent"),
      "sentiment": "bullish|bearish|neutral",
      "source": "Publication name if available"
    }}
  ],
  "sentiment_score": 0.0 to 1.0 or -1.0 to 0.0,
  "sentiment": "bullish|bearish|neutral",
  "impact": "high|medium|low",
  "key_events": [
    "Event 1: Description",
    "Event 2: Description"
  ],
  "summary": "Brief summary of market sentiment and why (1-2 sentences)"
}}

CRITICAL:
- Use ONLY information from Google Search results
- Do NOT make up headlines or events
- If no recent news found, indicate in summary
- Be objective and fact-based
- Sentiment must reflect actual market conditions

Analyze now: {pair}
"""
