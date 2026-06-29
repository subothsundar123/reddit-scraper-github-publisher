# Retail Upcoming Features

Scope: retail app features only. API/SDK-only and MCP/internal connector features are excluded.

Total features: 17

## Retail App / F&O Analytics

### F&O analytics plotted against price

- Status: upcoming / source_document_evidence
- Surfaces: Mobile App
- Capability: Plot OI, IV, premium and volume against the live underlying price for every F&O stock.
- User benefit: Shows relationships between price and positioning instead of isolated numbers.
- Source note: FO Analytics document repeatedly positions metrics plotted against price as the key value.
- Keywords: plotted against price, against price, oi vs spot, iv vs spot, premium vs spot, volume vs price, every metric plotted against price, F&O analytics plotted against price

### Straddle and strangle premium charts

- Status: upcoming / source_document_evidence
- Surfaces: Mobile App
- Capability: Chart straddle premium and strangle premium against the underlying to track decay, expansion and seller opportunity.
- User benefit: Directly supports option sellers running non-directional premium strategies.
- Source note: FO Analytics document includes straddle and strangle premium charting.
- Keywords: straddle premium, strangle premium, premium chart, straddle premium chart, strangle premium chart, Straddle and strangle premium charts

### Buy/sell actionables inside F&O Analytics

- Status: upcoming / source_document_evidence
- Surfaces: Mobile App
- Capability: Actionable buy/sell entry points from F&O analytics views, connected to option chain and trading surfaces.
- User benefit: Turns analytics from passive charts into a trade workflow.
- Source note: Revamp sheet mentions buy/sell actionables in F&O Analytics.
- Keywords: buy/sell actionables, buy sell actionables, actionables, f&o analytics actionables, Buy/sell actionables inside F&O Analytics

### Futures analytics by expiry

- Status: upcoming / source_document_evidence
- Surfaces: Mobile App
- Capability: Show OI, volume and price across every futures expiry in one view.
- User benefit: Helps traders understand rollover, positioning and expiry-wise futures pressure.
- Source note: FO Analytics document calls this the full futures picture by expiry.
- Keywords: futures picture, full futures picture, futures by expiry, oi volume price by expiry, expiry-wise futures, Futures analytics by expiry

## Retail App / Option Chain

### Call View and Put View in option chain

- Status: upcoming / user_confirmed_new_build
- Surfaces: Mobile App, Option chain
- Capability: Dedicated Call View and Put View so traders can focus on one side of the option chain while still switching quickly between calls and puts.
- User benefit: Helps option buyers, sellers and OI traders reduce visual clutter and focus on the side of the chain relevant to the current trade idea.
- Source note: User clarified Call view and Put view should be included in the upcoming retail feature list.
- Keywords: Call view, Put view, Calls view, Puts view, Call and Put view, Call side view, Put side view

### Custom option-chain layout

- Status: upcoming / source_document_evidence
- Surfaces: Mobile App
- Capability: Customise/customize the option-chain layout, reorder variables and save the chain layout by trading need.
- User benefit: Lets users cut noise and build a chain view for their style instead of using the same default screen.
- Source note: Includes exact source keyword: customise your own layout; reorder variables accordingly.
- Keywords: customise your own layout, customize your own layout, custom layout, reorder variables, cut the noise, trader view, Custom option-chain layout, Call view, Put view, Calls view, Puts view, Call and Put view

### Option Buyer mode in option chain

- Status: upcoming / new_build_evidence
- Surfaces: Mobile App, Option chain
- Capability: Option-chain mode optimized for option buyers, visible as Option Buyer in the option-chain header.
- User benefit: Helps buyers focus on premium, momentum, liquidity, ITM/OTM visibility and relevant strike selection without manually configuring every column.
- Source note: Screenshot shows Option Buyer mode selected in the option-chain header.
- Keywords: Option Buyer, Buyer mode, Option chain buyer preset, Buyer preset

### Option Seller mode in option chain

- Status: upcoming / new_build_evidence
- Surfaces: Mobile App, Option chain
- Capability: Option-chain mode/preset expected for option sellers, complementary to Option Buyer mode.
- User benefit: Helps sellers focus on OI concentration, IV, theta, bid-ask spread, liquidity, margin/risk and strike safety instead of using a generic chain.
- Source note: User confirmed Option Seller mode exists in the new build. Treat as upcoming/new-build evidence until public rollout is confirmed.
- Keywords: Option Seller, Seller mode, Option chain seller preset, Seller preset

### Option-chain customization, filters and column controls

- Status: upcoming / new_build_evidence
- Surfaces: Mobile App, Option chain, Customize sheet
- Capability: Configurable option-chain settings and filters including OI bars, PCR, total OI, max pain, ITM highlighting, today high/low, VWAP, premium, OI, OI buildup, volume, volume spike, IV, IV change, Greeks, bid-ask spread and OI concentration.
- User benefit: Lets different trader personas tune the option chain to their strategy instead of forcing one default layout.
- Source note: Screenshots show Settings and Filters tabs with toggles and filters for core option-chain data, columns and Greeks.
- Keywords: Option chain filters, Customize option chain, OI filter, Premium filter, IV filter, Greeks filter, Bid ask spread filter, OI concentration, Show OI bars, Show PCR, Show Max Pain, Highlight ITM Options, VWAP column, Call view

### Total Call OI and Total Put OI on option chain

- Status: upcoming / source_document_evidence
- Surfaces: Mobile App
- Capability: Show total call OI and total put OI with PCR, Max Pain and strike ladder context.
- User benefit: Improves quick read of call/put positioning and market pressure.
- Source note: Revamp sheet mentions total call and put OI; screenshot confirms Total Put label.
- Keywords: total call, total put, total call oi, total put oi, call oi, put oi, Total Call OI and Total Put OI on option chain

## Retail App / Personalization

### Trader persona-based app modes/settings

- Status: upcoming / new_build_evidence
- Surfaces: Mobile App, Compass, Home customization, Option chain
- Capability: Persona-based experience for Option Sellers, Option Buyers, Investors and OI Traders, changing visible tools, defaults, layouts and guidance.
- User benefit: Reduces clutter and makes Nubra feel purpose-built for investor, option buyer, option seller and OI-based trader journeys.
- Source note: User clarified persona types as Option sellers, Option buyers, Investor and OI trader. Treat as upcoming until public rollout is confirmed.
- Keywords: Investor mode, Trader mode, Persona settings, Persona-based settings, Mode selector, User persona, Option Seller persona, Option Buyer persona, Investor persona, OI Trader persona, OI trader, Option sellers, Option buyers

### Homepage customisation

- Status: upcoming / source_document_evidence
- Surfaces: Mobile App
- Capability: Customise/customize homepage widgets and shortcuts around the user persona and preferred workflows.
- User benefit: Improves discovery of tools like option chain, strategies, F&O analytics, sector heatmap and FII-DII.
- Source note: Revamp sheet mentions homepage customisation.
- Keywords: homepage customisation, homepage customization, home screen customization, home customisation, home customization, Homepage customisation

## Retail App / Scalper & Trading View

### Scalper and Trading View template customisation

- Status: upcoming / source_document_evidence
- Surfaces: Mobile App
- Capability: Save templates/customisations for Scalper and Trading View style workflows.
- User benefit: Helps active users keep preferred layouts and reduce repeated setup.
- Source note: Revamp sheet mentions Scalper & Trading View new customisation - save templates.
- Keywords: scalper, trading view, save templates, template customisation, template customization, saved templates, Scalper and Trading View template customisation

## Retail App / Strategies

### Live strategy risk recalculation while building legs

- Status: upcoming / source_document_evidence
- Surfaces: Mobile App
- Capability: When users build a strategy leg by leg, risk updates live including payoff, max profit, max loss, breakeven, probability and margin impact.
- User benefit: Makes custom strategy building safer and more understandable before execution.
- Source note: Strategies Appstore document says pick strikes and expiries and watch risk update live.
- Keywords: risk update live, live risk update, leg by leg, build any strategy, pick strikes and expiries, risk recalculate live, Live strategy risk recalculation while building legs

### Payoff and analysis on the face

- Status: upcoming / user_confirmed_new_build
- Surfaces: Mobile App, Strategies, Option chain
- Capability: Show payoff and key strategy analysis upfront on strategy cards or the main interaction surface without forcing the trader to open a deeper details page.
- User benefit: Lets traders judge risk, reward, breakeven, probability and margin impact faster before entering or editing a strategy.
- Source note: User clarified payoff and analysis on the face should be included. This extends risk-first strategy cards and strategy discovery.
- Keywords: payoff on face, analysis on face, payoff and analysis on the face, visible payoff, front-facing analysis, strategy card analysis, payoff upfront

### Strategy Appstore taxonomy by market view, trader outcome and instrument set

- Status: upcoming / source_document_evidence
- Surfaces: Mobile App
- Capability: Classify pre-built strategies by Market View, Trader Outcome and Instrument Set. Market views include Bullish, Bearish, Sideways and Big News. Trader outcomes include Income, Hedge, Directional, Volatility and Arbitrage. Instrument sets include Stock, Future and Option.
- User benefit: Makes the strategy library easier to browse by intent rather than only by strategy name.
- Source note: Revamp sheet explicitly lists Market View, Trader Outcome and Instrument Set taxonomy.
- Keywords: market view, bullish, bearish, sideways, big news, trader outcome, income, hedge, directional, volatility, arbitrage, instrument set, stock, future

## Retail App / Trading

### One-click trade with bid/ask across strikes

- Status: upcoming / source_document_evidence
- Surfaces: Mobile App
- Capability: One-click trade actions directly from bid/ask or LTP cells across option-chain strikes.
- User benefit: Reduces execution friction for active traders while keeping risk controls visible.
- Source note: Revamp sheet mentions one click trade with Bid and Ask across strikes and one-click mode across the app.
- Keywords: one click trade, one-click trade, bid ask trade, bid and ask across strikes, one click mode, one-click mode across the app, One-click trade with bid/ask across strikes
