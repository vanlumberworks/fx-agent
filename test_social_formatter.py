"""
Tests for Social Media Formatter

Validates formatting logic for Twitter, Telegram, and Facebook posts.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from utils.social_formatter import (
    format_for_twitter,
    format_for_telegram,
    format_for_facebook,
    format_all_platforms,
    is_trading_signal
)


def test_twitter_trading_signal():
    """Test Twitter formatting for trading signals."""
    print("\n" + "=" * 80)
    print("TEST 1: Twitter - Trading Signal")
    print("=" * 80)

    result = {
        'pair': 'EUR/USD',
        'decision': {
            'action': 'BUY',
            'confidence': 0.85,
            'reasoning': {
                'summary': 'Strong bullish momentum with ECB rate hike expectations.'
            },
            'trade_parameters': {
                'entry_price': 1.0850,
                'stop_loss': 1.0800,
                'take_profit': 1.0950
            }
        }
    }

    post = format_for_twitter(result, include_trade_params=True)

    print(post)
    print(f"\n✅ Length: {len(post)} chars")

    # Assertions
    assert len(post) <= 280, f"❌ Post exceeds 280 chars: {len(post)}"
    assert '🟢' in post, "❌ Missing BUY emoji"
    assert 'EUR/USD' in post, "❌ Missing pair"
    assert ('1.0850' in post or '1.085' in post), "❌ Missing entry price"
    assert 'NFA' in post or 'Not financial advice' in post.lower(), "❌ Missing disclaimer"
    assert '#' in post, "❌ Missing hashtags"

    print("✅ All assertions passed!\n")


def test_twitter_sell_signal():
    """Test Twitter formatting for SELL signals."""
    print("=" * 80)
    print("TEST 2: Twitter - SELL Signal")
    print("=" * 80)

    result = {
        'pair': 'GBP/USD',
        'decision': {
            'action': 'SELL',
            'confidence': 0.78,
            'reasoning': {
                'summary': 'GBP weakening on BOE dovish stance.'
            },
            'trade_parameters': {
                'entry_price': 1.2650,
                'stop_loss': 1.2700,
                'take_profit': 1.2550
            }
        }
    }

    post = format_for_twitter(result)

    print(post)
    print(f"\n✅ Length: {len(post)} chars")

    assert len(post) <= 280, f"❌ Post exceeds 280 chars"
    assert '🔴' in post, "❌ Missing SELL emoji"
    assert 'SELL' in post, "❌ Missing SELL keyword"

    print("✅ All assertions passed!\n")


def test_twitter_informational():
    """Test Twitter formatting for informational posts."""
    print("=" * 80)
    print("TEST 3: Twitter - Informational Post")
    print("=" * 80)

    result = {
        'pair': 'XAU/USD',
        'decision': {
            'action': 'WAIT',
            'confidence': 0.5,
            'reasoning': {
                'summary': 'Gold consolidating near key support. Awaiting Fed decision before taking position.'
            }
        }
    }

    post = format_for_twitter(result, include_trade_params=False)

    print(post)
    print(f"\n✅ Length: {len(post)} chars")

    assert len(post) <= 280, f"❌ Post exceeds 280 chars"
    assert 'XAU/USD' in post, "❌ Missing pair"
    assert '1.0850' not in post, "❌ Should not include trade params"

    print("✅ All assertions passed!\n")


def test_telegram_trading_signal():
    """Test Telegram formatting with markdown."""
    print("=" * 80)
    print("TEST 4: Telegram - Trading Signal")
    print("=" * 80)

    result = {
        'pair': 'EUR/USD',
        'decision': 'BUY',
        'entry_price': 1.0850,
        'stop_loss': 1.0800,
        'target_price': 1.0950,
        'risk_reward_ratio': 2.0,
        'confidence': 'High',
        'reasoning': 'Strong bullish momentum with ECB rate hike expectations. Technical breakout confirmed.',
        'citations': [
            {'title': 'ECB Policy Update', 'url': 'https://example.com/ecb'},
            {'title': 'EUR Technical Analysis', 'url': 'https://example.com/tech'}
        ]
    }

    post = format_for_telegram(result, channel_name="FX Signals Pro")

    print(post)

    # Assertions
    assert '**' in post, "❌ Missing markdown bold"
    assert 'Entry:' in post, "❌ Missing entry price"
    assert 'Target:' in post, "❌ Missing target"
    assert 'Stop Loss:' in post, "❌ Missing stop loss"
    assert 'Risk/Reward:' in post, "❌ Missing risk/reward"
    assert 'Disclaimer' in post, "❌ Missing disclaimer"
    assert 'FX Signals Pro' in post, "❌ Missing channel name"
    assert '[ECB Policy Update]' in post, "❌ Missing citations"

    print("✅ All assertions passed!\n")


def test_telegram_no_citations():
    """Test Telegram formatting without citations."""
    print("=" * 80)
    print("TEST 5: Telegram - No Citations")
    print("=" * 80)

    result = {
        'pair': 'BTC/USD',
        'decision': 'SELL',
        'entry_price': 45000,
        'stop_loss': 46000,
        'target_price': 43000,
        'reasoning': 'Bitcoin showing weakness at resistance.'
    }

    post = format_for_telegram(result)

    print(post)

    assert 'Sources:' not in post or '**Sources:**\n\n' in post, "❌ Unexpected citations section"
    assert 'Disclaimer' in post, "❌ Missing disclaimer"

    print("✅ All assertions passed!\n")


def test_facebook_trading_signal():
    """Test Facebook formatting with educational context."""
    print("=" * 80)
    print("TEST 6: Facebook - Trading Signal")
    print("=" * 80)

    result = {
        'pair': 'EUR/USD',
        'decision': 'BUY',
        'entry_price': 1.0850,
        'stop_loss': 1.0800,
        'target_price': 1.0950,
        'risk_reward_ratio': 2.0,
        'reasoning': 'Strong bullish momentum with ECB rate hike expectations.'
    }

    post = format_for_facebook(result, educational_context=True)

    print(post)

    # Assertions
    assert 'Trade Setup:' in post or 'Trade Parameters:' in post, "❌ Missing trade setup"
    assert 'Entry Level:' in post or 'Entry:' in post, "❌ Missing entry"
    assert 'What does this mean?' in post, "❌ Missing educational context"
    assert 'DISCLAIMER' in post.upper(), "❌ Missing disclaimer"
    assert 'financial advice' in post.lower(), "❌ Missing financial advice disclaimer"
    assert '#' in post, "❌ Missing hashtags"

    print("✅ All assertions passed!\n")


def test_facebook_informational():
    """Test Facebook informational post."""
    print("=" * 80)
    print("TEST 7: Facebook - Informational")
    print("=" * 80)

    result = {
        'pair': 'XAU/USD',
        'decision': 'WAIT',
        'reasoning': 'Gold consolidating near key support. Mixed signals from Fed policy and inflation data.'
    }

    post = format_for_facebook(result, include_trade_params=False)

    print(post)

    assert 'Entry Level:' not in post, "❌ Should not include trade params"
    assert 'What does this mean?' in post, "❌ Missing educational context"

    print("✅ All assertions passed!\n")


def test_format_all_platforms():
    """Test generating all platforms at once."""
    print("=" * 80)
    print("TEST 8: Format All Platforms")
    print("=" * 80)

    result = {
        'pair': 'GBP/JPY',
        'decision': 'SELL',
        'entry_price': 185.50,
        'stop_loss': 186.00,
        'target_price': 184.50,
        'reasoning': 'GBP/JPY showing bearish reversal pattern.'
    }

    posts = format_all_platforms(result)

    print("Twitter:")
    print("-" * 40)
    print(posts['twitter'])
    print()

    print("Telegram:")
    print("-" * 40)
    print(posts['telegram'][:200] + "...")  # Truncate for brevity
    print()

    print("Facebook:")
    print("-" * 40)
    print(posts['facebook'][:200] + "...")  # Truncate for brevity
    print()

    # Assertions
    assert 'twitter' in posts, "❌ Missing Twitter post"
    assert 'telegram' in posts, "❌ Missing Telegram post"
    assert 'facebook' in posts, "❌ Missing Facebook post"
    assert len(posts['twitter']) <= 280, "❌ Twitter post too long"
    assert 'GBP/JPY' in posts['twitter'], "❌ Missing pair in Twitter"
    assert 'GBP/JPY' in posts['telegram'], "❌ Missing pair in Telegram"
    assert 'GBP/JPY' in posts['facebook'], "❌ Missing pair in Facebook"

    print("✅ All assertions passed!\n")


def test_is_trading_signal():
    """Test trading signal detection."""
    print("=" * 80)
    print("TEST 9: Trading Signal Detection")
    print("=" * 80)

    # Valid signal
    signal = {
        'decision': 'BUY',
        'entry_price': 1.0850,
        'stop_loss': 1.0800,
        'target_price': 1.0950
    }
    assert is_trading_signal(signal) == True, "❌ Should be trading signal"
    print("✅ Valid BUY signal detected")

    # WAIT decision (not a signal)
    wait = {
        'decision': 'WAIT',
        'entry_price': 1.0850,
        'stop_loss': 1.0800,
        'target_price': 1.0950
    }
    assert is_trading_signal(wait) == False, "❌ WAIT should not be a signal"
    print("✅ WAIT correctly identified as not a signal")

    # Missing parameters (not a signal)
    incomplete = {
        'decision': 'BUY',
        'entry_price': 1.0850
    }
    assert is_trading_signal(incomplete) == False, "❌ Incomplete data should not be signal"
    print("✅ Incomplete data correctly rejected")

    print("\n✅ All signal detection tests passed!\n")


def test_custom_options():
    """Test custom formatting options."""
    print("=" * 80)
    print("TEST 10: Custom Options")
    print("=" * 80)

    result = {
        'pair': 'BTC/USD',
        'decision': 'BUY',
        'entry_price': 45000,
        'stop_loss': 44000,
        'target_price': 47000,
        'reasoning': 'Bitcoin breakout above resistance.'
    }

    # Custom Twitter hashtags
    twitter_post = format_for_twitter(
        result,
        custom_hashtags=["#Bitcoin", "#BTC", "#Crypto", "#HODL"]
    )
    print("Twitter with custom hashtags:")
    print(twitter_post)
    assert '#Bitcoin' in twitter_post, "❌ Missing custom hashtag"
    assert '#HODL' in twitter_post, "❌ Missing custom hashtag"
    print("✅ Custom hashtags applied\n")

    # Custom Telegram channel
    telegram_post = format_for_telegram(
        result,
        channel_name="Crypto Whale Signals"
    )
    print("Telegram with custom channel:")
    print(telegram_post[:150] + "...")
    assert 'Crypto Whale Signals' in telegram_post, "❌ Missing custom channel name"
    print("✅ Custom channel name applied\n")

    print("✅ All custom options tests passed!\n")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("🧪 SOCIAL FORMATTER TEST SUITE")
    print("=" * 80)

    try:
        test_twitter_trading_signal()
        test_twitter_sell_signal()
        test_twitter_informational()
        test_telegram_trading_signal()
        test_telegram_no_citations()
        test_facebook_trading_signal()
        test_facebook_informational()
        test_format_all_platforms()
        test_is_trading_signal()
        test_custom_options()

        print("=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\n📊 Summary:")
        print("   • Twitter formatting: ✅")
        print("   • Telegram formatting: ✅")
        print("   • Facebook formatting: ✅")
        print("   • Signal detection: ✅")
        print("   • Custom options: ✅")
        print()

    except AssertionError as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED!")
        print("=" * 80)
        print(f"Error: {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()
