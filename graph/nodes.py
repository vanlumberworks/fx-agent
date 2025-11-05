"""LangGraph node functions for forex agent system."""

import json
import os
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from graph.state import ForexAgentState
from agents import NewsAgent, TechnicalAgent, FundamentalAgent, RiskAgent


async def news_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Node: Analyze news for the currency pair using Google Search.

    Now async and powered by real Google Search!

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        State updates
    """
    pair = state["pair"]
    print(f"📰 News Agent analyzing {pair} with Google Search...")

    try:
        agent = NewsAgent()
        result = await agent.analyze(pair)

        return {
            "news_result": result,
            "step_count": state.get("step_count", 0) + 1,
        }
    except Exception as e:
        return {
            "news_result": {"success": False, "error": str(e)},
            "step_count": state.get("step_count", 0) + 1,
            "errors": {**state.get("errors", {}), "news": str(e)},
        }


async def technical_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Node: Perform technical analysis.

    Now async for parallel execution.

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        State updates
    """
    pair = state["pair"]
    print(f"📊 Technical Agent analyzing {pair}...")

    try:
        agent = TechnicalAgent()
        result = agent.analyze(pair)

        return {
            "technical_result": result,
            "step_count": state["step_count"] + 1,
        }
    except Exception as e:
        return {
            "technical_result": {"success": False, "error": str(e)},
            "step_count": state["step_count"] + 1,
            "errors": {**state.get("errors", {}), "technical": str(e)},
        }


async def fundamental_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Node: Analyze fundamental data.

    Now async for parallel execution.

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        State updates
    """
    pair = state["pair"]
    print(f"💰 Fundamental Agent analyzing {pair}...")

    try:
        agent = FundamentalAgent()
        result = agent.analyze(pair)

        return {
            "fundamental_result": result,
            "step_count": state["step_count"] + 1,
        }
    except Exception as e:
        return {
            "fundamental_result": {"success": False, "error": str(e)},
            "step_count": state["step_count"] + 1,
            "errors": {**state.get("errors", {}), "fundamental": str(e)},
        }


def risk_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Node: Calculate risk parameters.

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        State updates
    """
    pair = state["pair"]
    print(f"⚖️  Risk Agent calculating parameters...")

    try:
        # Get technical analysis results for entry/stop prices
        ta_result = state.get("technical_result", {})
        if not ta_result.get("success"):
            raise ValueError("Technical analysis failed, cannot calculate risk")

        ta_data = ta_result["data"]
        current_price = ta_data["current_price"]
        stop_loss = ta_data["stop_loss"]

        # Determine direction from technical signals
        signals = ta_data["signals"]
        direction = "BUY" if signals["overall"] == "BUY" else "SELL"

        # Get take profit
        take_profit = ta_data.get("take_profit")

        # Get account settings from environment or use defaults
        account_balance = float(os.getenv("ACCOUNT_BALANCE", "10000.0"))
        max_risk = float(os.getenv("MAX_RISK_PER_TRADE", "0.02"))

        # Initialize risk agent
        agent = RiskAgent(account_balance=account_balance, max_risk_per_trade=max_risk)

        # Analyze risk
        result = agent.analyze(
            pair=pair, entry_price=current_price, stop_loss=stop_loss, direction=direction, take_profit=take_profit, leverage=1.0
        )

        return {
            "risk_result": result,
            "step_count": state["step_count"] + 1,
        }
    except Exception as e:
        return {
            "risk_result": {"success": False, "error": str(e)},
            "step_count": state["step_count"] + 1,
            "errors": {**state.get("errors", {}), "risk": str(e)},
        }


def synthesis_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Node: Synthesize all agent outputs using Gemini with Google Search grounding.

    This is the critical node where:
    1. All agent outputs are collected
    2. Gemini LLM synthesizes the information
    3. Google Search provides real-time verification
    4. Final trading decision is made with citations

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        State updates with final decision
    """
    pair = state["pair"]
    print(f"🤖 Synthesis Agent making final decision with Google Search...")

    try:
        from google import genai
        from google.genai import types

        # Initialize Gemini client
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_AI_API_KEY not found in environment")

        client = genai.Client(api_key=api_key)

        # Build comprehensive prompt
        prompt = _build_synthesis_prompt(state)

        # Configure Google Search grounding
        grounding_tool = types.Tool(google_search=types.GoogleSearch())

        config_gemini = types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json",
            tools=[grounding_tool],
            thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disable thinking for speed
        )

        # Generate decision with Google Search
        response = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt], config=config_gemini)

        # Parse decision
        decision = json.loads(response.text)

        # Add grounding metadata (citations)
        if response.candidates[0].grounding_metadata:
            metadata = response.candidates[0].grounding_metadata
            decision["grounding_metadata"] = {
                "search_queries": metadata.web_search_queries or [],
                "sources": (
                    [{"title": c.web.title, "url": c.web.uri} for c in metadata.grounding_chunks] if metadata.grounding_chunks else []
                ),
            }

        print(f"✅ Final decision: {decision.get('action', 'UNKNOWN')}")

        return {
            "decision": decision,
            "step_count": state["step_count"] + 1,
        }

    except Exception as e:
        print(f"❌ Synthesis failed: {str(e)}")
        # Fallback decision
        return {
            "decision": {
                "action": "WAIT",
                "confidence": 0.0,
                "reasoning": {"summary": f"Synthesis failed: {str(e)}", "error": True},
            },
            "step_count": state["step_count"] + 1,
            "errors": {**state.get("errors", {}), "synthesis": str(e)},
        }


def _build_synthesis_prompt(state: ForexAgentState) -> str:
    """Build the synthesis prompt for Gemini."""
    pair = state["pair"]

    # Extract agent results
    news_data = state.get("news_result", {}).get("data", {})
    tech_data = state.get("technical_result", {}).get("data", {})
    fund_data = state.get("fundamental_result", {}).get("data", {})
    risk_data = state.get("risk_result", {}).get("data", {})

    prompt = f"""You are an expert forex trading synthesizer with real-time market access via Google Search.

CURRENCY PAIR: {pair}

AGENT ANALYSIS (Local Mock Data - Please verify with real-time web search):

📰 NEWS AGENT:
{json.dumps(news_data, indent=2)}

📊 TECHNICAL AGENT:
{json.dumps(tech_data, indent=2)}

💰 FUNDAMENTAL AGENT:
{json.dumps(fund_data, indent=2)}

⚖️  RISK AGENT:
{json.dumps(risk_data, indent=2)}

TASK:
1. Use Google Search to get REAL-TIME {pair} market data, news, and analysis
2. Verify the mock agent analysis against current web sources
3. Synthesize all information into a final trading decision
4. Provide clear reasoning with source citations

CRITICAL RULES:
- If Risk Agent rejected trade (trade_approved=false) → MUST output action: "WAIT"
- Prioritize real-time web data over mock agent data
- Consider all three dimensions: news sentiment, technical signals, fundamentals
- Only recommend BUY/SELL if confidence is high (>0.7) and risk is approved
- Cite specific sources for key claims

OUTPUT FORMAT (JSON):
{{
  "action": "BUY|SELL|WAIT",
  "confidence": 0.0-1.0,
  "reasoning": {{
    "summary": "One paragraph summary of the decision",
    "web_verification": "What real-time data confirmed or contradicted the mock analysis",
    "key_factors": ["factor1", "factor2", "factor3"],
    "risks": ["risk1", "risk2"]
  }},
  "trade_parameters": {{
    "entry_price": {tech_data.get('current_price', 0)},
    "stop_loss": {tech_data.get('stop_loss', 0)},
    "take_profit": {tech_data.get('take_profit', 0)},
    "position_size": {risk_data.get('position_size', 0)}
  }}
}}

Remember: Be conservative. When in doubt, output "WAIT".
"""

    return prompt


# Conditional edge functions
def should_continue_after_risk(state: ForexAgentState) -> str:
    """
    Determine if we should continue to synthesis after risk analysis.

    If risk agent rejected the trade, we skip synthesis and end.
    """
    risk_result = state.get("risk_result", {})

    if not risk_result.get("success", False):
        print("⚠️  Risk analysis failed, ending workflow")
        return "end"

    risk_data = risk_result.get("data", {})
    if not risk_data.get("trade_approved", False):
        print(f"🛑 Trade rejected by Risk Agent: {risk_data.get('rejection_reason')}")
        return "end"

    print("✅ Risk approved, proceeding to synthesis")
    return "continue"


def route_after_synthesis(state: ForexAgentState) -> str:
    """
    Route after synthesis node.

    Could add additional verification or human-in-the-loop here.
    """
    decision = state.get("decision", {})
    action = decision.get("action", "WAIT")

    print(f"🎯 Routing after synthesis: {action}")
    return "end"
