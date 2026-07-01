# Daily Manual Research Prompt

When the user says `dump todays social media data`, perform this workflow.

## Goal

Enrich today's scripted dump with public manual research covering retail trading, API/algo users, competitor signals, YouTube/social discussion, SEO/content opportunities and direct Nubra mentions.

## Research areas

### Retail

- option chain
- option buyer / option seller workflows
- OI trader workflows
- F&O analytics
- strategy builder
- payoff, margin, breakeven, probability of profit
- alerts, scanners and watchlists
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

## Final steps

After creating the JSONL file, run:

```powershell
.\.venv\Scripts\insights-publisher add-manual-research --date YYYY-MM-DD --input .\staging\manual_research_YYYY-MM-DD.jsonl --push
```

Then verify:

```powershell
.\.venv\Scripts\insights-publisher validate
```
