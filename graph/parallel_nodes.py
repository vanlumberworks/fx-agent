"""Parallel execution node for running multiple agents simultaneously using asyncio."""

import asyncio
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from graph.state import ForexAgentState
from graph.nodes import news_node, technical_node, fundamental_node


async def parallel_analysis_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Execute News, Technical, and Fundamental agents in parallel using asyncio.

    This significantly speeds up the analysis by running all three agents
    concurrently instead of sequentially.

    Performance:
    - Sequential: ~3-6 seconds (1-2s per agent)
    - Parallel (async): ~1-2 seconds (max of all agents)
    - Speedup: ~3x faster

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        State updates with all three agent results
    """
    print(f"⚡ Running parallel analysis (News + Technical + Fundamental) with asyncio...")

    try:
        # Run all agents concurrently with asyncio.gather()
        results = await asyncio.gather(
            news_node(state, config),
            technical_node(state, config),
            fundamental_node(state, config),
            return_exceptions=True  # Don't fail entire operation if one agent fails
        )

        news_update, technical_update, fundamental_update = results

        # Handle exceptions from individual agents
        if isinstance(news_update, Exception):
            print(f"  ⚠️  News agent failed: {str(news_update)}")
            news_update = {
                "news_result": {"success": False, "error": str(news_update)},
                "step_count": state.get("step_count", 0) + 1,
                "errors": {"news": str(news_update)},
            }

        if isinstance(technical_update, Exception):
            print(f"  ⚠️  Technical agent failed: {str(technical_update)}")
            technical_update = {
                "technical_result": {"success": False, "error": str(technical_update)},
                "step_count": state.get("step_count", 0) + 1,
                "errors": {"technical": str(technical_update)},
            }

        if isinstance(fundamental_update, Exception):
            print(f"  ⚠️  Fundamental agent failed: {str(fundamental_update)}")
            fundamental_update = {
                "fundamental_result": {"success": False, "error": str(fundamental_update)},
                "step_count": state.get("step_count", 0) + 1,
                "errors": {"fundamental": str(fundamental_update)},
            }

        # Merge results
        # Note: step_count will be incremented by each agent,
        # so we take the max to avoid counting multiple times
        max_steps = max(
            news_update.get("step_count", 0) if isinstance(news_update, dict) else 0,
            technical_update.get("step_count", 0) if isinstance(technical_update, dict) else 0,
            fundamental_update.get("step_count", 0) if isinstance(fundamental_update, dict) else 0,
        )

        # Merge errors if any
        errors = {}
        if news_update.get("errors"):
            errors.update(news_update["errors"])
        if technical_update.get("errors"):
            errors.update(technical_update["errors"])
        if fundamental_update.get("errors"):
            errors.update(fundamental_update["errors"])

        print(f"  ✅ Parallel analysis complete")

        return {
            "news_result": news_update.get("news_result"),
            "technical_result": technical_update.get("technical_result"),
            "fundamental_result": fundamental_update.get("fundamental_result"),
            "step_count": max_steps,
            "errors": errors if errors else None,
        }

    except Exception as e:
        print(f"  ❌ Async parallel execution failed: {str(e)}")

        # Fall back to sequential execution
        print(f"  ⚠️  Falling back to sequential async execution...")

        try:
            news_update = await news_node(state, config)
            state_with_news = {**state, **news_update}

            technical_update = await technical_node(state_with_news, config)
            state_with_tech = {**state_with_news, **technical_update}

            fundamental_update = await fundamental_node(state_with_tech, config)

            return {
                "news_result": news_update.get("news_result"),
                "technical_result": technical_update.get("technical_result"),
                "fundamental_result": fundamental_update.get("fundamental_result"),
                "step_count": fundamental_update.get("step_count", 0),
                "errors": {**state.get("errors", {}), "parallel_execution": str(e)},
            }
        except Exception as sequential_error:
            print(f"  ❌ Sequential fallback also failed: {str(sequential_error)}")
            raise
