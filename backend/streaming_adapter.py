"""Streaming adapter for ForexAgentSystem to enable real-time updates."""

import json
from typing import AsyncIterator, Dict, Any
from system import ForexAgentSystem
from utils.logger import get_logger, log_error

logger = get_logger(__name__)


class StreamingForexSystem:
    """
    Wrapper around ForexAgentSystem that provides streaming capabilities.

    This adapter:
    - Streams workflow execution steps in real-time
    - Provides detailed progress updates
    - Formats data for SSE (Server-Sent Events)
    - Handles errors gracefully
    """

    def __init__(self,
                 account_balance: float = None,
                 max_risk_per_trade: float = None,
                 api_key: str = None):
        """
        Initialize streaming system.

        Args:
            account_balance: Account balance in USD
            max_risk_per_trade: Max risk per trade as decimal
            api_key: Google AI API key
        """
        self.system = ForexAgentSystem(
            account_balance=account_balance,
            max_risk_per_trade=max_risk_per_trade,
            api_key=api_key
        )

    async def analyze_stream(self, query: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Analyze a trading query and stream results in real-time.

        This method streams events as the workflow progresses:
        1. Query parsing
        2. Agent analysis (News, Technical, Fundamental)
        3. Risk assessment
        4. Final synthesis
        5. Report generation

        Args:
            query: Natural language query or currency pair

        Yields:
            Dict events with type and data:
            - {"type": "start", "data": {"query": "..."}}
            - {"type": "query_parsed", "data": {...}}
            - {"type": "agent_start", "data": {...}}
            - {"type": "agent_progress", "data": {...}}
            - {"type": "agent_update", "data": {...}}
            - {"type": "risk_update", "data": {...}}
            - {"type": "decision", "data": {...}}
            - {"type": "report_update", "data": {...}}
            - {"type": "complete", "data": {...}}
            - {"type": "error", "data": {"error": "..."}}
        """
        logger.info(f"🔄 Starting streaming analysis for query: '{query}'")

        try:
            # Send start event
            start_event = {
                "type": "start",
                "data": {
                    "query": query,
                    "timestamp": self._get_timestamp()
                }
            }
            logger.debug(f"📤 Yielding event: {start_event['type']}")
            yield start_event

            # Prepare initial state
            inputs = {
                "user_query": query,
                "query_context": None,
                "pair": None,
                "messages": [],
                "step_count": 0,
                "news_result": None,
                "technical_result": None,
                "fundamental_result": None,
                "risk_result": None,
                "decision": None,
                "report_result": None,
                "should_continue": True,
                "errors": {},
            }

            # Track previous state to detect changes
            prev_state = {}

            logger.info("🚀 Starting workflow stream...")

            # Stream through the workflow (async) with multiple modes
            # Use both "values" (state updates) and "custom" (progress events)
            async for mode_data in self.system.app.astream(inputs, stream_mode=["values", "custom"]):
                # Handle different stream modes
                if isinstance(mode_data, tuple):
                    mode, data = mode_data
                    if mode == "custom":
                        # Forward custom progress events to frontend
                        logger.debug(f"📤 Custom event: {data}")
                        event_type = None
                        if "agent_start" in data:
                            event_type = "agent_start"
                        elif "agent_progress" in data:
                            event_type = "agent_progress"

                        if event_type:
                            yield {
                                "type": event_type,
                                "data": data,
                            }
                        continue
                    elif mode == "values":
                        # This is a "values" mode update (state)
                        state = data
                    else:
                        continue
                else:
                    # Fallback: treat as state if not a tuple
                    state = mode_data
                step = state.get("step_count", 0)
                logger.debug(f"📊 Received state update - Step: {step}, Keys: {list(state.keys())}")

                # Query parsing completed
                if state.get("query_context") and not prev_state.get("query_context"):
                    logger.info(f"✅ Query parsed - Pair: {state.get('pair')}, Step: {step}")
                    event = {
                        "type": "query_parsed",
                        "data": {
                            "step": step,
                            "query_context": state["query_context"],
                            "pair": state.get("pair"),
                            "timestamp": self._get_timestamp()
                        }
                    }
                    logger.debug(f"📤 Yielding event: query_parsed")
                    yield event

                # News agent completed
                if state.get("news_result") and not prev_state.get("news_result"):
                    success = state["news_result"].get("success", False)
                    logger.info(f"📰 News agent completed - Success: {success}, Step: {step}")
                    if not success:
                        logger.warning(f"⚠️  News agent failed: {state['news_result'].get('error', 'Unknown error')}")
                    event = {
                        "type": "agent_update",
                        "data": {
                            "step": step,
                            "agent": "news",
                            "result": state["news_result"],
                            "timestamp": self._get_timestamp()
                        }
                    }
                    logger.debug(f"📤 Yielding event: agent_update (news)")
                    yield event

                # Technical agent completed
                if state.get("technical_result") and not prev_state.get("technical_result"):
                    success = state["technical_result"].get("success", False)
                    logger.info(f"📊 Technical agent completed - Success: {success}, Step: {step}")
                    if not success:
                        logger.warning(f"⚠️  Technical agent failed: {state['technical_result'].get('error', 'Unknown error')}")
                    event = {
                        "type": "agent_update",
                        "data": {
                            "step": step,
                            "agent": "technical",
                            "result": state["technical_result"],
                            "timestamp": self._get_timestamp()
                        }
                    }
                    logger.debug(f"📤 Yielding event: agent_update (technical)")
                    yield event

                # Fundamental agent completed
                if state.get("fundamental_result") and not prev_state.get("fundamental_result"):
                    success = state["fundamental_result"].get("success", False)
                    logger.info(f"💼 Fundamental agent completed - Success: {success}, Step: {step}")
                    if not success:
                        logger.warning(f"⚠️  Fundamental agent failed: {state['fundamental_result'].get('error', 'Unknown error')}")
                    event = {
                        "type": "agent_update",
                        "data": {
                            "step": step,
                            "agent": "fundamental",
                            "result": state["fundamental_result"],
                            "timestamp": self._get_timestamp()
                        }
                    }
                    logger.debug(f"📤 Yielding event: agent_update (fundamental)")
                    yield event

                # Risk assessment completed
                if state.get("risk_result") and not prev_state.get("risk_result"):
                    risk_data = state["risk_result"]
                    approved = risk_data.get("data", {}).get("trade_approved", False)
                    logger.info(f"⚖️  Risk assessment completed - Approved: {approved}, Step: {step}")
                    if not approved:
                        reason = risk_data.get("data", {}).get("rejection_reason", "Unknown reason")
                        logger.warning(f"⚠️  Trade rejected: {reason}")
                    event = {
                        "type": "risk_update",
                        "data": {
                            "step": step,
                            "risk_result": risk_data,
                            "trade_approved": approved,
                            "timestamp": self._get_timestamp()
                        }
                    }
                    logger.debug(f"📤 Yielding event: risk_update")
                    yield event

                # Decision made
                if state.get("decision") and not prev_state.get("decision"):
                    decision = state["decision"]
                    action = decision.get("action", "UNKNOWN")
                    confidence = decision.get("confidence", 0)
                    logger.info(f"🎯 Final decision made - Action: {action}, Confidence: {confidence:.2%}, Step: {step}")
                    event = {
                        "type": "decision",
                        "data": {
                            "step": step,
                            "decision": decision,
                            "timestamp": self._get_timestamp()
                        }
                    }
                    logger.debug(f"📤 Yielding event: decision")
                    yield event

                # Report generated
                if state.get("report_result") and not prev_state.get("report_result"):
                    report_result = state["report_result"]
                    success = report_result.get("success", False)
                    word_count = report_result.get("metadata", {}).get("word_count", 0)
                    logger.info(f"📄 Report generated - Success: {success}, Words: {word_count}, Step: {step}")
                    if not success:
                        logger.warning(f"⚠️  Report generation failed: {report_result.get('error', 'Unknown error')}")
                    event = {
                        "type": "report_update",
                        "data": {
                            "step": step,
                            "report_result": report_result,
                            "timestamp": self._get_timestamp()
                        }
                    }
                    logger.debug(f"📤 Yielding event: report_update")
                    yield event

                prev_state = state.copy()

            # Send completion event with full result
            logger.info("✅ Workflow completed successfully")
            final_result = self.system._format_result(prev_state)
            logger.debug(f"📦 Final result keys: {list(final_result.keys())}")
            complete_event = {
                "type": "complete",
                "data": {
                    "result": final_result,
                    "timestamp": self._get_timestamp()
                }
            }
            logger.debug(f"📤 Yielding event: complete")
            yield complete_event
            logger.info("🏁 Streaming completed")

        except Exception as e:
            log_error(logger, e, "streaming analysis")
            logger.error(f"❌ Streaming failed at step {inputs.get('step_count', 0)}")

            # Send error event
            error_event = {
                "type": "error",
                "data": {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": self._get_timestamp()
                }
            }
            logger.debug(f"📤 Yielding event: error")
            yield error_event

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

    def get_info(self) -> Dict[str, Any]:
        """Get system information."""
        return self.system.get_info()
