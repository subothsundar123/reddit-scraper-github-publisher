# Daily Manual Research Prompt

When the user says `dump todays social media data`, perform this workflow.

## Goal

Enrich today's scripted dump with public manual research covering retail trading, API/algo users, competitor signals, YouTube/social discussion, SEO/content opportunities and direct Nubra mentions.

## Nubra brand sweep

Always begin with the broad public searches in `manual-research/source-query-bank.json` under `nubra_brand_sweep_queries`.
Review relevant public results containing Nubra even when they do not match a predefined feature keyword. Classify useful results afterward by feature, persona and intent. This broad sweep is the discovery layer for unexpected complaints, praise, comparisons and new product ideas.

Then use the targeted retail queries in `config/retail_feature_keywords.json` to recover long-tail feature discussions that broad ranked search results may omit.

## Research areas

### Retail

- option chain
- option buyer / option seller workflows
- OI trader workflows
- F&O analytics
- strategy builder
- payoff, margin, breakeven, probability of profit
- alerts, scanners and watchlists
- 250-instrument watchlists and automatic refresh
- OMS presets, best-fill execution and one-click mode
- instant fund movement and flexible brokerage
- AI-generated scans and chart analysis
- persona modes for option buyers, option sellers, investors, OI traders and scalpers
- strategy-level portfolios, P&L/risk-reward SL-TP and quantity sizing
- 40+ pre-built strategies and multi-instrument time-series charts
- iceberg modes, GTT, AMO and flexible order modification
- technical alerts, option-chain alerts and bid/ask visibility
- portfolio, investor mode and FII/DII
- PCR, max pain, IV, Greeks, OI buildup and volume spike
- trading app reviews, complaints and broker comparisons

### API/algo

- broker API issues
- WebSocket reliability
- historical data
- order execution and OMS
- SDK/docs/examples
- TOTP, static IP and session management
- backtesting, UAT and paper trading
- algo automation
- MCP/AI trading workflows

### Competitors

- Zerodha
- Dhan
- Fyers
- Upstox
- Angel One
- Sensibull
- Opstra
- AlgoTest
- TradingView
- StockEdge
- StockMock
- NiftyTrader

### Marketing and SEO

- high-priority SEO keywords
- competitor ranking pages
- content gaps
- webinar opportunities
- lead magnet opportunities

## Output format

Write one JSON object per line to:

```text
staging/manual_research_YYYY-MM-DD.jsonl
```

Use `manual-research/output-template.jsonl` as the shape.
When evidence permits, populate `feature_ids`, `personas` and `signal_type`. The merge command will infer them from the text when they are omitted.

## Final steps

After creating the JSONL file, run:

```powershell
.\.venv\Scripts\insights-publisher add-manual-research --date YYYY-MM-DD --input .\staging\manual_research_YYYY-MM-DD.jsonl --push
```

Then verify:

```powershell
.\.venv\Scripts\insights-publisher validate
```
