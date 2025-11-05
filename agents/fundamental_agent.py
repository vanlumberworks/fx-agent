"""Fundamental Agent - Analyzes economic fundamentals."""

from typing import Dict, Any
from datetime import datetime
import random


class FundamentalAgent:
    """
    Analyzes fundamental economic data for currency pairs.

    In production, this would fetch real economic data from APIs
    (FRED, World Bank, Trading Economics, etc.)
    """

    def __init__(self):
        self.name = "FundamentalAgent"

    def analyze(self, pair: str) -> Dict[str, Any]:
        """
        Analyze fundamental data for the given currency pair.

        Args:
            pair: Currency pair (e.g., "EUR/USD")

        Returns:
            Dict with fundamental analysis results
        """
        try:
            # Extract currencies
            base, quote = pair.split("/")

            # Get economic data for both currencies
            base_data = self._get_economic_data(base)
            quote_data = self._get_economic_data(quote)

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
                    "fundamental_score": fundamental_score,  # -1 to 1
                    "outlook": self._get_outlook(fundamental_score),
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "summary": self._generate_summary(base, quote, fundamental_score),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "data": {},
            }

    def _get_economic_data(self, currency: str) -> Dict[str, Any]:
        """Get mock economic data for a currency."""
        # Currency-specific base values (realistic ranges)
        data_ranges = {
            "EUR": {"gdp_growth": (1.0, 2.5), "inflation": (2.0, 4.0), "interest_rate": (3.5, 4.5)},
            "USD": {"gdp_growth": (2.0, 3.5), "inflation": (2.5, 4.5), "interest_rate": (4.5, 5.5)},
            "GBP": {"gdp_growth": (0.5, 2.0), "inflation": (3.0, 5.0), "interest_rate": (4.5, 5.5)},
            "JPY": {"gdp_growth": (0.5, 1.5), "inflation": (1.0, 3.0), "interest_rate": (0.0, 0.5)},
            "AUD": {"gdp_growth": (1.5, 3.0), "inflation": (2.5, 4.5), "interest_rate": (3.5, 4.5)},
        }

        ranges = data_ranges.get(currency, {"gdp_growth": (1.0, 3.0), "inflation": (2.0, 4.0), "interest_rate": (2.0, 5.0)})

        return {
            "gdp_growth": round(random.uniform(*ranges["gdp_growth"]), 2),  # Annual %
            "inflation": round(random.uniform(*ranges["inflation"]), 2),  # Annual %
            "interest_rate": round(random.uniform(*ranges["interest_rate"]), 2),  # %
            "unemployment": round(random.uniform(3.5, 7.0), 1),  # %
            "trade_balance": round(random.uniform(-50, 50), 1),  # Billions
            "debt_to_gdp": round(random.uniform(60, 120), 1),  # %
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
        # Weights for each metric
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
            return f"Fundamental analysis favors {base} over {quote}. Economic indicators suggest {base} strength with higher growth and better monetary policy."
        elif outlook == "bearish":
            return f"Fundamental analysis favors {quote} over {base}. Economic indicators suggest {quote} strength with better economic fundamentals."
        else:
            return f"Fundamental analysis shows balanced conditions between {base} and {quote}. Economic indicators are relatively neutral."
