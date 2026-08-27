# Broker Chart Community Analysis — Dhan, Groww and Sahi

Research window: 29 May to 27 August 2026

## 1. Scope and evidence

This report combines the available local corpus with fresh public web research. Sources include Reddit-indexed pages, public community forums, YouTube titles/descriptions, TradingView ideas and official broker pages. Reddit API collection was rate-limited during part of the window, so the counts below are source-record matches, not a census of all users. A zero means no matching record was found in the collected corpus; it does not mean the product or feature does not exist.

The local TradingView feed has reliable coverage from 22 July onward. Earlier dates in the 90-day window have limited or no TradingView records.

## 2. What each broker publicly offers

| Broker | Chart and workflow evidence | Product relevance |
|---|---|---|
| TradingView | Native options chain with calls/puts/straddle views, expiry/strike/spread filters, bid/ask, Greeks and IV. | Sets the benchmark for analysis depth and customisation. |
| Dhan | TradingView integration, option/futures chain, multiple layouts, basket orders, drag-and-drop orders, live P&L and chart trading. | Strong benchmark for chart-to-order execution. |
| Groww | Mobile-first charts, trade-from-chart, SL/target actions, indicators and drawings; publicly claims 0.6s chart load and 0.2s tick latency. | Benchmark for simple mobile chart UX and speed messaging. |
| Sahi | In-house charts, direct chart execution, OI on chart, 100+ indicators, seconds-level charts and chart-based trailing SL. | Benchmark for trader-persona workflows and fast intraday interaction. |

## 3. Community corpus coverage by broker

| Topic | Community/forum records | YouTube records | Official/manual records | TradingView records | What this means |
|---|---:|---:|---:|---:|---|
| Groww chart | 63 | 143 | 8 | 17 | Strong video/product visibility; community evidence is smaller and includes both usability and lag themes. |
| Dhan chart | 879 | 242 | 37 | 1 | Most visible in the collected corpus; discussion spans chart execution, reliability, options and data quality. |
| Sahi chart | 23 | 142 | 2 | 1 | Feature visibility is high in video content, but community sample is too small for frequency claims. |
| TradingView | 175 | 169 | 14 | 633 | Largest native TradingView discussion base; it should not be treated as broker-specific sentiment. |

## 4. What people like

| Theme | Evidence across sources | Product reading |
|---|---|---|
| Trade directly from charts | Dhan, Groww and Sahi pages plus community comparisons | Users value fewer steps between analysis and order placement. |
| Fast, responsive charts | Groww speed claims, Sahi latency claims and chart-performance discussions | Perceived latency is a core trust signal for intraday and options users. |
| Options context on the chart | TradingView, Dhan and Sahi product pages | OI, chain, Greeks and liquidity context are moving into the primary chart workflow. |
| Customisation | Layouts, indicators, drawings and saved views appear across broker products | Users want a personal workspace that persists across sessions. |
| Visible risk controls | Chart SL/target/trailing controls and payoff/risk discussions | Risk controls should be placed at decision time, not hidden after execution. |

## 5. What people dislike or report as friction

| Friction | Evidence | Product implication |
|---|---|---|
| Loading, lag and stale charts | Groww complaints, Dhan support FAQs and broker review pages | Measure chart load, tick freshness, reconnects and error rate; expose status transparently. |
| Price/OHLC mismatch | Dhan community posts and indexed Reddit comparisons | Show exchange timestamp, data source and reconciliation status when values differ. |
| Chart-to-order gaps | Dhan reviews and community requests for SL/target on chart | Treat entry, SL, target, modify and exit as one workflow. |
| Complexity on mobile | Groww and Sahi comparisons mention different trade-offs between simplicity and depth | Offer persona-based defaults rather than exposing every control at once. |
| Limited evidence for Sahi 5-second demand | The feature is officially documented, but no matching TradingView-community record was found | Validate demand through Sahi-specific communities before prioritising a clone. |

## 6. Indicator and analytics demand

The TradingView idea corpus is dominated by moving averages and momentum tools. Ranked mentions are: EMA, SMA, RSI, Fibonacci, MACD, VWAP, Bollinger Bands, ATR, Ichimoku, ADX, Supertrend and Stochastic. These are discussion mentions, not proof that each indicator is a requested broker feature.

The product opportunity is to make common indicators fast to apply, easy to save as presets and understandable for each trader persona. Differentiation is more likely to come from combining indicators with OI, liquidity, alerts and risk controls than from adding an unbounded indicator list.

## 7. What users are asking for

Across the combined evidence, the recurring asks are:

- Reliable real-time data and no chart freezing during market open.
- One-screen chart-to-order execution with entry, SL, target and trailing controls.
- Option-chain and OI information available beside or on the chart.
- Saved layouts, multi-chart views, drawing tools and reusable indicator presets.
- Better visibility into data freshness, price differences and order status.
- Faster mobile workflows for scalping and options trading.

## 8. Loading and performance signal

Loading-related language appears in broker support content, reviews and community records. It is a broad signal rather than a verified incident count because sources use different terms such as lag, blank chart, stale candle, freeze and slow refresh. Dhan has a dedicated support cluster for blank charts, stale prices, lag while drawing and candle updates; Groww publicly documents graph-not-moving causes and community posts report peak-time lag.

## 9. Product priorities derived from the evidence

1. **Chart reliability layer:** instrument load time, tick freshness, reconnects, blank states and candle integrity; show a user-facing status indicator.
2. **Chart-to-order workflow:** support entry, SL, target, trailing SL, modification and exit without leaving the chart.
3. **Options decision surface:** combine chain, OI, IV, Greeks, bid/ask and liquidity with the chart and persona defaults.
4. **Personal workspaces:** saved layouts, indicator presets, drawings and multi-chart views across devices.
5. **Persona-first defaults:** investor, option buyer, option seller, OI trader and scalper modes should change the information density and default actions.
6. **Evidence-led messaging:** publish measured performance and data freshness rather than broad “fast” claims alone.

## 10. Validation links

- https://www.tradingview.com/support/solutions/43000760837-options-chain-overview/
- https://groww.in/groww-charts
- https://groww.in/help/stocks%2C-f%26o-%26-ipo/searchable/why-is-the-graph-not-moving-during-market-hours
- https://dhan.co/tradingview/
- https://dhan.co/support/platforms/tradingview/my-chart-isn-t-loading-the-screen-is-blank-or-prices-aren-t-moving-what-should-i-do/
- https://www.sahi.com/advantage/charts
- https://www.sahi.com/video-guide/en/all-about-the-sahi-scalper-mode-sahiapp
- https://www.reddit.com/r/NSEbets/comments/1rwbk91/trading_charts_performance_analysis_fyers_vs_sahi/
- https://www.reddit.com/r/NSEbets/comments/1tqwpit/groww_glitch/
- https://www.reddit.com/r/IndianStockMarket/comments/1urih68/zerodha_vs_dhan_realtime_charts_data_issue/
- https://www.reddit.com/r/DalalStreetTalks/comments/1uw67c2/broker_lag_at_915_is_actually_frustrating/
- https://madefortrade.in/t/new-ideas-add-on-charts/61015
