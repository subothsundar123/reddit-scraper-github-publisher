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

Retail feature discovery is maintained centrally in `config/retail_feature_keywords.json`. The daily collector:

- pins five broad Nubra brand searches;
- rotates targeted searches across every retail feature bucket;
- uses round-robin selection so one large keyword bucket cannot crowd out the others;
- classifies collected text by Nubra feature ID, trader persona and intent;
- filters the broad `Nubra` query to trading/market context to avoid unrelated place-name results.

Reddit API collection also runs the targeted searches in `config/channels.json` in addition to the configured subreddit listings. The public fallback attempts the same public search endpoints but may be unavailable when Reddit returns 403/429.

Marketing SEO keyword intelligence lives in:

```text
marketing-keywords/current.json
marketing-keywords/manifest.json
```

This catalog is derived from the Nubra priority keyword workbook and keeps a compact, high-signal subset:

- priority competitor page clusters
- priority SEO keywords
- option-chain keyword list
- programmatic page ideas
- compact retail/API search seeds

YouTube collection automatically adds the compact SEO seed keywords from this catalog, so marketing priority terms also influence daily public-signal discovery without sending the full keyword universe into every collection run.

## Daily automation

GitHub Actions runs the publisher every day at **02:00 Asia/Kolkata** using `.github/workflows/daily-collection.yml`.

For YouTube to be included in the shared dump, add this repository secret:

```text
YOUTUBE_API_KEY
```

Path in GitHub:

```text
Repository → Settings → Secrets and variables → Actions → New repository secret
```

Once the secret is present, the scheduled job collects:

- Reddit posts/comments
- GitHub public issues/PR signals
- Hacker News public search signals
- broker/API public docs
- YouTube text signals split into retail and API/algo partitions

The daily output is still written to:

```text
daily-dumps/YYYY-MM-DD/
```

and indexed in:

```text
manifests/all_dumps.json
```

Connector users receive the new YouTube data automatically after their connector refreshes or runs `/update-insights-data`.

To package an existing scraper result:

```powershell
.\.venv\Scripts\insights-publisher package --input C:\path\all_results.json --signals .\staging\public_signals_2026-06-28.jsonl --date 2026-06-28
.\.venv\Scripts\insights-publisher publish --push
```

## Manual research enrichment

When the operator says:

```text
dump todays social media data
```

the intended workflow is:

1. Run the scripted daily collectors.
2. Do public manual web/social research using `manual-research/daily-research-prompt.md`.
3. Save findings as JSONL:

```text
staging/manual_research_YYYY-MM-DD.jsonl
```

4. Merge and push:

```powershell
.\.venv\Scripts\insights-publisher add-manual-research --date YYYY-MM-DD --input .\staging\manual_research_YYYY-MM-DD.jsonl --push
```

The merge command appends manual research to `daily-dumps/YYYY-MM-DD/signals.jsonl.gz`, rebuilds the summary, manifest and checksums, then validates and publishes when `--push` is used.

Manual research files and templates live in:

```text
manual-research/
```

## Repository contract

- `daily-dumps/YYYY-MM-DD/`: immutable compressed posts/comments/signals, summary, checksum manifest
- `manifests/all_dumps.json`: small index checked by the lead agent
- `product-catalog/current.json`: versioned Nubra capability and gap catalog
- `marketing-keywords/current.json`: SEO/content keyword intelligence
- `manual-research/`: repeatable manual enrichment runbook and templates
- `schemas/`: machine-readable contracts
- `config/channels.json`: approved public communities and collection limits

No Slack integration is included. Follow Reddit, GitHub and other source terms/rate limits.

Collection can run through the included GitHub Actions schedule or locally through `scripts/install_daily_task.ps1`. The GitHub workflow uses API secrets when present and otherwise uses the public JSON collector.
