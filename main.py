"""Main entry point for Forex Agent System."""

import sys
from system import ForexAgentSystem


def main():
    """Run forex analysis on a currency pair."""
    # Default pair
    pair = "EUR/USD"

    # Check if pair provided as command line argument
    if len(sys.argv) > 1:
        pair = sys.argv[1].upper()
        # Ensure proper format
        if "/" not in pair:
            print(f"❌ Invalid pair format: {pair}")
            print("   Use format: EUR/USD or EURUSD")
            sys.exit(1)

    try:
        # Initialize system
        print("🚀 Initializing Forex Agent System...")
        system = ForexAgentSystem()

        # Run analysis
        result = system.analyze(pair)

        # Print detailed results
        print("\n" + "=" * 60)
        print("📊 DETAILED RESULTS")
        print("=" * 60)

        # Agent summaries
        print("\n📰 News Agent:")
        news = result["agent_results"]["news"]
        if news and news.get("success"):
            print(f"   {news['data'].get('summary', 'N/A')}")
        else:
            print(f"   ❌ Error: {news.get('error', 'Unknown error')}")

        print("\n📊 Technical Agent:")
        tech = result["agent_results"]["technical"]
        if tech and tech.get("success"):
            print(f"   {tech['data'].get('summary', 'N/A')}")
        else:
            print(f"   ❌ Error: {tech.get('error', 'Unknown error')}")

        print("\n💰 Fundamental Agent:")
        fund = result["agent_results"]["fundamental"]
        if fund and fund.get("success"):
            print(f"   {fund['data'].get('summary', 'N/A')}")
        else:
            print(f"   ❌ Error: {fund.get('error', 'Unknown error')}")

        print("\n⚖️  Risk Agent:")
        risk = result["agent_results"]["risk"]
        if risk and risk.get("success"):
            print(f"   {risk['data'].get('summary', 'N/A')}")
        else:
            print(f"   ❌ Error: {risk.get('error', 'Unknown error')}")

        print("\n" + "=" * 60)
        print("✅ Analysis complete!")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease set GOOGLE_AI_API_KEY in .env file")
        print("Get your key from: https://aistudio.google.com/app/apikey")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
