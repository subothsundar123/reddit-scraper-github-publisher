"""Create reproducible chart-market counts from the published signal corpus.

The script intentionally starts from every collected record and normalises themes
after inspection.  It does not pre-filter the source corpus by a short keyword
query, which avoids hiding emerging chart/workflow language.
"""

from __future__ import annotations

import gzip
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def get_text(row: dict) -> str:
    # Internal classifier tags are deliberately excluded: they can be assigned
    # generically and would turn a content count into a pipeline-tag count.
    # Long idea write-ups repeat the same terms; 2,500 characters preserves the
    # title and immediate explanation while keeping corpus-wide analysis fast.
    return " ".join((str(row.get("title", "")), str(row.get("body", ""))[:2200], str(row.get("description", ""))[:300])).casefold()


def identity(row: dict) -> str:
    return str(row.get("external_id") or row.get("url") or row.get("id") or row.get("title"))


def raw_engagement(data: dict | None) -> int:
    """Safely sum numeric values in heterogeneous engagement fields."""
    return sum(int(value) for value in (data or {}).values() if isinstance(value, (int, float)))


def load_rows(pattern: str) -> list[dict]:
    records: dict[str, dict] = {}
    for path in sorted(ROOT.glob(pattern)):
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            for line in stream:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                key = identity(row)
                # Keep one observation of a post/idea even if it appeared in a
                # later daily feed. Prefer the record with more interaction data.
                old = records.get(key)
                old_eng = raw_engagement((old or {}).get("engagement")) if old else -1
                new_eng = raw_engagement(row.get("engagement"))
                if old is None or new_eng >= old_eng:
                    records[key] = row
    return list(records.values())


def match_count(rows: list[dict], phrase: str) -> int:
    pat = re.compile(r"(?<!\w)" + re.escape(phrase.casefold()) + r"(?!\w)")
    return sum(bool(pat.search(get_text(row))) for row in rows)


def engagement(row: dict) -> int:
    data = row.get("engagement") or {}
    return sum(int(data.get(key) or 0) for key in ("score", "comments", "boosts", "likes", "view_count") if isinstance(data.get(key), (int, float)))


def count_near(rows: list[dict], phrase: str, words: tuple[str, ...]) -> int:
    phrase_re = re.escape(phrase.casefold())
    word_re = "|".join(re.escape(word) for word in words)
    # Windowed approach: a polarity word must occur within 120 characters,
    # avoiding a page-wide accidental match.
    pat = re.compile(rf"(?:{phrase_re}).{{0,120}}(?:{word_re})|(?:{word_re}).{{0,120}}(?:{phrase_re})", re.I | re.S)
    return sum(bool(pat.search(get_text(row))) for row in rows)


def main() -> None:
    tv_rows = load_rows("daily-dumps/*/tradingview_signals.jsonl.gz")
    all_rows = load_rows("daily-dumps/*/signals.jsonl.gz")
    combined = {identity(row): row for row in all_rows}
    combined.update({identity(row): row for row in tv_rows})
    all_unique = list(combined.values())
    # Text construction is the expensive operation. Build it once so every
    # normalised topic is evaluated consistently and quickly.
    indexed = [(row, get_text(row)) for row in all_unique]
    indexed_tv = [(row, get_text(row)) for row in tv_rows]
    # The non-TradingView corpus is broad. This is a deliberately wide
    # content-based inclusion pass for chart research, after which the report
    # normalises all discovered chart/workflow topics. It is not a search-query
    # filter and does not decide which pages are collected.
    chart_context = (
        "chart", "tradingview", "indicator", "technical analysis", "price action", "candlestick",
        "trendline", "support", "resistance", "moving average", "rsi", "macd", "vwap", "fibonacci",
        "open interest", "oi profile", "volume profile", "options chain", "greeks", "implied volatility",
        "stop loss", "target", "scalper", "backtest", "replay", "screener", "webhook", "alert",
        "dhan", "groww", "sahi",
    )
    chart_indexed = [(row, text) for row, text in indexed if row.get("source") == "tradingview" or any(term in text for term in chart_context)]

    daily_files = sorted(ROOT.glob("daily-dumps/*/tradingview_signals.jsonl.gz"))
    file_counts = []
    for path in daily_files:
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            rows = [json.loads(line) for line in stream if line.strip()]
        file_counts.append((path.parent.name, len(rows)))

    monthly = Counter()
    for day, count in file_counts:
        monthly[day[:7]] += count

    indicators = [
        "EMA", "SMA", "RSI", "Fibonacci", "MACD", "VWAP", "Bollinger Bands", "ATR",
        "Ichimoku", "ADX", "Supertrend", "Stochastic", "Pivot Points", "Volume Profile",
        "Volume Delta", "Open Interest", "Implied Volatility", "Greeks", "PCR", "Max Pain",
        "Moving Average", "Support and Resistance", "Order Block", "Market Structure", "VWAP Bands",
        "RRG", "UT Bot", "RSI Divergence", "AVWAP", "Chandelier Exit",
    ]
    indicator_rows = [
        (item, sum(bool(re.search(r"(?<!\\w)" + re.escape(item.casefold()) + r"(?!\\w)", text)) for _, text in indexed_tv))
        for item in indicators
    ]
    indicator_rows.sort(key=lambda item: (-item[1], item[0]))

    # Categories are normalisation labels, selected after a whole-corpus review;
    # they are not used to choose which records enter the analysis.
    topics = [
        "Chart speed / loading", "Data accuracy / mismatched prices", "Chart-to-order", "Stop-loss and target",
        "Trailing stop", "Risk-reward / payoff", "Multi-chart layouts", "Layout / chart synchronisation",
        "Saved indicator templates", "Watchlist sections / colour coding", "Drawing tools", "Custom indicators / Pine Script",
        "Indicator discovery / favourites", "Indicator management", "Price / indicator alerts", "Alert debugging",
        "Mobile chart usability", "Chart customisation", "Seconds / scalper charts", "Trade execution speed",
        "OI on chart / OI profile", "Volume profile / order flow", "Options chain", "Options data on chart",
        "Bid/ask and liquidity", "IV / Greeks", "Historical / intraday data", "Replay / backtesting",
        "Chart patterns / auto-detection", "Screeners / scans", "Market / index overview", "Heatmap",
        "Multiple monitors", "Pop-out charts", "Chart webhooks", "AI chart assistance", "Chart sharing / ideas",
        "Risk position sizing", "Support/resistance", "Price action", "Candlesticks", "Trendlines",
        "EMA", "SMA", "Momentum oscillators", "Volatility indicators", "Volume indicators", "Fibonacci tools",
        "Strategy signals", "Trade journal / performance", "Portfolio on chart", "User data import",
    ]
    aliases = {
        "Chart speed / loading": ("loading", "blank chart", "chart load", "chart not", "graph not moving", "lag", "freeze", "slow"),
        "Data accuracy / mismatched prices": ("price mismatch", "price differs", "different ath", "data issue", "stale", "delayed price", "ohlc"),
        "Chart-to-order": ("trade on chart", "trade from chart", "chart-to-order", "order from chart", "trading on charts"),
        "Stop-loss and target": ("stop loss", "stop-loss", "sl/tp", "sl and target", "target amount"),
        "Trailing stop": ("trailing stop", "trailing sl", "trail both"),
        "Risk-reward / payoff": ("risk reward", "risk:reward", "payoff"),
        "Multi-chart layouts": ("multi chart", "multiple charts", "grid mode", "layouts"),
        "Layout / chart synchronisation": ("chart sync", "synchronization", "synchronisation", "time syncing", "tab linking"),
        "Saved indicator templates": ("indicator template", "saved template", "presets"),
        "Watchlist sections / colour coding": ("watchlist", "colour coding", "color coding"),
        "Drawing tools": ("drawing tools", "drawings", "draw on chart"),
        "Custom indicators / Pine Script": ("pine script", "custom indicator", "script editor"),
        "Indicator discovery / favourites": ("favourite indicator", "favorite indicator", "indicator library"),
        "Indicator management": ("indicator management", "add indicator", "remove indicator", "indicators on chart"),
        "Price / indicator alerts": ("price alert", "indicator alert", "alerts"),
        "Alert debugging": ("debug alert", "view chart"),
        "Mobile chart usability": ("mobile chart", "android", "ios", "mobile-first"),
        "Chart customisation": ("customise", "customize", "customisation", "customization"),
        "Seconds / scalper charts": ("5 second", "5-second", "seconds chart", "scalper"),
        "Trade execution speed": ("execution speed", "fast execution", "one-click trading"),
        "OI on chart / OI profile": ("oi profile", "oi on chart", "open interest"),
        "Volume profile / order flow": ("volume profile", "volume footprint", "order flow", "volume delta"),
        "Options chain": ("options chain", "option chain"),
        "Options data on chart": ("options data", "options on chart"),
        "Bid/ask and liquidity": ("bid ask", "bid/ask", "liquidity"),
        "IV / Greeks": ("implied volatility", "greeks"),
        "Historical / intraday data": ("historical data", "intraday data", "seconds data"),
        "Replay / backtesting": ("replay", "backtesting", "backtest"),
        "Chart patterns / auto-detection": ("chart pattern", "pattern detection", "auto-detection"),
        "Screeners / scans": ("screener", "scanner", "scan"),
        "Market / index overview": ("index screener", "indices", "market overview"),
        "Heatmap": ("heatmap", "heat map"),
        "Multiple monitors": ("multiple monitors", "multi monitor"),
        "Pop-out charts": ("pop-out", "pop out"),
        "Chart webhooks": ("webhook", "web hook"),
        "AI chart assistance": ("ai chart", "chatgpt", "ai assistant"),
        "Chart sharing / ideas": ("trading idea", "share your view", "community ideas"),
        "Risk position sizing": ("position size", "risk management"),
        "Support/resistance": ("support resistance", "support and resistance"),
        "Price action": ("price action",),
        "Candlesticks": ("candlestick", "heikin ashi"),
        "Trendlines": ("trendline", "trend line"),
        "EMA": ("ema",),
        "SMA": ("sma",),
        "Momentum oscillators": ("rsi", "macd", "stochastic", "adx"),
        "Volatility indicators": ("atr", "bollinger", "supertrend"),
        "Volume indicators": ("vwap", "volume indicator"),
        "Fibonacci tools": ("fibonacci", "fib ", "fib."),
        "Strategy signals": ("strategy signal", "buy signal", "sell signal"),
        "Trade journal / performance": ("trade journal", "performance analysis"),
        "Portfolio on chart": ("portfolio", "p&l"),
        "User data import": ("import data", "excel data"),
    }
    positive = ("love", "like", "useful", "helpful", "easy", "smooth", "fast", "great", "best", "good", "reliable", "powerful", "clean", "simple", "better")
    negative = ("slow", "lag", "loading", "blank", "freeze", "glitch", "issue", "problem", "missing", "cannot", "not available", "clunky", "confusing", "frustrating", "mismatch", "stale", "delay")
    topic_rows = []
    for topic in topics:
        matches = [(row, text) for row, text in chart_indexed if any(alias in text for alias in aliases[topic])]
        if not matches:
            continue
        joined = " ".join(aliases[topic])
        # Direction is deliberately conservative: it records a chart-topic
        # post that also uses positive/negative language, not a sentiment score.
        pos = sum(any(word in text for word in positive) for _, text in matches)
        neg = sum(any(word in text for word in negative) for _, text in matches)
        word_count = sum(len(text.split()) for _, text in matches)
        topic_rows.append({"topic": topic, "records": len(matches), "engagement": sum(engagement(row) for row, _ in matches), "comments": sum(int((row.get("engagement") or {}).get("comments") or 0) for row, _ in matches if isinstance((row.get("engagement") or {}).get("comments"), (int, float))), "average_words": round(word_count / len(matches)), "positive": pos, "negative": neg})
    topic_rows.sort(key=lambda row: (-row["records"], -row["engagement"], row["topic"]))

    brand_terms = ["tradingview", "groww", "dhan", "sahi", "groww charts", "dhan chart", "sahi chart", "5-second", "5 second"]
    brand_rows = [(term, sum(bool(re.search(r"(?<!\\w)" + re.escape(term.casefold()) + r"(?!\\w)", text)) for _, text in chart_indexed)) for term in brand_terms]
    loading_terms = ["loading", "blank chart", "graph not moving", "lag", "freeze", "stale", "delayed", "price mismatch", "price differs"]
    loading_rows = [(term, sum(bool(re.search(r"(?<!\\w)" + re.escape(term.casefold()) + r"(?!\\w)", text)) for _, text in chart_indexed)) for term in loading_terms]
    loading_unique = sum(any(re.search(r"(?<!\\w)" + re.escape(term.casefold()) + r"(?!\\w)", text) for term in loading_terms) for _, text in chart_indexed)

    output = {
        "unique_tradingview_records": len(tv_rows),
        "unique_all_source_records": len(all_unique),
        "unique_chart_related_records": len(chart_indexed),
        "collection_days": file_counts,
        "monthly_feed_records": dict(monthly),
        "indicator_counts": indicator_rows,
        "brand_counts": brand_rows,
        "loading_counts": loading_rows,
        "loading_unique_records": loading_unique,
        "topic_rows": topic_rows,
    }
    path = ROOT / "reports" / "chart-market-analysis-2026-08-27.json"
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(path)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
