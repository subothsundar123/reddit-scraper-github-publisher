# CAS and Pre-open UI Research

## Scope

CAS below means the Closing Auction Session for CAS-eligible cash equities. Pre-open means the call-auction price-discovery window before the normal market opens. The findings combine official exchange and broker material with public community feedback collected on 31 August 2026.

## 1. Closing Auction Session (CAS)

### What brokers currently show

| Broker / source | UI surface | Values disclosed or visible |
|---|---|---|
| [NSE](https://www.nseindia.com/market-data/closing-auction-session) | Public CAS page | Searchable live table: reference price, best bid/ask price and quantity, IEP, IEQ, change, final price/volume/value and imbalance. |
| [Zerodha](https://zerodha.com/z-connect/updates/track-closing-auction-session-on-kite-web) | Kite Web market depth; index view; separate [CAS dashboard](https://zerodha.com/cas/) | Reference price, indicative close and total imbalance in market depth. Index view shows indicative close. The standalone dashboard lists reference price, indicative close, % change and imbalance across NSE/BSE. |
| [Dhan](https://dhan.co/support/general/market-session-status-and-timing/what-is-the-indicative-equilibrium-price-iep/) | Same place as LTP; separate [Markets → Live → CAS Dashboard](https://madefortrade.in/t/introducing-cas-dashboard-on-dhan-web-watch-the-closing-auction-live/92645) | At the symbol level, IEP replaces the live-price surface. The dashboard adds reference price, LTP before CAS, imbalance, indicative close, % change from the pre-CAS LTP and NSE/BSE exchange-arbitrage view. |
| [5paisa](https://tradebetter.5paisa.com/t/important-nse-bse-closing-auction-session-cas-changes-effective-3rd-aug-26/942) | Company Page, below market depth | CAS-eligible tag, indicative close, reference price, imbalance and % change from close. It documents separate index and stock-futures handling. |
| [Groww](https://groww.in/blog/understanding-closing-prices) | Live price surface, exact screen not publicly specified | Indicative prices for F&O stocks and BSE indices; its published CAS explainer says indicative tradable quantity and indicative imbalance are shown alongside indicative close. |
| [ICICI Direct](https://www.icicidirect.com/faqs/stocks/what-are-the-different-prices-quantities-displayed-during-closing-auction-session) | Exact screen not publicly specified | Reference price, indicative price, indicative quantity, imbalance, market-order imbalance, CAS LTP/estimated close and indicative index. |
| [Kotak Neo](https://www.kotakneo.com/support/where-can-i-view-the-indicative-closing-price-during-closing-auction-session-cas/) | Automatic eligible-stock and index display; exact screen not publicly specified | Indicative close from 3:20 PM; indicative values for NIFTY, BANKNIFTY, SENSEX and BANKEX through CAS. |

### What public feedback is asking for

The feedback is still new and narrow because CAS went live only in August. Counts below are **unique, placement-specific public asks captured in this enrichment**, not total users, votes or market demand. A repeated comment by the same member is counted once.

| Requested surface | Direct asks | What was asked for |
|---|---:|---|
| Dedicated CAS dashboard / scanner | 1 | A market-wide live view of IEP, indicative matched quantity, imbalance and a close-window countdown. [Source](https://madefortrade.in/t/coming-up-closing-auction-session-cas-here-is-everything-you-need-to-know-about-it/92072/3) |
| Normal quote / ticker / LTP surface | 1 | Indicative close should be prominent on the ticker rather than buried in a separate view. [Source](https://madefortrade.in/t/introducing-cas-dashboard-on-dhan-web-watch-the-closing-auction-live/92645) |
| Index page / index section | 1 | Indicative-close updates for indices. [Source](https://madefortrade.in/t/introducing-cas-dashboard-on-dhan-web-watch-the-closing-auction-live/92645) |
| Market depth and order-state context | 1 | Indicative price, available buy/sell quantity, whether an order is pending/modified/matched, LTP-vs-expected-close difference, and MTM/margin/F&O-position effect. [Source](https://www.reddit.com/r/IndianStockMarket/comments/1vgatz7/cas_has_changed_the_last_15_minutes_of_the_market/) |
| Alerts | 1 | Alert when indicative close moves past a user-defined percentage or imbalance crosses a threshold. [Source](https://madefortrade.in/t/introducing-cas-dashboard-on-dhan-web-watch-the-closing-auction-live/92645) |
| Historical replay | 1 | Second-by-second playback of IEP, imbalance and exchange-arbitrage changes. [Source](https://madefortrade.in/t/introducing-cas-dashboard-on-dhan-web-watch-the-closing-auction-live/92645) |
| API field / stream | 2 | Live IEP plus volume/reference data for a programmatic feed. This is not a retail UI request, but it affects parity for advanced users. [Sources](https://madefortrade.in/t/introducing-cas-dashboard-on-dhan-web-watch-the-closing-auction-live/92645), [Angel One forum](https://smartapi.angelone.in/smartapi/forum/topic/5657/closing-auction-session-cas-elment-like-iep-volume-related) |
| Option chain | 0 | No direct public request found to put CAS data into every strike row. CAS is a cash-equity auction; a contextual underlying-CAS strip is more appropriate than repeating cash-auction values across strikes. |

### Reviews and issues in the discussion

| Positive feedback | Negative feedback / concern |
|---|---|
| Dhan users called the dashboard useful because it avoids switching through individual scrips and keeps imbalance beside the indicative close. | Early CAS rollout created confusion when broker terminals displayed a frozen LTP while the official close was moving; market reporting says many investors could not see IEP unless they had already placed an auction order. [Source](https://www.moneycontrol.com/news/business/markets/sebi-asks-brokers-to-beef-up-cas-awareness-upgrade-systems-no-rollback-on-cards-13995193.html) |
| The live dashboard makes end-of-day price discovery observable rather than only showing the result after the auction. | A Dhan community member reported its dashboard filters not working. |
| The LTP-before-CAS anchor plus indicative-close change is viewed as useful for seeing the forming closing move. | A Dhan user flagged cash-equity stop-loss cancellation during CAS as the material risk they needed surfaced. |

### Recommended CAS design

| Priority | Exact location | Exact values and behaviour |
|---|---|---|
| P0 | **Normal stock quote header / live-price card** | When an eligible stock enters CAS, replace the ambiguous frozen LTP state with `Indicative Close` as the primary live value. Keep `LTP at 3:15` and `Reference Price` directly below it, then show `₹ and % change vs LTP at 3:15`. Add a clear `Indicative — not final` label and a session-status chip. |
| P0 | **Market-depth drawer** | Show `Reference Price`, `IEP / Indicative Close`, `Indicative Executable Quantity`, `Total Buy Qty`, `Total Sell Qty`, `Net Imbalance` with buy/sell side, `Market-Order Imbalance`, and the `±3% CAS price band`. The exchange disseminates this auction context; do not force the customer to infer it from a stale LTP. [NSE specification](https://www.nseindia.in/static/products-services/closing-auction-session) |
| P0 | **Order ticket and orders screen** | Add phase-aware copy: `No orders accepted`, `Market + limit allowed`, `Limit only`, `Auction matching`, or `Final close confirmed`. For an open order, show its CAS state and the user’s limit relative to IEP. Include a short warning where an order type is not allowed or will be cancelled. |
| P0 | **Index quote card** | During CAS, label NIFTY/SENSEX as `Indicative Close` rather than presenting it as ordinary live LTP. Show the percentage change and a link to the relevant eligible-stock breakdown. |
| P1 | **Dedicated CAS scanner** | Include all CAS-eligible symbols. Default columns: `Indicative Close`, `% vs 3:15 LTP`, `Reference`, `Imbalance side/quantity`, `Executable Qty`, `NSE/BSE spread`, `session status`. Support sorting by % move and imbalance. This is the proven Dhan/Zerodha pattern for users monitoring more than one name. |
| P1 | **Charts and option-chain context** | On a CAS-eligible stock chart, mark the 3:15 LTP and current IEP with a short auction band/marker. In a stock option chain, show only a compact **underlying CAS strip** at the top: IEP, Δ vs 3:15 LTP and phase. Do not place the same cash-market CAS values on every option strike. |
| P2 | **Alerts and history** | Allow alerts for IEP movement vs 3:15 LTP and for imbalance thresholds. Store a post-close time series of IEP, executable quantity, imbalance and NSE/BSE difference for replay and research. |

## 2. Pre-open auction

### What is in the current buzz

| Topic | Evidence from public discussion |
|---|---|
| When does the displayed value become final? | A current community question asks whether the value near the end of collection is still indicative, when the opening price is finalised, and when broker/API data switches from indicative to final. [Source](https://madefortrade.in/t/pre-open-session-when-is-the-opening-price-actually-finalized/93141) |
| AMO and gap-open uncertainty | Retail questions repeatedly ask whether an after-market order executes at the prior close or the discovered open, especially for gap-up/gap-down situations. [Source](https://www.reddit.com/r/IndianStockMarket/comments/z0qpdx/how_does_gap_markets_work_and_some_specific_doubts/) |
| Buyer-versus-seller depth before an IPO listing | Listing-day discussions ask how to see buyer depth and point users to the stock page before the stock starts normal trading. [Source](https://www.reddit.com/r/IPO_India/comments/1vzurb5/tempsens_ipo_holdsell/) |
| New session design | The revised pre-open framework is due on 7 September 2026. It brings CAS-like order-entry phases, random closure and a market-order cutoff. [Zerodha explanation](https://tradingqna.com/t/modifications-in-pre-open-session-in-the-equity-segment-starting-september-7-2026/196662) |
| Data-quality concern | Traders have historically reported confusion where a chart’s first live candle did not appear to match the pre-open/opening price. The product should explicitly distinguish final auction open from the first continuous-market tick. [Source](https://tradingqna.com/t/why-many-of-the-stocks-opening-price-in-normal-market-after-9-15am-is-same-with-equilibrium-price/18164) |

### Exchange values that should be surfaced

NSE documents an `Indicative Equilibrium / Opening Price`, `Total Buy Qty`, `Total Sell Qty`, `% change vs previous close`, and `Indicative Equilibrium Quantity` for pre-open. It also says the market-depth surface carries best bids/offers and their quantities. [NSE specification](https://www.nseindia.com/static/products-services/equity-derivatives-pre-open-session) and [Zerodha’s implementation note](https://tradingqna.com/t/modifications-in-pre-open-session-in-the-equity-segment-starting-september-7-2026/196662).

### Recommended pre-open design

| Priority | Exact location | Exact values and behaviour |
|---|---|---|
| P0 | **Normal stock quote header** | Display `Indicative Open` as the primary live price only while the auction is live. Pair it with `₹ / % vs previous close`, `Indicative Executable Qty`, and `Not final — auction in progress`. When the exchange confirms the match, change the label to `Opening Price confirmed`. |
| P0 | **Market-depth drawer** | Add a `Pre-open` state above the normal depth with `Total Buy Qty`, `Total Sell Qty`, `Indicative Executable Qty`, and the best bids/offers and quantities. Show `No price discovered` explicitly when applicable; do not silently carry the previous close as if it were a live open. |
| P0 | **Order ticket / AMO review** | For an AMO or pre-open order, show: `Your limit`, `Current IEP`, `Session phase`, and `You may not be filled at the displayed IEP`. When changes are no longer permitted, the ticket must state that clearly. This directly addresses the AMO-price confusion. |
| P1 | **Pre-open scanner** | A single screen ranked by `% change vs previous close`, with filters for `high executable quantity`, `buy-heavy / sell-heavy`, and eligible segment. Keep it separate from the regular live scanner because the values are auction indications, not executed LTPs. |
| P1 | **Chart and day-open explanation** | Place an `Auction open` marker on the chart and explain that the first 1-minute candle can begin with a later continuous-market tick. This prevents an apparent “wrong opening price” complaint. |
| P2 | **IPO listing mode** | For IPO/special pre-open sessions, reuse the same surface but show the separate listing-session timings and issue price. Do not merge it with ordinary pre-open without the additional label. |

## Product conclusion

The minimum credible implementation is not merely an educational CAS page. It is a **session-aware price surface**: one clear value at the quote level, enough auction context in market depth to understand it, and an all-market scanner for users monitoring more than one name. Pre-open should use the same interaction model but explicitly distinguish an indicative opening price from a confirmed open and from the first post-open tick.
