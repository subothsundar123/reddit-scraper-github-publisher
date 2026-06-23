from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKBOOK_DUMP = pathlib.Path(r"C:\Users\suboth sundar\Desktop\Nubra_API_Full_context - Copy (2)\tmp\reddit_delivery_build\workbook_dump.json")


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def rows(sheet: dict) -> list[list]:
    return sheet.get("values") or []


raw = json.loads(WORKBOOK_DUMP.read_text(encoding="utf-8"))
by_name = {s["name"]: s for s in raw["sheets"]}
features = []

for index, row in enumerate(rows(by_name["what we have"])[2:], start=3):
    if not row or not row[1]:
        continue
    category, area, capability, notes = (list(row) + [None] * 4)[:4]
    text = f"{capability or ''} {notes or ''}".lower()
    status = "upcoming" if "upcoming sdk" in text else "available"
    features.append({
        "id": "nubra-" + slug(str(area)), "name": area, "category": category,
        "status": status, "availability": "public" if status == "available" else "announced/upcoming",
        "surfaces": ["API/SDK"], "capability": capability, "notes": notes,
        "aliases": sorted(set(filter(None, [area, capability]))),
        "source": {"type": "workbook", "file": "Nubra API data (1).xlsx", "sheet": "what we have", "row": index},
    })

for index, row in enumerate(rows(by_name["what can be added"])[2:], start=3):
    if not row or not row[1]:
        continue
    category, name, why, benefit, priority = (list(row) + [None] * 5)[:5]
    features.append({
        "id": "gap-" + slug(str(name)), "name": name, "category": category,
        "status": "not_available", "availability": "proposed",
        "surfaces": [], "capability": None, "notes": why, "user_benefit": benefit,
        "priority": str(priority).lower() if priority else None, "aliases": [name],
        "source": {"type": "workbook", "file": "Nubra API data (1).xlsx", "sheet": "what can be added", "row": index},
    })

supplements = [
    ("Nubra UAT", "Paper/forward testing sandbox", "available", "public", ["UAT", "API/SDK"], ["paper trading", "sandbox", "forward testing"]),
    ("Automated TOTP login", "Automated login flow using TOTP", "available", "public", ["API/SDK"], ["TOTP", "automated login"]),
    ("Primary and secondary static IP", "Primary/secondary IP support for automated trading", "available", "public", ["API/SDK"], ["static IP", "secondary IP", "IP whitelisting"]),
    ("Multi-session support", "Multiple concurrent API sessions", "available", "public", ["API/SDK"], ["multi session", "sessions"]),
    ("NubraOSS backtesting engine", "Open-source backtesting capability", "available", "open-source", ["NubraOSS"], ["backtest", "backtesting engine"]),
    ("OMS V3 advanced execution", "Multi-leg execution, targets, stop loss, trailing stop loss and timed execution", "internal_unverified", "internal/confirm before public claim", ["OMS V3"], ["multi-leg", "trailing stop", "timed execution"]),
    ("Nubra MCP", "AI/MCP access to Nubra knowledge and capabilities", "partial", "internal/early", ["MCP"], ["AI integration", "Claude", "MCP server"]),
    ("News API", "Market news data usable directly and by MCP", "internal_unverified", "internal/not publicly exposed", ["Internal API"], ["market news", "news feed"]),
    ("Developer AI support assistant", "Documentation assistant for developer questions", "available", "public", ["Documentation"], ["AI chatbot", "support chatbot"]),
    ("Public WebSocket health dashboard", "Public status and reliability dashboard for realtime streams", "not_available", "proposed", [], ["status page", "websocket dashboard", "uptime"]),
    ("Historical coverage directory", "Shows earliest available date by symbol, instrument and interval with a requirement box", "not_available", "proposed", [], ["data availability", "historical range", "suggestion box"]),
    ("Static-IP update API", "Expose the existing static-IP update capability as an API endpoint", "not_available", "proposed", [], ["update IP endpoint", "IP API"]),
    ("Advanced trader analytics", "P&L and order-history analytics built over stored order data", "not_available", "proposed", [], ["PnL analytics", "order history analytics"]),
    ("Visual strategy builder", "No-code condition, risk and execution workflow", "not_available", "proposed", [], ["strategy builder", "no-code algo"]),
]
for name, capability, status, availability, surfaces, aliases in supplements:
    features.append({
        "id": ("nubra-" if status in {"available", "partial", "upcoming", "internal_unverified"} else "gap-") + slug(name),
        "name": name, "category": "Supplemental product context", "status": status,
        "availability": availability, "surfaces": surfaces, "capability": capability,
        "notes": "Confirmed in project context; internal/unverified items must not be presented as public without validation.",
        "aliases": aliases + [name], "source": {"type": "project_context", "label": "approved product-insights discussions"},
    })

# De-duplicate exact IDs while preserving the richer, later supplemental entry.
dedup = {item["id"]: item for item in features}
catalog = {
    "catalog_version": "1.0.0",
    "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "status_definitions": {
        "available": "Available now on the stated surface",
        "upcoming": "Documented as upcoming; do not call generally available",
        "partial": "Some capability exists but scope/access needs qualification",
        "internal_unverified": "Known from internal context; requires owner confirmation before external claims",
        "not_available": "Gap or proposed capability",
    },
    "features": sorted(dedup.values(), key=lambda x: (str(x.get("category")), str(x.get("name")))),
}
out = ROOT / "product-catalog"
(out / "history").mkdir(parents=True, exist_ok=True)
text = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
(out / "current.json").write_bytes(text.encode("utf-8"))
(out / "history" / "1.0.0.json").write_bytes(text.encode("utf-8"))
sha = hashlib.sha256((out / "current.json").read_bytes()).hexdigest()
(out / "manifest.json").write_bytes((json.dumps({
    "current_version": "1.0.0", "path": "product-catalog/current.json", "sha256": sha,
    "feature_count": len(catalog["features"]), "updated_at": catalog["updated_at"],
}, indent=2) + "\n").encode("utf-8"))
print(f"Wrote {len(catalog['features'])} catalog entries")
