# Reddit Product Insights Publisher

This repository collects selected public Reddit discussions once per day, removes direct usernames, packages immutable daily dumps, validates checksums, and publishes the result for the insights agent.

It also supports credential-free public signal collection from:

- GitHub public issues and pull requests
- Hacker News public search results
- Broker/API public documentation pages

It can also collect text-only YouTube signals when a `YOUTUBE_API_KEY` is configured:

- video title and description
- channel name and video URL
- publish date, views, likes and comment count
- views/day, comments/day and engagement rate
- top/recent comments
- comment-level feature requests, pain points, questions and competitor mentions
- separate retail and API/algo partitions, including Nubra-specific searches

## Daily operation

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -e .
.\.venv\Scripts\insights-publisher daily --mode auto --push
```

`auto` uses the official Reddit API when credentials are configured and falls back to public Reddit JSON otherwise. The daily command also creates `signals.jsonl.gz` from public GitHub/Hacker News/broker-doc sources unless `--skip-signals` is passed. It never bypasses authentication, private communities, or rate limits.

To collect only public multi-channel signals:

```powershell
.\.venv\Scripts\insights-publisher collect-signals --date 2026-06-28
```

To collect only YouTube text signals:

```powershell
$env:YOUTUBE_API_KEY="your-youtube-data-api-key"
.\.venv\Scripts\insights-publisher collect-youtube --date 2026-06-30
```

YouTube collection is intentionally text-only. It does not download videos, images or thumbnails. Keywords live in `config/youtube_keywords.json` and are split into `retail` and `api` partitions so downstream analysis can keep retail app demand separate from API/algo/developer demand.

To package an existing scraper result:

```powershell
.\.venv\Scripts\insights-publisher package --input C:\path\all_results.json --signals .\staging\public_signals_2026-06-28.jsonl --date 2026-06-28
.\.venv\Scripts\insights-publisher publish --push
```

## Repository contract

- `daily-dumps/YYYY-MM-DD/`: immutable compressed posts/comments/signals, summary, checksum manifest
- `manifests/all_dumps.json`: small index checked by the lead agent
- `product-catalog/current.json`: versioned Nubra capability and gap catalog
- `schemas/`: machine-readable contracts
- `config/channels.json`: approved public communities and collection limits

No Slack integration is included. Follow Reddit, GitHub and other source terms/rate limits.

Collection can run through the included GitHub Actions schedule or locally through `scripts/install_daily_task.ps1`. The GitHub workflow uses API secrets when present and otherwise uses the public JSON collector.
