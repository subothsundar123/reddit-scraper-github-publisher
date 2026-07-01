# Manual Research Enrichment

This folder defines the daily manual-research workflow used when the operator says:

```text
dump todays social media data
```

The intended daily flow is:

1. Run the scripted collectors.
2. Do public manual web research for the day.
3. Save the findings as JSONL in `staging/manual_research_YYYY-MM-DD.jsonl`.
4. Merge those findings into `daily-dumps/YYYY-MM-DD/signals.jsonl.gz`.
5. Validate and push the dump.

## Command

```powershell
.\.venv\Scripts\insights-publisher add-manual-research --date 2026-07-01 --input .\staging\manual_research_2026-07-01.jsonl --push
```

## Manual research rules

- Use only public sources.
- Do not bypass logins, CAPTCHAs, private groups or rate limits.
- Store concise summaries, public URLs and the product signal.
- Hash or omit personal identifiers.
- Mark the evidence quality and source method clearly.
- Separate retail and API/algo signals using `segment`.

## Recommended source methods

```text
manual_retail_research
manual_api_research
manual_competitor_research
manual_seo_research
manual_social_indexed_search
manual_twitter_indexed_search
manual_web_research
```

## Required JSONL fields

Minimum:

```json
{"title":"...", "body":"...", "url":"...", "source":"manual_web_research", "channel":"...", "segment":"retail"}
```

The merge command will fill missing `id`, `tags`, `competitors`, `source_method` and `evidence_quality`.
