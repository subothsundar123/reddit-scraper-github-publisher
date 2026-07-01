from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "product-catalog"
CURRENT_PATH = CATALOG_DIR / "current.json"
RETAIL_PATH = CATALOG_DIR / "retail-upcoming-features.json"
RETAIL_MD_PATH = CATALOG_DIR / "retail-upcoming-features.md"
MANIFEST_PATH = CATALOG_DIR / "manifest.json"
VERSION = "1.1.0"

SOURCE = {
    "type": "user_input",
    "file": "conversation_2026-07-01",
    "notes": "User-confirmed Nubra retail feature input, cleaned and deduplicated on 2026-07-01.",
}


def feature(
    feature_id: str,
    name: str,
    category: str,
    surfaces: list[str],
    capability: str,
    user_benefit: str,
    aliases: list[str],
    priority: str = "high",
) -> dict:
    return {
        "id": feature_id,
        "category": category,
        "name": name,
        "status": "upcoming",
        "availability": "new_build_evidence",
        "surfaces": surfaces,
        "capability": capability,
        "notes": "Treat as upcoming/new-build evidence until public rollout is confirmed.",
        "user_benefit": user_benefit,
        "priority": priority,
        "aliases": aliases,
        "source": SOURCE,
    }


NEW_FEATURES = [
    feature(
        "nubra-expanded-auto-refresh-watchlists",
        "250-instrument watchlists with auto-refresh",
        "Retail App / Watchlist",
        ["Mobile App", "Watchlist"],
        "Support up to 250 stock and derivatives instruments in a watchlist, with automatic quote refresh.",
        "Lets active traders monitor a broader universe without manually refreshing prices or splitting instruments across many lists.",
        ["250 stocks watchlist", "250 instrument watchlist", "large watchlist", "auto refresh watchlist", "live watchlist refresh"],
    ),
    feature(
        "nubra-oms-order-presets",
        "Saved OMS order presets",
        "Retail App / Order Management",
        ["Mobile App", "OMS", "Order entry"],
        "Apply saved presets in the order management system for frequently used order, quantity, product and risk settings.",
        "Reduces repetitive order entry and makes fast execution more consistent.",
        ["apply presets on OMS", "OMS presets", "order presets", "saved order template", "Apply Preset"],
    ),
    feature(
        "nubra-nse-best-fill-price",
        "Best-fill-price execution on NSE",
        "Retail App / Execution",
        ["Mobile App", "NSE order execution"],
        "Seek the best available fill price on NSE within the user's order instructions and applicable exchange controls.",
        "Improves execution confidence and reduces avoidable price impact for active traders.",
        ["best fill price in NSE", "best price execution", "NSE best fill", "price improvement"],
    ),
    feature(
        "nubra-instant-fund-movement",
        "Instant fund addition and withdrawal",
        "Retail App / Funds",
        ["Mobile App", "Funds"],
        "Support instant withdrawals and instant fund additions of up to ₹5 lakh, subject to banking, risk and regulatory limits.",
        "Reduces waiting time before trading and makes unused capital easier to access.",
        ["instant withdrawal", "instant payout", "instant fund addition", "add funds up to 5 lakh", "₹5 lakh fund addition"],
    ),
    feature(
        "nubra-ai-query-scans",
        "Natural-language AI-generated scans",
        "Retail App / Discovery & Scanners",
        ["Mobile App", "Explore", "Ask AI", "Scanners"],
        "Convert a trader's plain-language query into a market scan with visible conditions and editable filters.",
        "Makes stock and derivatives discovery accessible without requiring users to construct complex scanner logic manually.",
        ["query based AI generated scans", "AI scanner", "natural language scanner", "prompt based screener", "AI generated scans"],
    ),
    feature(
        "nubra-flexible-brokerage",
        "Flexible brokerage plan",
        "Retail App / Pricing",
        ["Mobile App", "Account", "Brokerage plan"],
        "Offer a flexible brokerage plan that can fit different trading personas and usage patterns.",
        "Lets investors, option traders and high-frequency users choose a pricing structure aligned with how they trade.",
        ["flexible brokerage", "custom brokerage plan", "persona based brokerage", "Flexible Brokerage Plan"],
    ),
    feature(
        "nubra-chart-analyser",
        "Chart analyser",
        "Retail App / Charts & Analytics",
        ["Mobile App", "Charts", "Ask AI"],
        "Analyse a chart and surface technical structure, indicators, levels and possible trading observations in context.",
        "Helps users interpret charts faster while keeping the underlying signals visible for verification.",
        ["chart analyser", "chart analyzer", "AI chart analysis", "technical chart insights"],
    ),
    feature(
        "nubra-strategy-level-portfolios",
        "Strategy-level portfolios",
        "Retail App / Portfolio & Strategies",
        ["Mobile App", "Portfolio", "Strategies"],
        "Group positions and performance by strategy rather than showing only an account-level collection of individual legs.",
        "Allows multi-leg traders to understand capital, exposure and P&L at the level at which the trade was planned.",
        ["strategy lvl portfolios", "strategy level portfolio", "portfolio by strategy", "multi-leg portfolio grouping"],
    ),
    feature(
        "nubra-strategy-level-risk-controls",
        "Strategy-level stop-loss and target controls",
        "Retail App / Strategies & Risk",
        ["Mobile App", "Strategies", "Portfolio", "Order entry"],
        "Configure and manage strategy-level SL/TP using P&L values or risk-reward rules across all linked legs.",
        "Protects the intended strategy outcome without forcing traders to manage each leg independently.",
        ["P&L based SL TP", "pnl based stop loss", "risk reward SL TP", "strategy lvl SL TP", "strategy level stop loss", "strategy target"],
    ),
    feature(
        "nubra-amount-margin-quantity-sizing",
        "Quantity sizing by amount or margin",
        "Retail App / Order Entry",
        ["Mobile App", "Order entry", "Strategies"],
        "Calculate and select order quantity from a chosen investment amount or available margin.",
        "Makes position sizing faster and reduces manual quantity and lot calculations.",
        ["choose qty based on amount", "quantity based on margin", "amount based quantity", "margin based sizing", "position sizing"],
    ),
    feature(
        "nubra-dual-iceberg-modes",
        "Two configurable iceberg order modes",
        "Retail App / Advanced Orders",
        ["Mobile App", "Order entry", "OMS"],
        "Provide two configurable iceberg execution modes for splitting and managing larger orders.",
        "Gives large-order traders more control over market impact and execution behaviour.",
        ["iceberg two modes", "two iceberg modes", "iceberg execution mode", "advanced iceberg order"],
    ),
    feature(
        "nubra-no-app-price-restriction",
        "Removal of app-level price restrictions",
        "Retail App / Order Entry",
        ["Mobile App", "Order entry"],
        "Avoid unnecessary app-level price restrictions while continuing to enforce exchange, regulatory and risk limits.",
        "Prevents valid orders from being blocked by overly narrow application controls.",
        ["no price restriction", "remove price restriction", "order price flexibility", "app price limits"],
        "medium",
    ),
    feature(
        "nubra-technical-option-chain-alerts",
        "Technical and option-chain alerts",
        "Retail App / Alerts",
        ["Mobile App", "Alerts", "Charts", "Option chain"],
        "Create alerts from technical conditions and option-chain signals such as OI, volume, IV, Greeks, PCR, price and strike activity.",
        "Lets users monitor relevant market changes without continuously watching charts or the option chain.",
        ["technical alerts", "indicator alerts", "option chain alerts", "OI alert", "IV alert", "strike alert"],
    ),
    feature(
        "nubra-strategy-time-series-chart",
        "Strategy-level time-series charts across instruments",
        "Retail App / Strategies & Analytics",
        ["Mobile App", "Strategies", "Portfolio", "Charts"],
        "Plot a strategy as a time series while combining its linked stock, futures and options instruments.",
        "Shows how a complete strategy evolves over time instead of presenting disconnected leg-level charts.",
        ["strategy level time series", "mixed stock options chart", "strategy chart", "multi-instrument time series"],
    ),
    feature(
        "nubra-gtt-amo-orders",
        "GTT and AMO order support",
        "Retail App / Advanced Orders",
        ["Mobile App", "Order entry", "Orders"],
        "Support Good Till Triggered and After Market Orders in the retail order workflow.",
        "Allows users to prepare orders outside market hours and maintain trigger-based trade instructions.",
        ["GTT", "Good Till Triggered", "AMO", "After Market Order"],
    ),
    feature(
        "nubra-flexible-order-type-modification",
        "Flexible order-type modification",
        "Retail App / Order Management",
        ["Mobile App", "OMS", "Orders"],
        "Allow eligible open orders to be modified between supported order types, including conversion from iceberg to other types, subject to exchange rules.",
        "Reduces cancel-and-recreate friction when execution conditions change.",
        ["flexible order modification", "change order type", "iceberg to other order type", "convert open order"],
    ),
    feature(
        "nubra-bid-ask-on-chart",
        "Bid and ask prices on charts",
        "Retail App / Charts & Execution",
        ["Mobile App", "Charts", "Trading View"],
        "Display live bid and ask prices on the chart and connect them to the trading workflow.",
        "Helps traders judge spread and execution context without leaving the chart.",
        ["bid ask on chart", "bid and ask chart", "spread on chart", "live bid ask overlay"],
    ),
]


ENHANCEMENTS = {
    "nubra-retail-persona-modes": {
        "capability": "Persona-based broker experience for Option Sellers, Option Buyers, Investors and OI Traders, changing visible tools, defaults, layouts, guidance and workflows.",
        "aliases": ["customised broker", "customized broker", "OI trader mode", "option seller mode", "option buyer mode"],
        "notes": "User confirmed that 'customised broker' refers to the existing persona-based experience, not a separate feature.",
    },
    "nubra-option-chain-custom-filters-columns": {
        "capability": "Configurable option-chain settings, filters and saved modes including OI bars, PCR, total OI, max pain, ITM highlighting, today high/low, VWAP, premium, OI, OI buildup, volume, volume spike, IV, IV change, Greeks, bid-ask spread and OI concentration.",
        "aliases": ["save option chain filters", "saved option chain mode", "save chain layout"],
    },
    "nubra-one-click-trade-bid-ask": {
        "capability": "One-click mode with direct trade actions from bid/ask or LTP cells across option-chain strikes, with bid/ask visible in the chain.",
        "aliases": ["bid ask on option chain", "one click mode"],
    },
    "nubra-strategy-taxonomy-market-outcome-instrument": {
        "capability": "Offer 40+ pre-built strategies classified by Market View, Trader Outcome and Instrument Set. Market views include Bullish, Bearish, Sideways and Big News; outcomes include Income, Hedge, Directional, Volatility and Arbitrage; instrument sets include Stock, Future and Option.",
        "aliases": ["40+ pre-built strategies", "40 built-in strategies", "ready-made strategies"],
    },
    "nubra-scalper-tradingview-template-customisation": {
        "name": "Scalper mode and saved TradingView templates",
        "capability": "Provide a focused Scalper mode and save preferred Scalper/TradingView-style layouts and execution templates.",
        "aliases": ["scalper mode", "scalper workflow", "saved trading template"],
    },
}


def merge_unique(existing: list[str] | None, additions: list[str]) -> list[str]:
    values = list(existing or [])
    seen = {value.casefold() for value in values}
    for value in additions:
        if value.casefold() not in seen:
            values.append(value)
            seen.add(value.casefold())
    return values


def upsert(features: list[dict]) -> list[dict]:
    by_id = {item["id"]: item for item in features}
    for feature_id, changes in ENHANCEMENTS.items():
        item = by_id[feature_id]
        for key, value in changes.items():
            if key == "aliases":
                item["aliases"] = merge_unique(item.get("aliases"), value)
            elif key == "notes":
                item["notes"] = f'{item.get("notes", "").rstrip()} {value}'.strip()
            else:
                item[key] = value
    for item in NEW_FEATURES:
        by_id[item["id"]] = item
    return list(by_id.values())


def markdown(features: list[dict]) -> str:
    sections: dict[str, list[dict]] = {}
    for item in features:
        sections.setdefault(item["category"], []).append(item)
    lines = [
        "# Retail Upcoming Features",
        "",
        "Scope: retail app features only. API/SDK-only and MCP/internal connector features are excluded.",
        "",
        f"Total features: {len(features)}",
        "",
    ]
    for category, items in sections.items():
        lines.extend([f"## {category}", ""])
        for item in items:
            source = item.get("source", {})
            source_note = source.get("notes", "")
            lines.extend(
                [
                    f"### {item['name']}",
                    "",
                    f"- Status: {item['status']} / {item['availability']}",
                    f"- Surfaces: {', '.join(item.get('surfaces', []))}",
                    f"- Capability: {item['capability']}",
                    f"- User benefit: {item['user_benefit']}",
                    f"- Source note: {source_note}",
                    f"- Keywords: {', '.join(item.get('aliases', []))}",
                    "",
                ]
            )
    return "\n".join(lines)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    retail = json.loads(RETAIL_PATH.read_text(encoding="utf-8"))
    current = json.loads(CURRENT_PATH.read_text(encoding="utf-8"))

    retail["features"] = upsert(retail["features"])
    retail["count"] = len(retail["features"])
    retail["generated_at"] = now

    current["features"] = upsert(current["features"])
    current["catalog_version"] = VERSION
    current["updated_at"] = now

    write_json(RETAIL_PATH, retail)
    RETAIL_MD_PATH.write_text(markdown(retail["features"]), encoding="utf-8")
    write_json(CURRENT_PATH, current)
    write_json(CATALOG_DIR / "history" / f"{VERSION}.json", current)

    digest = hashlib.sha256(CURRENT_PATH.read_bytes()).hexdigest()
    manifest = {
        "current_version": VERSION,
        "path": "product-catalog/current.json",
        "sha256": digest,
        "feature_count": len(current["features"]),
        "updated_at": now,
    }
    write_json(MANIFEST_PATH, manifest)
    print(f"Retail upcoming features: {len(retail['features'])}")
    print(f"Full product catalog features: {len(current['features'])}")
    print(f"Catalog version: {VERSION}")


if __name__ == "__main__":
    main()
