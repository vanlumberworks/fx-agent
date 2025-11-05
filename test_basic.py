"""Basic tests to validate the system without requiring API key."""

import sys


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from agents import NewsAgent, TechnicalAgent, FundamentalAgent, RiskAgent

        print("  ✅ Agents import successfully")
    except ImportError as e:
        print(f"  ❌ Agent import failed: {e}")
        return False

    try:
        from graph.state import ForexAgentState

        print("  ✅ State definition imports successfully")
    except ImportError as e:
        print(f"  ❌ State import failed: {e}")
        return False

    try:
        from graph.nodes import news_node, technical_node, fundamental_node, risk_node, synthesis_node

        print("  ✅ Node functions import successfully")
    except ImportError as e:
        print(f"  ❌ Node import failed: {e}")
        return False

    try:
        from graph.workflow import build_forex_workflow

        print("  ✅ Workflow builder imports successfully")
    except ImportError as e:
        print(f"  ❌ Workflow import failed: {e}")
        return False

    return True


def test_agents():
    """Test that agents work with mock data."""
    print("\nTesting agents...")

    from agents import NewsAgent, TechnicalAgent, FundamentalAgent, RiskAgent

    # Test News Agent
    try:
        agent = NewsAgent()
        result = agent.analyze("EUR/USD")
        assert result["success"] == True
        assert "sentiment" in result["data"]
        print("  ✅ News Agent works")
    except Exception as e:
        print(f"  ❌ News Agent failed: {e}")
        return False

    # Test Technical Agent
    try:
        agent = TechnicalAgent()
        result = agent.analyze("EUR/USD")
        assert result["success"] == True
        assert "trend" in result["data"]
        print("  ✅ Technical Agent works")
    except Exception as e:
        print(f"  ❌ Technical Agent failed: {e}")
        return False

    # Test Fundamental Agent
    try:
        agent = FundamentalAgent()
        result = agent.analyze("EUR/USD")
        assert result["success"] == True
        assert "outlook" in result["data"]
        print("  ✅ Fundamental Agent works")
    except Exception as e:
        print(f"  ❌ Fundamental Agent failed: {e}")
        return False

    # Test Risk Agent
    try:
        agent = RiskAgent(account_balance=10000, max_risk_per_trade=0.02)
        result = agent.analyze(pair="EUR/USD", entry_price=1.0850, stop_loss=1.0800, direction="BUY", take_profit=1.0950)

        assert result["success"] == True
        assert "trade_approved" in result["data"]
        print("  ✅ Risk Agent works")
    except Exception as e:
        print(f"  ❌ Risk Agent failed: {e}")
        return False

    return True


def test_workflow_build():
    """Test that workflow can be built (without running)."""
    print("\nTesting workflow build...")

    try:
        from graph.workflow import build_forex_workflow

        app = build_forex_workflow()
        print("  ✅ Workflow builds successfully")
        return True
    except Exception as e:
        print(f"  ❌ Workflow build failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("BASIC VALIDATION TESTS")
    print("=" * 60)

    tests = [test_imports, test_agents, test_workflow_build]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test crashed: {e}")
            import traceback

            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nNext step: Set up your .env file with GOOGLE_AI_API_KEY")
        print("Then run: python main.py EUR/USD")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
