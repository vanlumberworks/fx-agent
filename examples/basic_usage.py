"""Basic usage examples for Forex Agent System."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from system import ForexAgentSystem


def example_1_basic_analysis():
    """Example 1: Basic analysis of a currency pair."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic EUR/USD Analysis")
    print("=" * 60)

    # Initialize system
    system = ForexAgentSystem()

    # Analyze EUR/USD
    result = system.analyze("EUR/USD")

    # Access decision
    decision = result["decision"]
    print(f"\nFinal Decision: {decision['action']}")
    print(f"Confidence: {decision['confidence']:.0%}")


def example_2_multiple_pairs():
    """Example 2: Analyze multiple currency pairs."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Multiple Currency Pairs")
    print("=" * 60)

    pairs = ["EUR/USD", "GBP/USD", "USD/JPY"]

    system = ForexAgentSystem()

    results = {}
    for pair in pairs:
        print(f"\nAnalyzing {pair}...")
        result = system.analyze(pair, verbose=False)
        results[pair] = result["decision"]

    # Compare results
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    for pair, decision in results.items():
        action = decision.get("action", "UNKNOWN")
        confidence = decision.get("confidence", 0.0)
        print(f"{pair}: {action} ({confidence:.0%})")


def example_3_custom_settings():
    """Example 3: Custom account settings."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Custom Account Settings")
    print("=" * 60)

    # Initialize with custom settings
    system = ForexAgentSystem(account_balance=50000.0, max_risk_per_trade=0.01)  # $50k account  # 1% risk per trade

    result = system.analyze("EUR/USD")

    # Check risk parameters
    risk_data = result["agent_results"]["risk"]["data"]
    print(f"\nRisk Parameters:")
    print(f"  Account Balance: ${risk_data['account_balance']:,.2f}")
    print(f"  Max Risk: {risk_data['risk_percentage']}%")
    print(f"  Dollar Risk: ${risk_data['dollar_risk']:.2f}")
    print(f"  Position Size: {risk_data['position_size']:.2f} lots")


def example_4_access_agent_data():
    """Example 4: Access individual agent results."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Access Agent Data")
    print("=" * 60)

    system = ForexAgentSystem()
    result = system.analyze("EUR/USD", verbose=False)

    # Access news data
    news_data = result["agent_results"]["news"]["data"]
    print(f"\nNews Sentiment: {news_data['sentiment']}")
    print(f"Impact: {news_data['impact']}")

    # Access technical data
    tech_data = result["agent_results"]["technical"]["data"]
    print(f"\nTechnical Analysis:")
    print(f"  Current Price: {tech_data['current_price']}")
    print(f"  Trend: {tech_data['trend']}")
    print(f"  RSI: {tech_data['indicators']['rsi']}")

    # Access fundamental data
    fund_data = result["agent_results"]["fundamental"]["data"]
    print(f"\nFundamental Outlook: {fund_data['outlook']}")

    # Access web sources
    grounding = result["decision"].get("grounding_metadata", {})
    sources = grounding.get("sources", [])
    print(f"\nWeb Sources: {len(sources)} sources used")


def example_5_system_info():
    """Example 5: Get system information."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: System Information")
    print("=" * 60)

    system = ForexAgentSystem()
    info = system.get_info()

    print("\nSystem Configuration:")
    print(f"  Account Balance: ${info['system']['account_balance']:,.2f}")
    print(f"  Max Risk: {info['system']['max_risk_per_trade']*100}%")
    print(f"  API Configured: {info['system']['api_configured']}")

    print("\nWorkflow Information:")
    print(f"  Nodes: {info['workflow']['num_nodes']}")
    print(f"  Edges: {info['workflow']['num_edges']}")
    print(f"  Node List: {', '.join(info['workflow']['nodes'])}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("FOREX AGENT SYSTEM - EXAMPLES")
    print("=" * 70)

    try:
        example_1_basic_analysis()
        example_2_multiple_pairs()
        example_3_custom_settings()
        example_4_access_agent_data()
        example_5_system_info()

        print("\n" + "=" * 70)
        print("✅ All examples completed successfully!")
        print("=" * 70)

    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure GOOGLE_AI_API_KEY is set in .env file")
        print("Get your key from: https://aistudio.google.com/app/apikey")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
