# Reddit Product Insights Publisher

This private repository collects selected public Reddit discussions once per day, removes direct usernames, packages immutable daily dumps, validates checksums, and publishes the result for the insights agent.

## Daily operation

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -e .
.\.venv\Scripts\insights-publisher daily --mode auto --push
```

`auto` uses the official Reddit API when credentials are configured and falls back to public Reddit JSON otherwise. It never bypasses authentication, private communities, or rate limits. To package an existing scraper result:

```powershell
.\.venv\Scripts\insights-publisher package --input C:\path\all_results.json --date 2026-06-22
.\.venv\Scripts\insights-publisher publish --push
```

## Repository contract

- `daily-dumps/YYYY-MM-DD/`: immutable compressed posts/comments, summary, checksum manifest
- `manifests/all_dumps.json`: small index checked by the lead agent
- `product-catalog/current.json`: versioned Nubra capability and gap catalog
- `schemas/`: machine-readable contracts
- `config/channels.json`: approved public communities and collection limits

No Slack integration is included. Keep the GitHub repository private and follow Reddit's current developer/data terms.
