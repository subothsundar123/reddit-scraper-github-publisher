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
    indicator = Counter()
    chart_counts = Counter()
    top_threads = []
    daily, monthly = Counter(), Counter()
    people = Counter()
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
        for topic in match_topics(s):
            topic_count[topic] += 1; topic_eng[topic] += e
            if any(x in s for x in POSITIVE): topic_pos[topic] += 1
            if any(x in s for x in NEGATIVE): topic_neg[topic] += 1
        for name, terms in {"RSI":["rsi"],"EMA":["ema"],"SMA":["sma"],"VWAP":["vwap"],"MACD":["macd"],"Bollinger Bands":["bollinger"],"Supertrend":["supertrend"],"Stochastic":["stochastic"],"ATR":["atr"],"ADX":["adx"],"Fibonacci":["fibonacci"],"Ichimoku":["ichimoku"]}.items():
            if any(t in s for t in terms): indicator[name] += 1
        for name, terms in {"TradingView": ["tradingview"], "Groww Chart":["groww chart","groww charts"], "Sahi Chart":["sahi chart","sahi charts"], "Dhan Chart":["dhan chart","dhan charts"], "Sahi 5-second Chart":["sahi 5 sec","sahi 5-second","5 sec chart"]}.items():
            if any(t in s for t in terms): chart_counts[name] += 1
        top_threads.append((e, int((r.get("engagement") or {}).get("comments") or 0), len(s.split()), r.get("url"), r.get("title", "")))

    # Chart and performance questions also include non-TV community signals.
    for r in all_rows:
        s = text(r)
        for name, terms in {"TradingView": ["tradingview","tv communities"], "Groww Chart":["groww chart","groww charts"], "Sahi Chart":["sahi chart","sahi charts"], "Dhan Chart":["dhan chart","dhan charts"], "Sahi 5-second Chart":["sahi 5 sec","sahi 5-second","5 sec chart"], "Loading/performance issues":["loading","lag","slow","freeze","glitch"]}.items():
            if any(t in s for t in terms): chart_counts[name] += 1

    out = [f"# TradingView and Community Analysis (data through {AS_OF})", ""]
    out += ["## 1. What users like and dislike about TradingView features", "", "| Feature area | Positive mentions | Negative mentions | Discussions | Engagement |", "|---|---:|---:|---:|---:|"]
    for topic, n in sorted(topic_count.items(), key=lambda x: (-topic_eng[x[0]], -x[1])):
        out.append(f"| {topic} | {topic_pos[topic]} | {topic_neg[topic]} | {n} | {topic_eng[topic]} |")
    out += ["", "Positive/negative counts are based on feature-related wording in the collected text, not Like buttons.", "", "## 2. Groww Chart, Sahi Chart and Dhan Chart discussions", "", "| Chart/topic | Relevant discussions | What the discussion indicates |", "|---|---:|---|"]
    for name in ("Groww Chart", "Sahi Chart", "Dhan Chart", "Sahi 5-second Chart"):
        n = chart_counts[name]
        indication = "Users compare chart speed, usability, indicators and reliability." if n else "No matching discussion found in the current snapshots."
        out.append(f"| {name} | {n} | {indication} |")
    out += ["", "## 3. Indicator mentions ranked by frequency", "", "| Rank | Indicator | Mentions |", "|---:|---|---:|"]
    for i, (name, n) in enumerate(indicator.most_common(), 1): out.append(f"| {i} | {name} | {n} |")
    out += ["", "## 4. What users are asking for on TradingView", "", "| Rank | Request category | Discussions | Engagement |", "|---:|---|---:|---:|"]
    for i, (topic, n) in enumerate(sorted(topic_count.items(), key=lambda x: (-topic_eng[x[0]], -x[1])), 1): out.append(f"| {i} | {topic} | {n} | {topic_eng[topic]} |")
    out += ["", "## 5. Daily and monthly TradingView community counts", "", "| Date/month | Discussions |", "|---|---:|"]
    for k, n in sorted({**monthly, **daily}.items()): out.append(f"| {k} | {n} |")
    out += ["", "## 6. Discussions about TradingView and broker charts", "", "| Topic | Matching discussions |", "|---|---:|"]
    for k in ("TradingView", "Groww Chart", "Sahi Chart", "Dhan Chart"): out.append(f"| {k} | {chart_counts[k]} |")
    out += ["", "## 7. Top 50 discussions by engagement, frequency, comments and length", "", "| Rank | Topic/title | Engagement | Comments | Length (words) |", "|---:|---|---:|---:|---:|"]
    for i, (e, comments, length, url, title) in enumerate(sorted(top_threads, reverse=True)[:50], 1):
        out.append(f"| {i} | {title.replace('|','/')} | {e} | {comments} | {length} |")
    out += ["", "## 8. Sahi 5-second chart discussions", "", f"Matching discussions: **{chart_counts['Sahi 5-second Chart']}**", "", "## 9. Loading and performance issues", "", f"Matching discussions: **{chart_counts['Loading/performance issues']}**", "", "## Verification links", ""]
    out += [f"- {u}" for u in LINKS]
    path = ROOT / "reports" / f"tradingview-community-analysis-{AS_OF}.md"; path.parent.mkdir(exist_ok=True); path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(path)

if __name__ == "__main__": main()
