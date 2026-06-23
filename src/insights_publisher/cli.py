from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
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


def package_dump(input_path: pathlib.Path, collection_date: str, source: str = "reddit") -> pathlib.Path:
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
    summary = {
        "collection_date": collection_date,
        "source": source,
        "posts": len(posts),
        "comments": len(comments),
        "subreddits": subreddit_counts,
        "engagement": {
            "post_score_sum": sum(p["score"] for p in posts),
            "comment_score_sum": sum(c["score"] for c in comments),
            "reported_comment_sum": sum(p["num_comments"] for p in posts),
        },
        "privacy": "Public text retained for analysis; Reddit usernames replaced with stable one-way hashes.",
    }
    _write_json(out / "summary.json", summary)
    files = []
    for p in (post_path, comment_path, out / "summary.json"):
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
        "posts": len(posts), "comments": len(comments),
    })
    index["dumps"].sort(key=lambda d: d["collection_date"])
    index["updated_at"] = manifest["generated_at"]
    _write_json(manifest_path, index)
    return out


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
    subprocess.run(["git", "add", "daily-dumps", "manifests", "product-catalog", "schemas"], cwd=ROOT, check=True)
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
    p = sub.add_parser("package")
    p.add_argument("--input", type=pathlib.Path, required=True)
    p.add_argument("--date", default=dt.date.today().isoformat())
    sub.add_parser("validate")
    pub = sub.add_parser("publish"); pub.add_argument("--push", action="store_true")
    daily = sub.add_parser("daily")
    daily.add_argument("--mode", choices=["auto", "api", "public"], default="auto")
    daily.add_argument("--push", action="store_true")
    args = parser.parse_args()
    if args.command == "collect":
        use_api = args.mode == "api" or (args.mode == "auto" and os.getenv("REDDIT_CLIENT_ID"))
        print((collect_api if use_api else collect_public)(args.config, args.output))
    elif args.command == "package": print(package_dump(args.input, args.date))
    elif args.command == "validate": validate()
    elif args.command == "publish": git_publish(args.push)
    elif args.command == "daily":
        output = ROOT / "staging" / f"reddit_{dt.date.today().isoformat()}.json"
        use_api = args.mode == "api" or (args.mode == "auto" and os.getenv("REDDIT_CLIENT_ID"))
        (collect_api if use_api else collect_public)(ROOT / "config" / "channels.json", output)
        package_dump(output, dt.date.today().isoformat())
        git_publish(args.push)


if __name__ == "__main__":
    main()
