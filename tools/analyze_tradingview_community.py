"""Answer the TradingView/community questions from published snapshots."""
from __future__ import annotations

import gzip
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-08-27"

TOPICS = {
    "Charts and charting": ["chart", "candlestick", "layout", "drawing", "trendline"],
    "Indicators": ["indicator", "rsi", "ema", "sma", "vwap", "macd", "bollinger", "supertrend", "stochastic", "atr", "adx", "ichimoku", "fibonacci"],
    "Option-chain analytics": ["option chain", "open interest", "oi", "pcr", "max pain", "implied volatility", "iv", "strike"],
    "Alerts and automation": ["alert", "webhook", "automation", "strategy", "script", "pine"],
    "Backtesting and replay": ["backtest", "back-testing", "replay", "paper trading", "paper-trading"],
    "Execution and order workflow": ["order", "execution", "slippage", "broker", "buy", "sell", "scalper"],
    "Risk and payoff": ["stop loss", "stop-loss", "target", "payoff", "breakeven", "breakeven", "hedg", "risk reward", "risk-reward", "margin"],
    "Performance and reliability": ["loading", "load", "lag", "slow", "freeze", "crash", "disconnect", "reliab", "glitch", "latency"],
    "Community and ideas": ["idea", "community", "publish", "follow", "social", "script"],
    "Watchlists and screeners": ["watchlist", "screener", "scanner", "filter"],
}
POSITIVE = ["like", "love", "useful", "helpful", "easy", "smooth", "fast", "powerful", "clean", "best", "good", "great", "reliable", "accurate", "convenient", "simple"]
NEGATIVE = ["hate", "bad", "poor", "confus", "difficult", "hard", "slow", "lag", "loading", "crash", "freeze", "glitch", "missing", "expensive", "cannot", "can't", "issue", "problem", "disappoint"]
LINKS = [
    "https://in.tradingview.com/ideas/",
    "https://in.tradingview.com/ideas/options/",
    "https://in.tradingview.com/ideas/optionchain/",
    "https://in.tradingview.com/ideas/niftyoptions/",
    "https://in.tradingview.com/ideas/banknifty/",
    "https://in.tradingview.com/ideas/niftystrategy/",
    "https://in.tradingview.com/ideas/optionbuying/",
    "https://in.tradingview.com/symbols/NSE-NIFTY/ideas/",
]

def rows(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue

def engagement(row: dict) -> int:
    e = row.get("engagement") or {}
    return sum(int(e.get(k) or 0) for k in ("score", "comments", "boosts", "likes", "view_count"))

def text(row: dict) -> str:
    return f"{row.get('title','')} {row.get('body','')} {row.get('description','')}".casefold()

def match_topics(s: str) -> list[str]:
    return [name for name, terms in TOPICS.items() if any(t in s for t in terms)]

def main() -> None:
    tv, all_signals = {}, []
    for dump in sorted((ROOT / "daily-dumps").glob("*/")):
        p = dump / "tradingview_signals.jsonl.gz"
        if p.exists():
            for r in rows(p):
                tv.setdefault(r.get("id") or r.get("url"), r)
        p = dump / "signals.jsonl.gz"
        if p.exists():
            for r in rows(p):
                all_signals.append(r)
    tv_rows = list(tv.values())
    # Keep only records with a TV URL for TV-specific counts.
    tv_rows = [r for r in tv_rows if "tradingview" in str(r.get("url", "")).casefold() or str(r.get("source", "")).casefold() == "tradingview"]
    all_rows = {r.get("id") or r.get("url"): r for r in all_signals if r.get("id") or r.get("url")}
    all_rows.update({r.get("id") or r.get("url"): r for r in tv_rows})
    all_rows = list(all_rows.values())

    topic_count, topic_eng, topic_pos, topic_neg = Counter(), Counter(), Counter(), Counter()
    topic_comments, topic_words = Counter(), Counter()
    indicator = Counter()
    chart_counts = Counter()
    chart_sources = defaultdict(Counter)
    top_threads = []
    daily, monthly = Counter(), Counter()
    people = Counter()
    author_sets = defaultdict(set)
    for r in tv_rows:
        s = text(r)
        e = engagement(r)
        d = str(r.get("created_at") or r.get("collected_on") or "")[:10]
        if re.match(r"^20\d{2}-\d{2}-\d{2}$", d):
            daily[d] += 1
            monthly[d[:7]] += 1
        author = r.get("author_hash")
        if author:
            people["TradingView authors"] += 1
            author_sets["TradingView"].add(author)
        for topic in match_topics(s):
            topic_count[topic] += 1; topic_eng[topic] += e
            topic_comments[topic] += int((r.get("engagement") or {}).get("comments") or 0)
            topic_words[topic] += len(s.split())
            if any(x in s for x in POSITIVE): topic_pos[topic] += 1
            if any(x in s for x in NEGATIVE): topic_neg[topic] += 1
        for name, terms in {"RSI":["rsi"],"EMA":["ema"],"SMA":["sma"],"VWAP":["vwap"],"MACD":["macd"],"Bollinger Bands":["bollinger"],"Supertrend":["supertrend"],"Stochastic":["stochastic"],"ATR":["atr"],"ADX":["adx"],"Fibonacci":["fibonacci"],"Ichimoku":["ichimoku"]}.items():
            if any(t in s for t in terms): indicator[name] += 1
        for name, terms in {"TradingView": ["tradingview"], "Groww Chart":["groww chart","groww charts"], "Sahi Chart":["sahi chart","sahi charts"], "Dhan Chart":["dhan chart","dhan charts"], "Sahi 5-second Chart":["sahi 5 sec","sahi 5-second","5 sec chart"]}.items():
            if any(t in s for t in terms):
                chart_counts[name] += 1
                chart_sources[name][str(r.get("source") or "unknown")] += 1
            if any(t in s for t in terms) and r.get("author_hash"):
                author_sets[name].add(r["author_hash"])
        category = match_topics(s)[0] if match_topics(s) else "Other TradingView discussion"
        top_threads.append((e, int((r.get("engagement") or {}).get("comments") or 0), len(s.split()), category))

    # Chart and performance questions also include non-TV community signals.
    for r in all_rows:
        s = text(r)
        for name, terms in {"TradingView": ["tradingview","tv communities"], "Groww Chart":["groww chart","groww charts"], "Sahi Chart":["sahi chart","sahi charts"], "Dhan Chart":["dhan chart","dhan charts"], "Sahi 5-second Chart":["sahi 5 sec","sahi 5-second","5 sec chart"], "Loading/performance issues":["loading","lag","slow","freeze","glitch"]}.items():
            if any(t in s for t in terms):
                chart_counts[name] += 1
                chart_sources[name][str(r.get("source") or "unknown")] += 1

    out = [f"# TradingView and Community Analysis (data through {AS_OF})", ""]
    out += ["## 1. What users like and dislike about TradingView features", "", "| Feature area | Positive mentions | Negative mentions | Discussions | Engagement | Product reading |", "|---|---:|---:|---:|---:|---|"]
    product_reading = {"Option-chain analytics":"Users value decision-ready derivatives context, not just raw quotes.", "Execution and order workflow":"Chart-to-order speed and control are central to perceived quality.", "Indicators":"Breadth matters, but setup clarity and responsiveness matter more.", "Risk and payoff":"Pre-trade risk visibility is a recurring adoption lever.", "Charts and charting":"Chart reliability and customisation are foundational expectations.", "Community and ideas":"Discovery and education can turn analysis into repeat usage.", "Alerts and automation":"Users want dependable, actionable notifications.", "Performance and reliability":"Reliability issues can outweigh feature breadth.", "Watchlists and screeners":"Reusable discovery workflows reduce daily effort.", "Backtesting and replay":"Users need evidence before trusting a strategy."}
    for topic, n in sorted(topic_count.items(), key=lambda x: (-topic_eng[x[0]], -x[1])):
        out.append(f"| {topic} | {topic_pos[topic]} | {topic_neg[topic]} | {n} | {topic_eng[topic]} | {product_reading.get(topic, 'Validate the theme with qualitative review.')} |")
    out += ["", "Positive/negative counts are based on feature-related wording in the collected text, not Like buttons.", "", "## 2. Groww Chart, Sahi Chart and Dhan Chart discussions", "", "These are keyword matches across the corpus, not verified unique people. A YouTube title or broker page is product evidence, not community sentiment.", "", "| Chart/topic | Corpus matches | Source mix | What can be concluded |", "|---|---:|---|---|"]
    for name in ("Groww Chart", "Sahi Chart", "Dhan Chart", "Sahi 5-second Chart"):
        n = chart_counts[name]
        mix = ", ".join(f"{k}: {v}" for k,v in chart_sources[name].most_common()) or "No matching source"
        indication = "Needs community-specific collection before claiming user preference." if n else "No matching record in the current snapshots."
        out.append(f"| {name} | {n} | {mix} | {indication} |")
    out += ["", "## 3. Indicator mentions ranked by frequency", "", "| Rank | Indicator | Mentions |", "|---:|---|---:|"]
    for i, (name, n) in enumerate(indicator.most_common(), 1): out.append(f"| {i} | {name} | {n} |")
    out += ["", "## 4. What users are asking for on TradingView", "", "| Rank | Request category | Discussions | Engagement | Product opportunity |", "|---:|---|---:|---:|---|"]
    for i, (topic, n) in enumerate(sorted(topic_count.items(), key=lambda x: (-topic_eng[x[0]], -x[1])), 1): out.append(f"| {i} | {topic} | {n} | {topic_eng[topic]} | {product_reading.get(topic, 'Validate before prioritising.')} |")
    out += ["", "## 5. Daily and monthly TradingView community counts", "", "| Date/month | Discussions |", "|---|---:|"]
    for k, n in sorted({**monthly, **daily}.items()): out.append(f"| {k} | {n} |")
    out += ["", "## 6. Discussions about TradingView and broker charts", "", "| Topic | Matching discussions | Unique authors |", "|---|---:|---:|"]
    for k in ("TradingView", "Groww Chart", "Sahi Chart", "Dhan Chart"): out.append(f"| {k} | {chart_counts[k]} | {len(author_sets[k]) if author_sets[k] else 'Not available'} |")
    out += ["", "Author counts use the anonymized author hash when the source exposes it; they are not inferred from thread counts."]
    # Group the most-engaged records by product theme. Listing individual records
    # made the previous report repeat the same broad category many times.
    grouped = {category: {"records": topic_count[category], "engagement": topic_eng[category], "comments": topic_comments[category], "words": topic_words[category]} for category in topic_count}
    implications = {
        "Option-chain analytics": "Expose actionable chain filters, OI/IV context and saved views.",
        "Execution and order workflow": "Reduce chart-to-order friction and make order status explicit.",
        "Indicators": "Prioritise fast indicator setup, presets and clear explanations.",
        "Risk and payoff": "Make payoff, SL/TP and risk-reward visible before order placement.",
        "Charts and charting": "Invest in speed, layouts, drawings and consistent price display.",
        "Community and ideas": "Improve discovery, publishing, follow and idea-to-trade workflows.",
        "Alerts and automation": "Support dependable alerts, webhooks and reusable conditions.",
        "Performance and reliability": "Instrument load time, errors and disconnects and surface status.",
        "Watchlists and screeners": "Add reusable filters, saved screens and fast watchlist actions.",
        "Backtesting and replay": "Connect replay/backtesting to rules, metrics and paper execution.",
        "Other TradingView discussion": "Review manually before converting into a roadmap theme.",
    }
    out += ["", "## 7. Product opportunity ranking", "", "Themes are grouped once across the full corpus. Engagement is a prioritisation signal, not a user count.", "", "| Rank | Product theme | Records | Engagement | Comments | Avg. length | Product implication |", "|---:|---|---:|---:|---:|---:|---|"]
    ranked = sorted(grouped.items(), key=lambda kv: (-kv[1]["engagement"], -kv[1]["records"]))
    for i, (category, g) in enumerate(ranked, 1):
        avg = round(g["words"] / g["records"]) if g["records"] else 0
        out.append(f"| {i} | {category} | {g['records']} | {g['engagement']} | {g['comments']} | {avg} | {implications.get(category, 'Validate with qualitative review before prioritising.')} |")
    out += ["", "## 8. Sahi 5-second chart discussions", "", f"Matching records: **{chart_counts['Sahi 5-second Chart']}**. Sahi publicly describes a 5-second chart in Scalper Mode, but the current TradingView-community corpus contains no matching user discussion.", "", "## 9. Loading and performance issues", "", f"Matching records: **{chart_counts['Loading/performance issues']}**. This is a broad keyword signal across sources and is not a platform-specific incident count.", "", "## 10. Source validation", "", "TradingView does have a native options-chain product today, including calls-only, puts-only and straddle views, expiry/strike/spread filters, bid/ask, Greeks and implied volatility. Option-chain mentions in this report describe discussion themes; they do not mean TradingView lacks an option chain.", "", "Groww, Dhan and Sahi chart claims are product evidence from official pages. They are separate from community sentiment counts.", "", "## Verification links", ""]
    out += ["- https://www.tradingview.com/support/solutions/43000760837-options-chain-overview/", "- https://www.tradingview.com/features/", "- https://groww.in/groww-charts", "- https://dhan.co/tradingview/", "- https://www.sahi.com/video-guide/en/all-about-the-sahi-scalper-mode-sahiapp", "- https://www.reddit.com/r/NSEbets/comments/1rwbk91/trading_charts_performance_analysis_fyers_vs_sahi/", "- https://www.reddit.com/r/NSEbets/comments/1tqwpit/groww_glitch/", "- https://www.reddit.com/r/IndianStockMarket/comments/1ntib7f/ama_with_the_dhan_team/"]
    path = ROOT / "reports" / f"tradingview-community-analysis-{AS_OF}.md"; path.parent.mkdir(exist_ok=True); path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(path)

if __name__ == "__main__": main()
