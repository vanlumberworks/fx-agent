"""Test async News Agent with Google Search."""

import asyncio
import os
from agents.news_agent import NewsAgent


async def test_news_agent():
    """Test News Agent with various currency pairs."""
    print("=" * 70)
    print("TESTING ASYNC NEWS AGENT WITH GOOGLE SEARCH")
    print("=" * 70)

    # Check API key
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        print("\n❌ GOOGLE_AI_API_KEY not found in environment")
        print("Please set it in .env file")
        return 1

    agent = NewsAgent()

    # Test pairs
    pairs = [
        "EUR/USD",
        "XAU/USD",  # Gold
        "BTC/USD",  # Bitcoin
    ]

    print(f"\nTesting {len(pairs)} currency pairs...\n")

    for pair in pairs:
        print(f"\n{'='*70}")
        print(f"Testing: {pair}")
        print(f"{'='*70}\n")

        try:
            result = await agent.analyze(pair)

            if result["success"]:
                data = result["data"]

                print(f"✅ Success!")
                print(f"\nSentiment: {data['sentiment']} ({data['sentiment_score']:.2f})")
                print(f"Impact: {data['impact']}")
                print(f"News Count: {data['news_count']}")
                print(f"Data Source: {data['data_source']}")

                # Show headlines
                print(f"\nHeadlines:")
                for i, headline in enumerate(data["headlines"][:3], 1):
                    print(f"\n{i}. {headline.get('title', 'No title')}")
                    print(f"   Date: {headline.get('date', 'N/A')}")
                    print(f"   Sentiment: {headline.get('sentiment', 'N/A')}")
                    if "source" in headline:
                        print(f"   Source: {headline.get('source')}")

                # Show key events
                if data.get("key_events"):
                    print(f"\nKey Events:")
                    for event in data["key_events"]:
                        print(f"  • {event}")

                # Show summary
                print(f"\nSummary:")
                print(f"  {data['summary']}")

                # Show search queries used
                if data.get("search_queries"):
                    print(f"\nGoogle Search Queries Used:")
                    for query in data["search_queries"][:3]:
                        print(f"  • {query}")

                # Show sources
                if data.get("sources"):
                    print(f"\nSources ({len(data['sources'])} total):")
                    for i, source in enumerate(data["sources"][:3], 1):
                        print(f"  {i}. {source.get('title', 'No title')}")
                        print(f"     {source.get('url', 'No URL')}")

            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            import traceback

            traceback.print_exc()

    print(f"\n{'='*70}")
    print("✅ TESTING COMPLETE")
    print(f"{'='*70}\n")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(asyncio.run(test_news_agent()))
