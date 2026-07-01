from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "marketing-keywords" / "current.json"
OUTPUT_DIR = ROOT / "marketing-keywords" / "views"
INDEX_PATH = ROOT / "marketing-keywords" / "README.md"
PAGE_SIZE = 500


def display(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    if any(marker in text for marker in ("â", "Ã", "ð")):
        try:
            text = text.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return text.replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()


def number(value: Any) -> str:
    try:
        return f"{int(float(value)):,}"
    except (TypeError, ValueError):
        return display(value)


def link(label: Any, url: Any) -> str:
    label_text = display(label)
    url_text = str(url or "").strip()
    return f"[{label_text}]({url_text})" if label_text and url_text else label_text


def table(headers: list[str], rows: list[list[Any]]) -> str:
    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    output.extend("| " + " | ".join(display(cell) for cell in row) + " |" for row in rows)
    return "\n".join(output)


def page_header(title: str, description: str, count: int) -> list[str]:
    return [
        f"# {title}",
        "",
        description,
        "",
        f"Entries on this page: **{count:,}**",
        "",
        "[← Back to SEO keyword index](../README.md)",
        "",
    ]


def write_page(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def chunked_pages(
    items: list[dict[str, Any]],
    stem: str,
    title: str,
    description: str,
    headers: list[str],
    row_builder: Any,
) -> list[tuple[str, int, int]]:
    pages = []
    total_pages = max(1, math.ceil(len(items) / PAGE_SIZE))
    for page_index in range(total_pages):
        start = page_index * PAGE_SIZE
        subset = items[start : start + PAGE_SIZE]
        filename = f"{stem}-{page_index + 1:02d}.md"
        page_title = f"{title} — Part {page_index + 1} of {total_pages}"
        rows = [row_builder(item, start + index + 1) for index, item in enumerate(subset)]
        write_page(
            OUTPUT_DIR / filename,
            page_header(page_title, description, len(subset))
            + [table(headers, rows)],
        )
        pages.append((filename, start + 1, start + len(subset)))
    return pages


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    summary = catalog["summary"]
    clusters = list(catalog.get("priority_clusters") or [])
    keywords = list(catalog.get("priority_keywords") or [])
    option_keywords = list(catalog.get("option_chain_keywords") or [])
    programmatic = list(catalog.get("programmatic_pages") or [])
    retail_seeds = list((catalog.get("search_seed_keywords") or {}).get("retail") or [])
    api_seeds = list((catalog.get("search_seed_keywords") or {}).get("api_algo") or [])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for old_page in OUTPUT_DIR.glob("*.md"):
        old_page.unlink()

    cluster_rows = [
        [
            index,
            item.get("cluster_topic"),
            item.get("priority"),
            item.get("theme"),
            number(item.get("max_keyword_volume")),
            number(item.get("keyword_count")),
            link(item.get("best_competitor"), item.get("best_competitor_url")),
            item.get("top_keywords"),
        ]
        for index, item in enumerate(clusters, 1)
    ]
    write_page(
        OUTPUT_DIR / "priority-clusters.md",
        page_header(
            "Priority SEO Clusters",
            "Keyword clusters grouped by search intent and competitor coverage.",
            len(clusters),
        )
        + [
            table(
                ["#", "Cluster", "Priority", "Theme", "Max volume", "Keywords", "Best competitor", "Top keywords"],
                cluster_rows,
            )
        ],
    )

    seed_rows = []
    for segment, items in (("Retail", retail_seeds), ("API / Algo", api_seeds)):
        for item in items:
            seed_rows.append([segment, item.get("keyword"), item.get("priority"), number(item.get("volume"))])
    write_page(
        OUTPUT_DIR / "search-seeds.md",
        page_header(
            "Daily Search Seed Keywords",
            "Compact high-priority keywords used to enrich daily discovery queries.",
            len(seed_rows),
        )
        + [table(["Segment", "Keyword", "Priority", "Volume"], seed_rows)],
    )

    option_rows = [
        [index, item.get("keyword"), number(item.get("volume")), item.get("theme")]
        for index, item in enumerate(option_keywords, 1)
    ]
    write_page(
        OUTPUT_DIR / "option-chain-keywords.md",
        page_header(
            "Option-Chain Keywords",
            "Retail search terms related to option chains, OI, PCR, strikes, expiries and derivatives analytics.",
            len(option_keywords),
        )
        + [table(["#", "Keyword", "Volume", "Theme"], option_rows)],
    )

    keyword_pages = chunked_pages(
        keywords,
        "priority-keywords",
        "Priority SEO Keywords",
        "The prioritized competitor keyword universe. Review product relevance before using a keyword in Nubra content.",
        ["#", "Keyword", "Volume", "Difficulty", "Theme", "Cluster", "Intent", "Best ranking source"],
        lambda item, index: [
            index,
            item.get("keyword"),
            number(item.get("volume")),
            item.get("keyword_difficulty"),
            item.get("theme"),
            item.get("cluster_topic"),
            ", ".join(
                label
                for key, label in (
                    ("informational", "Informational"),
                    ("commercial", "Commercial"),
                    ("transactional", "Transactional"),
                )
                if str(item.get(key)).casefold() == "yes"
            ),
            link(item.get("best_competitor"), item.get("best_ranking_url")),
        ],
    )

    programmatic_pages = chunked_pages(
        programmatic,
        "programmatic-pages",
        "Programmatic SEO Page Ideas",
        "Potential scalable landing pages derived from repeated search patterns.",
        ["#", "Keyword", "Volume", "Theme", "Priority", "Suggested slug"],
        lambda item, index: [
            index,
            item.get("keyword"),
            number(item.get("volume")),
            item.get("programmatic_theme"),
            item.get("priority_cluster"),
            item.get("suggested_slug"),
        ],
    )

    raw_rows = summary.get("raw_rows") or {}
    included = summary.get("included_rows") or {}
    lines = [
        "# Nubra Marketing SEO Keywords",
        "",
        "GitHub-friendly views of the marketing keyword catalog derived from `Nubra - Priority Kws.xlsx`.",
        "",
        "> These tables are for discovery and prioritisation. The full competitor universe contains broad terms, so product relevance should be checked before creating content.",
        "",
        "## Catalog summary",
        "",
        table(
            ["Dataset", "Included entries"],
            [
                ["Priority clusters", number(included.get("priority_clusters"))],
                ["Priority keywords", number(included.get("priority_keywords"))],
                ["Option-chain keywords", number(included.get("option_chain_keywords"))],
                ["Programmatic page ideas", number(included.get("programmatic_pages"))],
                ["Retail daily search seeds", number(len(retail_seeds))],
                ["API/algo daily search seeds", number(len(api_seeds))],
            ],
        ),
        "",
        "## Readable views",
        "",
        "- [Priority SEO clusters](views/priority-clusters.md)",
        "- [Daily retail and API search seeds](views/search-seeds.md)",
        "- [Option-chain keywords](views/option-chain-keywords.md)",
    ]
    for filename, start, end in keyword_pages:
        lines.append(f"- [Priority keywords {start:,}–{end:,}](views/{filename})")
    for filename, start, end in programmatic_pages:
        lines.append(f"- [Programmatic page ideas {start:,}–{end:,}](views/{filename})")
    lines.extend(
        [
            "",
            "## Source coverage",
            "",
            table(
                ["Source sheet", "Raw rows reviewed"],
                [
                    ["Top Pages Consolidated", number(raw_rows.get("top_pages"))],
                    ["Competitor Index of Keywords", number(raw_rows.get("competitor_keywords"))],
                    ["Category-Level Option Analysis", number(raw_rows.get("option_chain_keywords"))],
                    ["Programmatic Pages Expansion", number(raw_rows.get("programmatic_pages"))],
                ],
            ),
            "",
            "## Machine-readable files",
            "",
            "- [`current.json`](current.json) — complete connector catalog",
            "- [`manifest.json`](manifest.json) — version, checksum and record counts",
            "",
            "To regenerate these Markdown views after updating `current.json`:",
            "",
            "```powershell",
            "python .\\tools\\export_marketing_keywords_markdown.py",
            "```",
        ]
    )
    write_page(INDEX_PATH, lines)
    print(f"Generated {3 + len(keyword_pages) + len(programmatic_pages)} Markdown data pages")
    print(f"Index: {INDEX_PATH}")


if __name__ == "__main__":
    main()
