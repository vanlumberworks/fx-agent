"""News Agent - Analyzes market news and sentiment."""

from typing import Dict, Any
from datetime import datetime, timedelta
import random


class NewsAgent:
    """
    Analyzes news and market sentiment for a currency pair.

    In production, this would connect to real news APIs (NewsAPI, Bloomberg, etc.)
    For now, it provides realistic mock data.
    """

    def __init__(self):
        self.name = "NewsAgent"

    def analyze(self, pair: str) -> Dict[str, Any]:
        """
        Analyze news for the given currency pair.

        Args:
            pair: Currency pair (e.g., "EUR/USD")

        Returns:
            Dict with analysis results
        """
        try:
            # Extract currencies
            base, quote = pair.split("/")

            # Mock news headlines (realistic examples)
            headlines = self._generate_mock_headlines(base, quote)

            # Calculate sentiment
            sentiment_score = self._calculate_sentiment(headlines)

            # Determine impact
            impact = self._assess_impact(sentiment_score)

            return {
                "success": True,
                "agent": self.name,
                "data": {
                    "pair": pair,
                    "headlines": headlines,
                    "sentiment_score": sentiment_score,  # -1 to 1
                    "sentiment": self._sentiment_label(sentiment_score),
                    "impact": impact,
                    "news_count": len(headlines),
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "summary": self._generate_summary(base, quote, sentiment_score),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "data": {},
            }

    def _generate_mock_headlines(self, base: str, quote: str) -> list:
        """Generate realistic mock news headlines."""
        templates = [
            f"{base} Central Bank signals interest rate stability",
            f"{quote} economy shows strong GDP growth",
            f"Trade tensions ease between {base} and {quote} regions",
            f"{base} inflation concerns mount amid supply chain issues",
            f"Market expects {quote} policy tightening next quarter",
        ]

        # Randomly select 3-5 headlines
        num_headlines = random.randint(3, 5)
        selected = random.sample(templates, min(num_headlines, len(templates)))

        return [
            {
                "title": headline,
                "timestamp": (datetime.utcnow() - timedelta(hours=random.randint(1, 48))).isoformat(),
                "sentiment": random.choice(["bullish", "bearish", "neutral"]),
            }
            for headline in selected
        ]

    def _calculate_sentiment(self, headlines: list) -> float:
        """Calculate overall sentiment score."""
        sentiment_map = {"bullish": 0.7, "neutral": 0.0, "bearish": -0.7}

        if not headlines:
            return 0.0

        total = sum(sentiment_map.get(h["sentiment"], 0.0) for h in headlines)
        return round(total / len(headlines), 2)

    def _sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label."""
        if score > 0.3:
            return "bullish"
        elif score < -0.3:
            return "bearish"
        else:
            return "neutral"

    def _assess_impact(self, sentiment_score: float) -> str:
        """Assess the impact level."""
        abs_score = abs(sentiment_score)
        if abs_score > 0.6:
            return "high"
        elif abs_score > 0.3:
            return "medium"
        else:
            return "low"

    def _generate_summary(self, base: str, quote: str, sentiment: float) -> str:
        """Generate a summary of the news analysis."""
        sentiment_label = self._sentiment_label(sentiment)

        if sentiment_label == "bullish":
            return f"News sentiment is bullish for {base}/{quote}. Positive economic indicators and policy signals suggest upward pressure."
        elif sentiment_label == "bearish":
            return f"News sentiment is bearish for {base}/{quote}. Negative headlines and economic concerns suggest downward pressure."
        else:
            return f"News sentiment is neutral for {base}/{quote}. Mixed signals with no clear directional bias."
