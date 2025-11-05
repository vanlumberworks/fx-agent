"""Test historical price data integration."""

from agents.price_service import get_price_service


def test_enriched_price():
    """Test enriched price data with historical context."""
    print("=" * 70)
    print("TESTING ENRICHED PRICE DATA (Current + Historical + OHLC)")
    print("=" * 70)

    price_service = get_price_service()

    # Test forex pair with full historical data
    pair = "EUR/USD"
    print(f"\n📊 Fetching enriched price for {pair}...\n")

    enriched = price_service.get_enriched_price(pair)

    if enriched:
        print(f"✅ Success!\n")
        print(f"Pair: {enriched['pair']}")
        print(f"Current Price: ${enriched['price']}")
        print(f"Bid/Ask: ${enriched['bid']} / ${enriched['ask']}")
        print(f"Source: {enriched['source']}")
        print(f"Timestamp: {enriched['timestamp']}")

        # Historical context
        if "historical" in enriched and enriched["historical"]:
            print(f"\n📈 Historical Context:")
            hist = enriched["historical"]
            print(f"  Yesterday's Rate: ${hist['yesterday_rate']}")
            print(f"  24h Change: ${hist['price_change']} ({hist['price_change_pct']:+.2f}%)")

        # OHLC data
        if "ohlc" in enriched and enriched["ohlc"]:
            print(f"\n📊 Yesterday's OHLC:")
            ohlc = enriched["ohlc"]
            print(f"  Open:  ${ohlc['open']}")
            print(f"  High:  ${ohlc['high']}")
            print(f"  Low:   ${ohlc['low']}")
            print(f"  Close: ${ohlc['close']}")

        # Calculate trading range
        if "ohlc" in enriched and enriched["ohlc"]:
            ohlc = enriched["ohlc"]
            range_pct = ((ohlc["high"] - ohlc["low"]) / ohlc["low"]) * 100
            print(f"\n  Yesterday's Range: {range_pct:.2f}%")

    else:
        print(f"❌ Failed to fetch enriched price for {pair}")

    print("\n" + "=" * 70)


def test_historical_rates():
    """Test historical rates endpoint."""
    print("\n📅 TESTING HISTORICAL RATES")
    print("=" * 70)

    price_service = get_price_service()

    pair = "GBP/USD"
    print(f"\nFetching yesterday's rate for {pair}...\n")

    historical = price_service.get_historical_rates(pair, "yesterday")

    if historical:
        print(f"✅ Success!")
        print(f"  Pair: {historical['pair']}")
        print(f"  Rate: ${historical['rate']}")
        print(f"  Date: {historical['date']}")
        print(f"  Source: {historical['source']}")
    else:
        print(f"❌ Failed")

    print("\n" + "=" * 70)


def test_ohlc():
    """Test OHLC endpoint."""
    print("\n📊 TESTING OHLC DATA")
    print("=" * 70)

    price_service = get_price_service()

    pair = "USD/JPY"
    print(f"\nFetching yesterday's OHLC for {pair}...\n")

    ohlc = price_service.get_ohlc(pair, "yesterday")

    if ohlc:
        print(f"✅ Success!")
        print(f"  Pair: {ohlc['pair']}")
        print(f"  Open:  ${ohlc['open']}")
        print(f"  High:  ${ohlc['high']}")
        print(f"  Low:   ${ohlc['low']}")
        print(f"  Close: ${ohlc['close']}")
        print(f"  Date: {ohlc['date']}")

        # Calculate metrics
        range_val = ohlc["high"] - ohlc["low"]
        range_pct = (range_val / ohlc["low"]) * 100
        body = abs(ohlc["close"] - ohlc["open"])
        body_pct = (body / ohlc["open"]) * 100

        print(f"\n  Range: {range_val:.5f} ({range_pct:.2f}%)")
        print(f"  Body: {body:.5f} ({body_pct:.2f}%)")

        if ohlc["close"] > ohlc["open"]:
            print(f"  Candle: 🟢 Bullish")
        elif ohlc["close"] < ohlc["open"]:
            print(f"  Candle: 🔴 Bearish")
        else:
            print(f"  Candle: ⚪ Doji")
    else:
        print(f"❌ Failed")

    print("\n" + "=" * 70)


def test_multiple_pairs():
    """Test enriched data for multiple pairs."""
    print("\n🌍 TESTING MULTIPLE PAIRS")
    print("=" * 70)

    price_service = get_price_service()

    pairs = ["EUR/USD", "GBP/USD", "USD/JPY"]

    print(f"\nFetching enriched data for {len(pairs)} pairs...\n")

    for pair in pairs:
        enriched = price_service.get_enriched_price(pair)

        if enriched:
            hist = enriched.get("historical", {})
            change_pct = hist.get("price_change_pct") if hist else None

            if change_pct is not None:
                direction = "📈" if change_pct > 0 else "📉"
                print(f"{direction} {pair}: ${enriched['price']} ({change_pct:+.2f}%)")
            else:
                print(f"   {pair}: ${enriched['price']}")
        else:
            print(f"❌ {pair}: Failed")

    print("\n" + "=" * 70)


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("HISTORICAL PRICE DATA INTEGRATION TEST")
    print("=" * 70)

    try:
        test_enriched_price()
        test_historical_rates()
        test_ohlc()
        test_multiple_pairs()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS COMPLETED!")
        print("=" * 70)

        print("\n💡 Key Features Demonstrated:")
        print("   ✓ Enriched price data (current + historical + OHLC)")
        print("   ✓ Historical rates endpoint")
        print("   ✓ OHLC (Open/High/Low/Close) data")
        print("   ✓ 24-hour price change calculation")
        print("   ✓ Trading range metrics")
        print("   ✓ Candlestick pattern identification")

        print("\n📊 APIs Used:")
        print("   • Forex Rate API - Latest prices")
        print("   • Forex Rate API - Historical rates")
        print("   • Forex Rate API - OHLC data")

        print("\n🎯 Next: This enriched data is now available to LLM agents for better analysis!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
