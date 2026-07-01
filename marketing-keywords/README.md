# Nubra Marketing SEO Keywords

GitHub-friendly views of the marketing keyword catalog derived from `Nubra - Priority Kws.xlsx`.

> These tables are for discovery and prioritisation. The full competitor universe contains broad terms, so product relevance should be checked before creating content.

## Catalog summary

| Dataset | Included entries |
| --- | --- |
| Priority clusters | 220 |
| Priority keywords | 2,500 |
| Option-chain keywords | 547 |
| Programmatic page ideas | 1,000 |
| Retail daily search seeds | 80 |
| API/algo daily search seeds | 4 |

## Readable views

- [Priority SEO clusters](views/priority-clusters.md)
- [Daily retail and API search seeds](views/search-seeds.md)
- [Option-chain keywords](views/option-chain-keywords.md)
- [Priority keywords 1–500](views/priority-keywords-01.md)
- [Priority keywords 501–1,000](views/priority-keywords-02.md)
- [Priority keywords 1,001–1,500](views/priority-keywords-03.md)
- [Priority keywords 1,501–2,000](views/priority-keywords-04.md)
- [Priority keywords 2,001–2,500](views/priority-keywords-05.md)
- [Programmatic page ideas 1–500](views/programmatic-pages-01.md)
- [Programmatic page ideas 501–1,000](views/programmatic-pages-02.md)

## Source coverage

| Source sheet | Raw rows reviewed |
| --- | --- |
| Top Pages Consolidated | 30,758 |
| Competitor Index of Keywords | 53,834 |
| Category-Level Option Analysis | 547 |
| Programmatic Pages Expansion | 3,087 |

## Machine-readable files

- [`current.json`](current.json) — complete connector catalog
- [`manifest.json`](manifest.json) — version, checksum and record counts

To regenerate these Markdown views after updating `current.json`:

```powershell
python .\tools\export_marketing_keywords_markdown.py
```
