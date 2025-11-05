"""Risk Agent - Calculates position sizing and risk parameters."""

from typing import Dict, Any
from datetime import datetime


class RiskAgent:
    """
    Calculates risk management parameters for trades.

    Implements proper position sizing, stop loss, take profit, and risk/reward analysis.
    """

    def __init__(self, account_balance: float = 10000.0, max_risk_per_trade: float = 0.02):
        """
        Initialize Risk Agent.

        Args:
            account_balance: Total account balance
            max_risk_per_trade: Maximum risk per trade as decimal (e.g., 0.02 = 2%)
        """
        self.name = "RiskAgent"
        self.account_balance = account_balance
        self.max_risk_per_trade = max_risk_per_trade

    def analyze(
        self,
        pair: str,
        entry_price: float,
        stop_loss: float,
        direction: str,
        take_profit: float = None,
        leverage: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Calculate risk parameters for a trade.

        Args:
            pair: Currency pair (e.g., "EUR/USD")
            entry_price: Proposed entry price
            stop_loss: Stop loss price
            direction: "BUY" or "SELL"
            take_profit: Take profit price (optional)
            leverage: Leverage to use (default 1.0 = no leverage)

        Returns:
            Dict with risk analysis results
        """
        try:
            # Calculate risk per pip
            risk_in_pips = self._calculate_pips(entry_price, stop_loss, direction)

            # Calculate position size
            position_size = self._calculate_position_size(risk_in_pips, pair)

            # Calculate dollar risk
            dollar_risk = self.account_balance * self.max_risk_per_trade

            # Calculate reward if take profit provided
            reward_data = {}
            if take_profit:
                reward_in_pips = self._calculate_pips(entry_price, take_profit, direction, reward=True)
                risk_reward_ratio = reward_in_pips / risk_in_pips if risk_in_pips > 0 else 0
                potential_profit = (reward_in_pips / risk_in_pips) * dollar_risk if risk_in_pips > 0 else 0

                reward_data = {
                    "take_profit": take_profit,
                    "reward_in_pips": round(reward_in_pips, 1),
                    "risk_reward_ratio": round(risk_reward_ratio, 2),
                    "potential_profit": round(potential_profit, 2),
                }

            # Validate trade
            trade_approved, rejection_reason = self._validate_trade(risk_in_pips, risk_reward_ratio if take_profit else None)

            return {
                "success": True,
                "agent": self.name,
                "data": {
                    "pair": pair,
                    "direction": direction,
                    "entry_price": entry_price,
                    "stop_loss": stop_loss,
                    "risk_in_pips": round(risk_in_pips, 1),
                    "position_size": round(position_size, 2),
                    "dollar_risk": round(dollar_risk, 2),
                    "risk_percentage": round(self.max_risk_per_trade * 100, 2),
                    "leverage": leverage,
                    "account_balance": self.account_balance,
                    **reward_data,
                    "trade_approved": trade_approved,
                    "rejection_reason": rejection_reason,
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "summary": self._generate_summary(trade_approved, position_size, dollar_risk, rejection_reason),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "data": {},
            }

    def _calculate_pips(self, entry: float, exit: float, direction: str, reward: bool = False) -> float:
        """Calculate pip distance between two prices."""
        # For most pairs, 1 pip = 0.0001
        # For JPY pairs, 1 pip = 0.01
        pip_multiplier = 10000  # Standard pairs
        # TODO: Detect JPY pairs and use 100 instead

        if direction == "BUY":
            if reward:
                return abs(exit - entry) * pip_multiplier
            else:
                return abs(entry - exit) * pip_multiplier
        else:  # SELL
            if reward:
                return abs(entry - exit) * pip_multiplier
            else:
                return abs(exit - entry) * pip_multiplier

    def _calculate_position_size(self, risk_in_pips: float, pair: str) -> float:
        """
        Calculate position size in lots.

        Formula: Position Size = (Account Risk) / (Risk in Pips * Pip Value)
        """
        # Standard lot = 100,000 units
        # Pip value for standard lot on EUR/USD = $10
        # We'll calculate position size in standard lots

        dollar_risk = self.account_balance * self.max_risk_per_trade
        pip_value_per_standard_lot = 10  # USD

        if risk_in_pips <= 0:
            return 0.0

        # Position size in standard lots
        position_size = dollar_risk / (risk_in_pips * pip_value_per_standard_lot)

        return position_size

    def _validate_trade(self, risk_in_pips: float, risk_reward_ratio: float = None) -> tuple:
        """
        Validate if trade meets risk management criteria.

        Returns:
            (approved: bool, reason: str or None)
        """
        # Rule 1: Risk must be positive
        if risk_in_pips <= 0:
            return False, "Invalid stop loss: risk in pips must be positive"

        # Rule 2: Risk must not be too large (e.g., max 100 pips)
        if risk_in_pips > 100:
            return False, f"Risk too high: {risk_in_pips:.1f} pips exceeds maximum of 100 pips"

        # Rule 3: Risk/Reward ratio must be at least 1.5:1 if provided
        if risk_reward_ratio is not None:
            if risk_reward_ratio < 1.5:
                return False, f"Poor risk/reward ratio: {risk_reward_ratio:.2f} is below minimum of 1.5"

        # Rule 4: Risk must not be too small (e.g., min 10 pips)
        if risk_in_pips < 10:
            return False, f"Risk too small: {risk_in_pips:.1f} pips is below minimum of 10 pips"

        return True, None

    def _generate_summary(self, approved: bool, position_size: float, dollar_risk: float, reason: str = None) -> str:
        """Generate risk analysis summary."""
        if not approved:
            return f"Trade REJECTED: {reason}"

        return f"Trade APPROVED: Position size {position_size:.2f} lots, risking ${dollar_risk:.2f} ({self.max_risk_per_trade*100:.1f}% of account)."
