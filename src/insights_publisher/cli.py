from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time
from collections import Counter
from typing import Any, Iterable

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def _sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _anon(value: Any) -> str | None:
    if not value or str(value).lower() in {"[deleted]", "[removed]", "none"}:
        return None
    return "u_" + hashlib.sha256(str(value).encode()).hexdigest()[:16]


def _gzip_jsonl(path: pathlib.Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            for row in rows:
                gz.write((json.dumps(row, ensure_ascii=False) + "\n").encode("utf-8"))
                count += 1
    return count


TOPIC_TAGS = {
    "websocket": ["websocket", "socket", "streaming", "reconnect", "feed"],
    "historical_data": ["historical", "candle", "ohlc", "history", "archive"],
    "backtesting": ["backtest", "backtesting", "strategy test"],
    "order_execution": ["order", "execution", "fill", "oms", "basket", "gtt"],
    "options_analytics": ["option", "greeks", "payoff", "iv", "open interest", "option chain"],
    "option_chain": ["option chain", "pcr", "max pain", "oi buildup", "oi concentration"],
    "strategy_builder": ["strategy builder", "payoff", "breakeven", "probability of profit", "strategy appstore"],
    "trader_personas": ["option buyer", "option seller", "oi trader", "investor mode", "scalper"],
    "developer_onboarding": ["docs", "documentation", "quickstart", "sdk", "sample", "auth", "login"],
    "market_data": ["market data", "quote", "tick", "ltp", "depth"],
    "automation": ["algo", "automation", "strategy", "bot"],
    "pricing_margin": ["margin", "brokerage", "charges", "pricing"],
    "mcp_ai": ["mcp", "ai", "agent", "claude"],
}


COMPETITOR_ALIASES = {
    "Nubra": ["nubra", "zanskar"],
    "Zerodha": ["zerodha", "kite connect", "kite.trade"],
    "Upstox": ["upstox"],
    "Dhan": ["dhan", "dhanhq"],
    "Fyers": ["fyers"],
    "Angel One": ["angel one", "smartapi", "smart api"],
    "ICICI Direct": ["icici", "breeze"],
    "Shoonya": ["shoonya", "finvasia"],
    "Alice Blue": ["alice blue", "ant api"],
}


def _tags(text: str) -> list[str]:
    lower = text.lower()
    return [tag for tag, keys in TOPIC_TAGS.items() if any(key in lower for key in keys)]


def _competitors(text: str) -> list[str]:
    lower = text.lower()
    return [name for name, keys in COMPETITOR_ALIASES.items() if any(key in lower for key in keys)]


def _segment(text: str) -> str:
    lower = text.lower()
    api_terms = ["api", "sdk", "websocket", "github", "python", "developer", "endpoint", "algo", "automation"]
    return "api_algo" if any(term in lower for term in api_terms) else "retail"


def _signal_id(source: str, external_id: Any, url: str, title: str) -> str:
    raw = f"{source}:{external_id or ''}:{url}:{title}"
    return source[:3] + "_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _signal(
    *,
    source: str,
    channel: str,
    item_type: str,
    collected_on: str,
    title: str,
    body: str,
    url: str,
    external_id: Any = None,
    created_at: Any = None,
    author: Any = None,
    engagement: dict[str, Any] | None = None,
    evidence_quality: str = "public_api",
    source_method: str = "public_signal_collector",
) -> dict[str, Any]:
    text = f"{title} {body}"
    return {
        "id": _signal_id(source, external_id, url, title),
        "source": source,
        "channel": channel,
        "item_type": item_type,
        "external_id": str(external_id) if external_id is not None else None,
        "collected_on": collected_on,
        "created_at": created_at,
        "title": title or "",
        "body": body or "",
        "url": url or "",
        "author_hash": _anon(author),
        "engagement": engagement or {},
        "tags": _tags(text),
        "segment": _segment(text),
        "competitors": _competitors(text),
        "evidence_quality": evidence_quality,
        "source_method": source_method,
    }


def _clean_html_text(value: str, limit: int = 900) -> str:
    value = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", value or "")
    value = re.sub(r"(?s)<[^>]+>", " ", value)
    value = re.sub(r"&nbsp;|&#160;", " ", value)
    value = re.sub(r"&amp;", "&", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit]


def _html_title(html: str, fallback: str) -> str:
    match = re.search(r"(?is)<title[^>]*>(.*?)</title>", html or "")
    return _clean_html_text(match.group(1), 160) if match else fallback


def _normalize_comment(comment: Any, post_id: str, index: int) -> dict[str, Any]:
    if isinstance(comment, dict):
        body = comment.get("body") or ""
        score = int(comment.get("score") or 0)
        author = comment.get("author")
        created = comment.get("created_utc") or comment.get("timestamp")
        cid = comment.get("id")
    else:
        body, score, author, created, cid = str(comment), 0, None, None, None
    cid = cid or hashlib.sha256(f"{post_id}:{index}:{body}".encode()).hexdigest()[:16]
    return {
        "id": str(cid), "post_id": post_id, "body": body, "score": score,
        "author_hash": _anon(author), "created_utc": created,
    }


def _load_signals(path: pathlib.Path | None) -> list[dict[str, Any]]:
    if not path or not path.exists():
        return []
    if path.suffix == ".gz":
        opener = gzip.open
        mode = "rt"
    else:
        opener = open
        mode = "r"
    with opener(path, mode, encoding="utf-8") as f:  # type: ignore[arg-type]
        return [json.loads(line) for line in f if line.strip()]


def package_dump(
    input_path: pathlib.Path,
    collection_date: str,
    source: str = "reddit",
    signals_path: pathlib.Path | None = None,
) -> pathlib.Path:
    payload = _json(input_path)
    if isinstance(payload, list):
        grouped = {"unknown": payload}
    elif isinstance(payload, dict):
        grouped = payload
    else:
        raise ValueError("Input must be a JSON object keyed by subreddit or a list of posts")

    seen: set[str] = set()
    posts: list[dict[str, Any]] = []
    comments: list[dict[str, Any]] = []
    subreddit_counts: dict[str, int] = {}
    for subreddit, values in grouped.items():
        if not isinstance(values, list):
            continue
        for raw in values:
            if not isinstance(raw, dict):
                continue
            post_id = str(raw.get("id") or hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()[:16])
            if post_id in seen:
                continue
            seen.add(post_id)
            sub = str(raw.get("subreddit") or subreddit)
            row = {
                "id": post_id,
                "subreddit": sub,
                "sort_type": raw.get("sort_type"),
                "title": raw.get("title") or "",
                "body": raw.get("selftext") or raw.get("body") or "",
                "flair": raw.get("flair"),
                "post_type": raw.get("post_type"),
                "score": int(raw.get("score") or 0),
                "num_comments": int(raw.get("num_comments") or len(raw.get("comments") or [])),
                "created_utc": raw.get("created_utc") or raw.get("timestamp"),
                "permalink": raw.get("permalink"),
                "url": raw.get("url"),
                "author_hash": _anon(raw.get("author")),
                "collected_on": collection_date,
                "source_method": raw.get("source_method") or "reddit_collector",
                "research_query": raw.get("research_query"),
                "evidence_quality": raw.get("evidence_quality") or "direct_collection",
            }
            posts.append(row)
            subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
            for idx, comment in enumerate(raw.get("comments") or []):
                comments.append(_normalize_comment(comment, post_id, idx))

    out = ROOT / "daily-dumps" / collection_date
    out.mkdir(parents=True, exist_ok=True)
    post_path, comment_path = out / "posts.jsonl.gz", out / "comments.jsonl.gz"
    _gzip_jsonl(post_path, posts)
    _gzip_jsonl(comment_path, comments)
    signals = _load_signals(signals_path)
    signal_path = out / "signals.jsonl.gz"
    signal_count = _gzip_jsonl(signal_path, signals) if signals else 0
    summary = {
        "collection_date": collection_date,
        "source": source,
        "posts": len(posts),
        "comments": len(comments),
        "signals": signal_count,
        "subreddits": subreddit_counts,
        "source_methods": dict(Counter(p.get("source_method") or "unknown" for p in posts)),
        "signal_sources": dict(Counter(s.get("source") or "unknown" for s in signals)),
        "signal_channels": dict(Counter(s.get("channel") or "unknown" for s in signals)),
        "evidence_quality": dict(Counter(p.get("evidence_quality") or "unknown" for p in posts)),
        "engagement": {
            "post_score_sum": sum(p["score"] for p in posts),
            "comment_score_sum": sum(c["score"] for c in comments),
            "reported_comment_sum": sum(p["num_comments"] for p in posts),
        },
        "privacy": "Public text retained for analysis; Reddit usernames replaced with stable one-way hashes.",
    }
    _write_json(out / "summary.json", summary)
    files = []
    output_files = [post_path, comment_path, out / "summary.json"]
    if signal_count:
        output_files.append(signal_path)
    for p in output_files:
        files.append({"path": p.relative_to(ROOT).as_posix(), "sha256": _sha(p), "bytes": p.stat().st_size})
    manifest = {
        "schema_version": "1.0", "collection_date": collection_date,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(), "files": files,
    }
    _write_json(out / "manifest.json", manifest)
    manifest_path = ROOT / "manifests" / "all_dumps.json"
    index = _json(manifest_path) if manifest_path.exists() else {"schema_version": "1.0", "dumps": []}
    index["dumps"] = [d for d in index["dumps"] if d.get("collection_date") != collection_date]
    index["dumps"].append({
        "collection_date": collection_date,
        "manifest": (out / "manifest.json").relative_to(ROOT).as_posix(),
        "posts": len(posts), "comments": len(comments), "signals": signal_count,
    })
    index["dumps"].sort(key=lambda d: d["collection_date"])
    index["updated_at"] = manifest["generated_at"]
    _write_json(manifest_path, index)
    return out


def collect_github_signals(cfg: dict[str, Any], collection_date: str) -> list[dict[str, Any]]:
    import requests
    if not cfg.get("enabled", True):
        return []
    session = requests.Session()
    session.headers["User-Agent"] = os.getenv("GITHUB_USER_AGENT", "product-insights-public-signal-collector/1.0")
    token = os.getenv("GITHUB_TOKEN")
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    rows: dict[str, dict[str, Any]] = {}
    limit = min(int(cfg.get("max_results_per_query", 25)), 50)
    for query in cfg.get("queries", []):
        params = {"q": query, "sort": "updated", "order": "desc", "per_page": limit}
        response = session.get("https://api.github.com/search/issues", params=params, timeout=30)
        if response.status_code in {403, 429}:
            break
        response.raise_for_status()
        for item in response.json().get("items", []):
            title = item.get("title") or ""
            body = item.get("body") or ""
            row = _signal(
                source="github",
                channel=item.get("repository_url", "").rsplit("/", 1)[-1] or "github_search",
                item_type="pull_request" if "pull_request" in item else "issue",
                collected_on=collection_date,
                external_id=item.get("id"),
                created_at=item.get("created_at"),
                author=(item.get("user") or {}).get("login"),
                title=title,
                body=body[:1500],
                url=item.get("html_url") or "",
                engagement={
                    "comments": item.get("comments") or 0,
                    "reactions": (item.get("reactions") or {}).get("total_count") or 0,
                    "score": item.get("score") or 0,
                },
                evidence_quality="public_github_api",
                source_method="github_search_api",
            )
            rows[row["id"]] = row
        time.sleep(1.0)
    return list(rows.values())


def collect_hacker_news_signals(cfg: dict[str, Any], collection_date: str) -> list[dict[str, Any]]:
    import requests
    if not cfg.get("enabled", True):
        return []
    rows: dict[str, dict[str, Any]] = {}
    limit = min(int(cfg.get("max_results_per_query", 20)), 50)
    session = requests.Session()
    session.headers["User-Agent"] = "product-insights-public-signal-collector/1.0"
    for query in cfg.get("queries", []):
        response = session.get(
            "https://hn.algolia.com/api/v1/search",
            params={"query": query, "tags": "story", "hitsPerPage": limit},
            timeout=30,
        )
        response.raise_for_status()
        for item in response.json().get("hits", []):
            title = item.get("title") or item.get("story_title") or ""
            body = item.get("comment_text") or ""
            object_id = item.get("objectID")
            row = _signal(
                source="hacker_news",
                channel=query,
                item_type="story",
                collected_on=collection_date,
                external_id=object_id,
                created_at=item.get("created_at"),
                author=item.get("author"),
                title=title,
                body=body,
                url=item.get("url") or f"https://news.ycombinator.com/item?id={object_id}",
                engagement={"points": item.get("points") or 0, "comments": item.get("num_comments") or 0},
                evidence_quality="public_hn_api",
                source_method="hacker_news_algolia_api",
            )
            rows[row["id"]] = row
        time.sleep(0.5)
    return list(rows.values())


def collect_broker_doc_signals(cfg: dict[str, Any], collection_date: str) -> list[dict[str, Any]]:
    import requests
    if not cfg.get("enabled", True):
        return []
    session = requests.Session()
    session.headers["User-Agent"] = "product-insights-public-signal-collector/1.0"
    rows: list[dict[str, Any]] = []
    for page in cfg.get("pages", []):
        name, url = page.get("name") or "broker_docs", page.get("url") or ""
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            html = response.text
            title = _html_title(html, name)
            body = _clean_html_text(html, 1400)
            rows.append(_signal(
                source="broker_docs",
                channel=name,
                item_type="docs_page",
                collected_on=collection_date,
                external_id=url,
                created_at=response.headers.get("last-modified"),
                title=title,
                body=body,
                url=url,
                engagement={},
                evidence_quality="public_docs_page",
                source_method="broker_docs_page_fetch",
            ))
        except Exception as exc:
            rows.append(_signal(
                source="broker_docs",
                channel=name,
                item_type="fetch_error",
                collected_on=collection_date,
                external_id=url,
                title=f"{name} fetch issue",
                body=f"Could not fetch public docs page during collection: {type(exc).__name__}",
                url=url,
                engagement={},
                evidence_quality="collection_error",
                source_method="broker_docs_page_fetch",
            ))
        time.sleep(0.5)
    return rows


def _int(value: Any) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def _published_after(days: int | None) -> str | None:
    if not days:
        return None
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=max(1, int(days)))
    return since.isoformat().replace("+00:00", "Z")


def _days_since(value: str | None) -> float:
    if not value:
        return 1.0
    try:
        published = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return 1.0
    return max(1.0, (dt.datetime.now(dt.timezone.utc) - published).total_seconds() / 86400)


def _youtube_get(session: Any, api_key: str, path: str, params: dict[str, Any]) -> dict[str, Any]:
    params = {**params, "key": api_key}
    response = session.get(f"https://www.googleapis.com/youtube/v3/{path}", params=params, timeout=30)
    if response.status_code in {403, 429}:
        raise RuntimeError(f"YouTube API quota or permission issue: {response.status_code}")
    response.raise_for_status()
    return response.json()


def _flatten_youtube_keywords(cfg: dict[str, Any]) -> list[dict[str, str]]:
    limit = int(cfg.get("limits", {}).get("max_queries_per_partition", 20))
    rows: list[dict[str, str]] = []
    for partition, part_cfg in (cfg.get("partitions") or {}).items():
        segment = part_cfg.get("segment") or ("api_algo" if partition == "api" else "retail")
        count = 0
        for bucket, keywords in (part_cfg.get("keyword_buckets") or {}).items():
            for keyword in keywords:
                if count >= limit:
                    break
                rows.append({
                    "partition": partition,
                    "segment": segment,
                    "bucket": bucket,
                    "keyword": str(keyword),
                })
                count += 1
            if count >= limit:
                break
    return rows


def _comment_signal_type(text: str) -> str:
    lower = text.lower()
    if any(term in lower for term in ("please add", "need", "want", "missing", "feature", "can you add")):
        return "feature_request"
    if any(term in lower for term in ("problem", "issue", "slow", "delay", "not working", "confusing", "difficult")):
        return "pain_point"
    if any(term in lower for term in ("zerodha", "dhan", "fyers", "sensibull", "opstra", "upstox", "angel")):
        return "competitor_comparison"
    if "?" in text or any(term in lower for term in ("how", "why", "which", "what is", "best")):
        return "question"
    return "general"


def _youtube_video_comments(
    session: Any,
    api_key: str,
    video_id: str,
    max_relevant: int,
    max_recent: int,
    pause: float,
) -> list[dict[str, Any]]:
    comments: dict[str, dict[str, Any]] = {}
    for order, limit in (("relevance", max_relevant), ("time", max_recent)):
        if limit <= 0:
            continue
        page_token = None
        while len([c for c in comments.values() if c.get("order") == order]) < limit:
            params = {
                "part": "snippet",
                "videoId": video_id,
                "maxResults": min(100, limit),
                "order": order,
                "textFormat": "plainText",
            }
            if page_token:
                params["pageToken"] = page_token
            try:
                payload = _youtube_get(session, api_key, "commentThreads", params)
            except Exception:
                break
            for item in payload.get("items", []):
                snippet = ((item.get("snippet") or {}).get("topLevelComment") or {}).get("snippet") or {}
                comment_id = ((item.get("snippet") or {}).get("topLevelComment") or {}).get("id") or item.get("id")
                text = snippet.get("textDisplay") or snippet.get("textOriginal") or ""
                if not comment_id or not text:
                    continue
                comments.setdefault(str(comment_id), {
                    "comment_id": str(comment_id),
                    "text": text[:1200],
                    "likes": _int(snippet.get("likeCount")),
                    "published_at": snippet.get("publishedAt"),
                    "updated_at": snippet.get("updatedAt"),
                    "order": order,
                    "signal_type": _comment_signal_type(text),
                    "feature_mentions": _tags(text),
                    "competitor_mentions": _competitors(text),
                })
            page_token = payload.get("nextPageToken")
            if not page_token:
                break
            time.sleep(pause)
    return sorted(comments.values(), key=lambda row: (row["likes"], row["published_at"] or ""), reverse=True)


def _youtube_comment_summary(comments: list[dict[str, Any]]) -> dict[str, Any]:
    types = Counter(comment.get("signal_type") or "general" for comment in comments)
    features = Counter(tag for comment in comments for tag in comment.get("feature_mentions", []))
    competitors = Counter(name for comment in comments for name in comment.get("competitor_mentions", []))
    recent_cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)
    recent_count = 0
    for comment in comments:
        published = comment.get("published_at")
        if not published:
            continue
        try:
            if dt.datetime.fromisoformat(published.replace("Z", "+00:00")) >= recent_cutoff:
                recent_count += 1
        except ValueError:
            pass
    return {
        "comment_signal_types": dict(types),
        "feature_mentions": dict(features.most_common(12)),
        "competitor_mentions": dict(competitors.most_common(12)),
        "recent_comment_count": recent_count,
        "question_count": types.get("question", 0),
        "feature_request_count": types.get("feature_request", 0),
        "pain_point_count": types.get("pain_point", 0),
    }


def collect_youtube_signals(config_path: pathlib.Path, output_path: pathlib.Path, collection_date: str) -> pathlib.Path:
    import requests
    cfg = _json(config_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows: dict[str, dict[str, Any]] = {}
    if not cfg.get("enabled", True):
        output_path.write_text("", encoding="utf-8")
        return output_path
    api_key = os.getenv(cfg.get("api_key_env") or "YOUTUBE_API_KEY")
    if not api_key:
        output_path.write_text("", encoding="utf-8")
        print("Skipping YouTube collection: set YOUTUBE_API_KEY to enable it.", file=sys.stderr)
        return output_path

    limits = cfg.get("limits") or {}
    max_videos = min(50, int(limits.get("max_videos_per_query", 5)))
    max_comments = int(limits.get("max_comments_per_video", 80))
    max_recent = int(limits.get("max_recent_comments_per_video", 40))
    pause = float(limits.get("request_pause_seconds", 0.15))
    published_after = _published_after(limits.get("published_after_days"))
    session = requests.Session()
    session.headers["User-Agent"] = "product-insights-youtube-agent/1.0"

    for item in _flatten_youtube_keywords(cfg):
        params: dict[str, Any] = {
            "part": "snippet",
            "type": "video",
            "q": item["keyword"],
            "maxResults": max_videos,
            "order": "relevance",
            "relevanceLanguage": "en",
            "safeSearch": "none",
        }
        if published_after:
            params["publishedAfter"] = published_after
        search = _youtube_get(session, api_key, "search", params)
        ids = [
            (result.get("id") or {}).get("videoId")
            for result in search.get("items", [])
            if (result.get("id") or {}).get("videoId")
        ]
        if not ids:
            time.sleep(pause)
            continue
        videos = _youtube_get(session, api_key, "videos", {
            "part": "snippet,statistics",
            "id": ",".join(ids),
            "maxResults": len(ids),
        })
        for video in videos.get("items", []):
            video_id = video.get("id")
            snippet = video.get("snippet") or {}
            stats = video.get("statistics") or {}
            title = snippet.get("title") or ""
            description = snippet.get("description") or ""
            channel = snippet.get("channelTitle") or snippet.get("channelId") or "youtube"
            published_at = snippet.get("publishedAt")
            comments = _youtube_video_comments(session, api_key, str(video_id), max_comments, max_recent, pause)
            summary = _youtube_comment_summary(comments)
            views = _int(stats.get("viewCount"))
            likes = _int(stats.get("likeCount"))
            comment_count = _int(stats.get("commentCount"))
            age_days = _days_since(published_at)
            body_parts = [
                f"Partition: {item['partition']}",
                f"Keyword bucket: {item['bucket']}",
                f"Matched keyword: {item['keyword']}",
                f"Description: {description[:1800]}",
                "Top comments:",
            ]
            for comment in comments[:25]:
                body_parts.append(f"- [{comment['signal_type']}; likes {comment['likes']}] {comment['text'][:450]}")
            body = "\n".join(body_parts)
            row = _signal(
                source="youtube",
                channel=channel,
                item_type="video_comment_thread",
                collected_on=collection_date,
                external_id=video_id,
                created_at=published_at,
                title=title,
                body=body[:9000],
                url=f"https://www.youtube.com/watch?v={video_id}",
                engagement={
                    "views": views,
                    "likes": likes,
                    "comments": comment_count,
                    "views_per_day": round(views / age_days, 2),
                    "comments_per_day": round(comment_count / age_days, 2),
                    "engagement_rate": round((likes + comment_count) / views, 6) if views else 0,
                    **summary,
                },
                evidence_quality="public_youtube_api",
                source_method="youtube_data_api",
            )
            row.update({
                "platform_partition": item["partition"],
                "segment": item["segment"],
                "keyword_bucket": item["bucket"],
                "matched_keyword": item["keyword"],
                "video_metrics": {
                    "views": views,
                    "likes": likes,
                    "comment_count": comment_count,
                    "published_at": published_at,
                    "views_per_day": round(views / age_days, 2),
                    "comments_per_day": round(comment_count / age_days, 2),
                    "engagement_rate": round((likes + comment_count) / views, 6) if views else 0,
                },
                "comment_summary": summary,
                "comments_sample": comments[:50],
            })
            rows[row["id"]] = row
        time.sleep(pause)

    with output_path.open("w", encoding="utf-8") as f:
        for row in rows.values():
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return output_path


def collect_public_signals(config_path: pathlib.Path, output_path: pathlib.Path, collection_date: str) -> pathlib.Path:
    cfg = _json(config_path)
    rows: list[dict[str, Any]] = []
    rows.extend(collect_github_signals(cfg.get("github", {}), collection_date))
    rows.extend(collect_hacker_news_signals(cfg.get("hacker_news", {}), collection_date))
    rows.extend(collect_broker_doc_signals(cfg.get("broker_docs", {}), collection_date))
    youtube_cfg = cfg.get("youtube", {})
    if youtube_cfg.get("enabled", False):
        youtube_config = ROOT / youtube_cfg.get("config", "config/youtube_keywords.json")
        youtube_output = output_path.parent / f"youtube_signals_{collection_date}.jsonl"
        collect_youtube_signals(youtube_config, youtube_output, collection_date)
        rows.extend(_load_signals(youtube_output))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return output_path


def collect_public(config_path: pathlib.Path, output_path: pathlib.Path) -> pathlib.Path:
    import requests
    cfg = _json(config_path)
    ua = os.getenv("REDDIT_USER_AGENT", "personal-market-analysis/1.0")
    session = requests.Session()
    session.headers["User-Agent"] = ua
    result: dict[str, list[dict[str, Any]]] = {}
    for sub in cfg["subreddits"]:
        collected: dict[str, dict[str, Any]] = {}
        for sort in cfg.get("sorts", ["new"]):
            url = f"https://www.reddit.com/r/{sub}/{sort}.json"
            params = {"limit": min(int(cfg.get("limit_per_sort", 100)), 100), "raw_json": 1}
            response = session.get(url, params=params, timeout=30)
            if response.status_code in {403, 429}:
                print(f"Skipping r/{sub}/{sort}: Reddit returned {response.status_code}", file=sys.stderr)
                time.sleep(1.1)
                continue
            response.raise_for_status()
            for child in response.json().get("data", {}).get("children", []):
                d = child.get("data", {})
                pid = "t3_" + str(d.get("id"))
                row = collected.setdefault(pid, {
                    "id": pid, "subreddit": sub, "title": d.get("title"),
                    "author": d.get("author"), "score": d.get("score"),
                    "num_comments": d.get("num_comments"), "permalink": "https://reddit.com" + str(d.get("permalink", "")),
                    "url": d.get("url"), "selftext": d.get("selftext"), "flair": d.get("link_flair_text"),
                    "timestamp": d.get("created_utc"), "comments": [], "sort_type": sort,
                })
                if sort not in str(row.get("sort_type", "")).split(","):
                    row["sort_type"] = str(row.get("sort_type", "")) + "," + sort
            time.sleep(1.1)
        result[sub] = list(collected.values())
    _write_json(output_path, result)
    return output_path


def collect_api(config_path: pathlib.Path, output_path: pathlib.Path) -> pathlib.Path:
    import praw
    cfg = _json(config_path)
    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"], client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        username=os.getenv("REDDIT_USERNAME"), password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.environ["REDDIT_USER_AGENT"],
    )
    result: dict[str, list[dict[str, Any]]] = {}
    for sub in cfg["subreddits"]:
        found: dict[str, dict[str, Any]] = {}
        sr = reddit.subreddit(sub)
        for sort in cfg.get("sorts", ["new"]):
            listing = getattr(sr, sort)(limit=int(cfg.get("limit_per_sort", 100)))
            for p in listing:
                pid = "t3_" + p.id
                if pid in found:
                    continue
                p.comments.replace_more(limit=0)
                found[pid] = {
                    "id": pid, "subreddit": sub, "sort_type": sort, "title": p.title,
                    "author": str(p.author) if p.author else None, "score": p.score,
                    "num_comments": p.num_comments, "permalink": "https://reddit.com" + p.permalink,
                    "url": p.url, "selftext": p.selftext, "flair": p.link_flair_text,
                    "timestamp": p.created_utc,
                    "comments": [{"id": c.id, "author": str(c.author) if c.author else None, "score": c.score,
                                  "body": c.body, "created_utc": c.created_utc}
                                 for c in list(p.comments)[: int(cfg.get("comment_limit", 100))]],
                }
        result[sub] = list(found.values())
    _write_json(output_path, result)
    return output_path


def validate() -> None:
    index = _json(ROOT / "manifests" / "all_dumps.json")
    for dump in index["dumps"]:
        manifest = _json(ROOT / dump["manifest"])
        for file in manifest["files"]:
            path = ROOT / file["path"]
            if not path.exists() or _sha(path) != file["sha256"]:
                raise RuntimeError(f"Integrity failure: {path}")
    print(f"Validated {len(index['dumps'])} dump(s)")


def git_publish(push: bool) -> None:
    validate()
    subprocess.run(["git", "add", "daily-dumps", "manifests", "product-catalog", "schemas", "config"], cwd=ROOT, check=True)
    status = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
    if status.returncode:
        subprocess.run(["git", "commit", "-m", f"data: publish insights snapshot {dt.date.today().isoformat()}"], cwd=ROOT, check=True)
    if push:
        subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--mode", choices=["auto", "api", "public"], default="auto")
    c.add_argument("--config", type=pathlib.Path, default=ROOT / "config" / "channels.json")
    c.add_argument("--output", type=pathlib.Path, default=ROOT / "staging" / "all_results.json")
    sig = sub.add_parser("collect-signals")
    sig.add_argument("--config", type=pathlib.Path, default=ROOT / "config" / "public_signal_sources.json")
    sig.add_argument("--output", type=pathlib.Path)
    sig.add_argument("--date", default=dt.date.today().isoformat())
    y = sub.add_parser("collect-youtube")
    y.add_argument("--config", type=pathlib.Path, default=ROOT / "config" / "youtube_keywords.json")
    y.add_argument("--output", type=pathlib.Path)
    y.add_argument("--date", default=dt.date.today().isoformat())
    p = sub.add_parser("package")
    p.add_argument("--input", type=pathlib.Path, required=True)
    p.add_argument("--date", default=dt.date.today().isoformat())
    p.add_argument("--source", default="reddit")
    p.add_argument("--signals", type=pathlib.Path)
    sub.add_parser("validate")
    pub = sub.add_parser("publish"); pub.add_argument("--push", action="store_true")
    daily = sub.add_parser("daily")
    daily.add_argument("--mode", choices=["auto", "api", "public"], default="auto")
    daily.add_argument("--skip-signals", action="store_true")
    daily.add_argument("--push", action="store_true")
    args = parser.parse_args()
    if args.command == "collect":
        use_api = args.mode == "api" or (args.mode == "auto" and os.getenv("REDDIT_CLIENT_ID"))
        print((collect_api if use_api else collect_public)(args.config, args.output))
    elif args.command == "collect-signals":
        output = args.output or ROOT / "staging" / f"public_signals_{args.date}.jsonl"
        print(collect_public_signals(args.config, output, args.date))
    elif args.command == "collect-youtube":
        output = args.output or ROOT / "staging" / f"youtube_signals_{args.date}.jsonl"
        print(collect_youtube_signals(args.config, output, args.date))
    elif args.command == "package": print(package_dump(args.input, args.date, args.source, args.signals))
    elif args.command == "validate": validate()
    elif args.command == "publish": git_publish(args.push)
    elif args.command == "daily":
        today = dt.date.today().isoformat()
        output = ROOT / "staging" / f"reddit_{today}.json"
        use_api = args.mode == "api" or (args.mode == "auto" and os.getenv("REDDIT_CLIENT_ID"))
        (collect_api if use_api else collect_public)(ROOT / "config" / "channels.json", output)
        signals = None
        if not args.skip_signals:
            signals = ROOT / "staging" / f"public_signals_{today}.jsonl"
            collect_public_signals(ROOT / "config" / "public_signal_sources.json", signals, today)
        package_dump(output, today, signals_path=signals)
        git_publish(args.push)


if __name__ == "__main__":
    main()
