"""LangGraph workflow builder for forex trading system."""

from langgraph.graph import StateGraph, END
from graph.state import ForexAgentState
from graph.nodes import (
    news_node,
    technical_node,
    fundamental_node,
    risk_node,
    synthesis_node,
    should_continue_after_risk,
    route_after_synthesis,
)


def build_forex_workflow():
    """
    Build and compile the forex trading LangGraph workflow.

    Workflow:
    1. News analysis
    2. Technical analysis
    3. Fundamental analysis
    4. Risk assessment
    5. Conditional: If risk approved → Synthesis, else → End
    6. Synthesis with Gemini + Google Search
    7. End

    Returns:
        Compiled StateGraph application
    """
    # Create the state graph
    workflow = StateGraph(ForexAgentState)

    # Add nodes
    workflow.add_node("news", news_node)
    workflow.add_node("technical", technical_node)
    workflow.add_node("fundamental", fundamental_node)
    workflow.add_node("risk", risk_node)
    workflow.add_node("synthesis", synthesis_node)

    # Set entry point
    workflow.set_entry_point("news")

    # Define sequential flow through analysis agents
    workflow.add_edge("news", "technical")
    workflow.add_edge("technical", "fundamental")
    workflow.add_edge("fundamental", "risk")

    # Conditional edge after risk assessment
    # If risk approved, continue to synthesis
    # If risk rejected, end immediately
    workflow.add_conditional_edges(
        "risk",
        should_continue_after_risk,
        {
            "continue": "synthesis",
            "end": END,
        },
    )

    # After synthesis, always end
    # (Could add human-in-the-loop or verification here)
    workflow.add_conditional_edges(
        "synthesis",
        route_after_synthesis,
        {
            "end": END,
        },
    )

    # Compile the graph
    app = workflow.compile()

    return app


def visualize_workflow(app=None):
    """
    Visualize the workflow graph.

    Requires: ipython, matplotlib

    Args:
        app: Compiled workflow (if None, builds a new one)
    """
    if app is None:
        app = build_forex_workflow()

    try:
        from IPython.display import Image, display

        # Generate mermaid diagram
        png_data = app.get_graph().draw_mermaid_png()
        display(Image(png_data))
    except ImportError:
        print("Visualization requires IPython. Install with: pip install ipython")
        print("\nWorkflow structure:")
        print("  START")
        print("    ↓")
        print("  news_node")
        print("    ↓")
        print("  technical_node")
        print("    ↓")
        print("  fundamental_node")
        print("    ↓")
        print("  risk_node")
        print("    ↓")
        print("  [Risk Approved?]")
        print("    ↓ Yes          ↓ No")
        print("  synthesis_node   END")
        print("    ↓")
        print("  END")


def get_workflow_info(app=None):
    """
    Get information about the workflow.

    Args:
        app: Compiled workflow (if None, builds a new one)

    Returns:
        Dict with workflow information
    """
    if app is None:
        app = build_forex_workflow()

    # Get graph structure
    graph = app.get_graph()

    nodes = list(graph.nodes.keys())
    edges = [(e.source, e.target) for e in graph.edges]

    return {
        "nodes": nodes,
        "edges": edges,
        "num_nodes": len(nodes),
        "num_edges": len(edges),
    }
