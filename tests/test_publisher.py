import datetime as dt
import gzip
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class PublishedSnapshotTests(unittest.TestCase):
    def test_collection_date_uses_business_timezone_at_utc_boundary(self):
        from insights_publisher.cli import _collection_date
        instant = dt.datetime(2026, 7, 1, 20, 30, tzinfo=dt.timezone.utc)
        self.assertEqual(_collection_date(instant, "Asia/Kolkata"), "2026-07-02")

    def test_manifest_files_and_checksums_exist(self):
        index = json.loads((ROOT / "manifests/all_dumps.json").read_text())
        self.assertGreaterEqual(len(index["dumps"]), 1)
        for entry in index["dumps"]:
            manifest = json.loads((ROOT / entry["manifest"]).read_text())
            for item in manifest["files"]:
                self.assertTrue((ROOT / item["path"]).exists())

    def test_seed_dump_is_readable(self):
        with gzip.open(ROOT / "daily-dumps/2026-06-22/posts.jsonl.gz", "rt", encoding="utf-8") as f:
            first = json.loads(next(f))
        self.assertIn("id", first)
        self.assertNotIn("author", first)
        self.assertIn("author_hash", first)

    def test_catalog_has_status_definitions(self):
        catalog = json.loads((ROOT / "product-catalog/current.json").read_text())
        self.assertGreater(len(catalog["features"]), 100)
        self.assertIn("internal_unverified", catalog["status_definitions"])

    def test_retail_upcoming_catalog_is_deduplicated_and_expanded(self):
        catalog = json.loads((ROOT / "product-catalog/retail-upcoming-features.json").read_text(encoding="utf-8"))
        ids = {item["id"] for item in catalog["features"]}
        self.assertEqual(catalog["count"], 34)
        self.assertEqual(len(ids), catalog["count"])
        self.assertIn("nubra-expanded-auto-refresh-watchlists", ids)
        self.assertIn("nubra-ai-query-scans", ids)
        self.assertIn("nubra-strategy-level-risk-controls", ids)
        self.assertIn("nubra-technical-option-chain-alerts", ids)
        persona = next(item for item in catalog["features"] if item["id"] == "nubra-retail-persona-modes")
        self.assertIn("customised broker", persona["aliases"])

    def test_public_signal_schema_exists(self):
        schema = json.loads((ROOT / "schemas/public-signal.schema.json").read_text())
        self.assertIn("source", schema["required"])
        cfg = json.loads((ROOT / "config/public_signal_sources.json").read_text())
        self.assertIn("github", cfg)
        self.assertIn("youtube", cfg)

    def test_youtube_keywords_are_partitioned(self):
        cfg = json.loads((ROOT / "config/youtube_keywords.json").read_text())
        self.assertIn("retail", cfg["partitions"])
        self.assertIn("api", cfg["partitions"])
        self.assertTrue(cfg["seo_seed_keywords"]["enabled"])
        retail_keywords = json.dumps(cfg["partitions"]["retail"]["keyword_buckets"]).lower()
        api_keywords = json.dumps(cfg["partitions"]["api"]["keyword_buckets"]).lower()
        self.assertIn("nubra", retail_keywords)
        self.assertIn("nubra", api_keywords)
        self.assertIn("option chain", retail_keywords)
        self.assertIn("websocket", api_keywords)

    def test_retail_feature_searches_include_brand_sweep_and_rotation(self):
        from insights_publisher.cli import _flatten_youtube_keywords
        cfg = json.loads((ROOT / "config/youtube_keywords.json").read_text(encoding="utf-8"))
        feature_cfg = json.loads((ROOT / "config/retail_feature_keywords.json").read_text(encoding="utf-8"))
        self.assertIn("Nubra", feature_cfg["broad_nubra_queries"])
        self.assertGreaterEqual(len(feature_cfg["feature_buckets"]), 10)
        rows = _flatten_youtube_keywords(cfg, "2026-07-01")
        brand = [row for row in rows if row["bucket"] == "nubra_brand_sweep"]
        feature_rows = [row for row in rows if row["bucket"].startswith("retail_feature_")]
        retail_base_buckets = {
            row["bucket"] for row in rows
            if row["partition"] == "retail"
            and not row["bucket"].startswith("retail_feature_")
            and row["bucket"] not in {"nubra_brand_sweep", "marketing_seo_priority"}
        }
        self.assertEqual(len(brand), 5)
        self.assertEqual(len(feature_rows), 30)
        self.assertGreaterEqual(len(retail_base_buckets), 8)

    def test_reddit_search_queries_include_broad_nubra_sweep(self):
        cfg = json.loads((ROOT / "config/channels.json").read_text(encoding="utf-8"))
        self.assertIn("Nubra", cfg["search_queries"])
        self.assertIn("option chain alerts", cfg["search_queries"])

    def test_seo_keyword_catalog_exists(self):
        manifest = json.loads((ROOT / "marketing-keywords/manifest.json").read_text(encoding="utf-8"))
        catalog = json.loads((ROOT / "marketing-keywords/current.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["path"], "marketing-keywords/current.json")
        self.assertGreaterEqual(manifest["priority_keyword_count"], 1000)
        self.assertGreaterEqual(manifest["option_chain_keyword_count"], 500)
        self.assertIn("search_seed_keywords", catalog)
        self.assertGreaterEqual(len(catalog["search_seed_keywords"]["retail"]), 50)

    def test_seo_keyword_markdown_views_are_complete(self):
        catalog = json.loads((ROOT / "marketing-keywords/current.json").read_text(encoding="utf-8"))
        index = (ROOT / "marketing-keywords/README.md").read_text(encoding="utf-8")
        self.assertIn("Priority SEO clusters", index)
        self.assertIn("Priority keywords 2,001", index)
        self.assertIn("Programmatic page ideas 501", index)
        view_dir = ROOT / "marketing-keywords/views"
        keyword_pages = sorted(view_dir.glob("priority-keywords-*.md"))
        programmatic_pages = sorted(view_dir.glob("programmatic-pages-*.md"))
        self.assertEqual(len(keyword_pages), 5)
        self.assertEqual(len(programmatic_pages), 2)
        self.assertTrue((view_dir / "option-chain-keywords.md").exists())
        keyword_rows = sum(
            text.count("\n| ") - 2
            for text in (page.read_text(encoding="utf-8") for page in keyword_pages)
        )
        self.assertEqual(keyword_rows, len(catalog["priority_keywords"]))

    def test_manual_research_assets_exist(self):
        self.assertTrue((ROOT / "manual-research/daily-research-prompt.md").exists())
        self.assertTrue((ROOT / "manual-research/research-checklist.md").exists())
        queries = json.loads((ROOT / "manual-research/source-query-bank.json").read_text(encoding="utf-8"))
        self.assertEqual(queries["trigger_phrase"], "dump todays social media data")
        self.assertIn("retail_queries", queries)

    def test_manual_signal_normalization(self):
        from insights_publisher.cli import _normalize_signal_row
        row = _normalize_signal_row({
            "title": "Need better option chain filters",
            "body": "Users compare Sensibull and Nubra for OI filters.",
            "url": "https://example.com",
            "segment": "retail",
        }, "2026-07-01")
        self.assertEqual(row["source_method"], "manual_web_research")
        self.assertEqual(row["segment"], "retail")
        self.assertIn("option_chain", row["tags"])
        self.assertIn("Nubra", row["competitors"])

    def test_feature_persona_and_intent_classification(self):
        from insights_publisher.cli import _is_nubra_market_relevant, _normalize_signal_row
        row = _normalize_signal_row({
            "title": "Option sellers need strategy-level stop loss",
            "body": "Please add P&L based SL TP for the full strategy portfolio.",
            "url": "https://example.com/request",
        }, "2026-07-01")
        self.assertIn("nubra-strategy-level-risk-controls", row["feature_ids"])
        self.assertIn("option_seller", row["personas"])
        self.assertEqual(row["signal_type"], "feature_request")
        funds_row = _normalize_signal_row({
            "title": "Need instant withdrawal",
            "body": "Please add instant payout for unused trading funds.",
            "url": "https://example.com/funds",
        }, "2026-07-01")
        self.assertIn("nubra-instant-fund-movement", funds_row["feature_ids"])
        self.assertNotIn("nubra-flexible-brokerage", funds_row["feature_ids"])
        self.assertTrue(_is_nubra_market_relevant("Nubra option trading app review"))
        self.assertFalse(_is_nubra_market_relevant("Nubra Valley travel guide"))

    def test_youtube_collector_skips_without_key(self):
        from insights_publisher.cli import collect_youtube_signals
        import os
        import tempfile
        os.environ.pop("YOUTUBE_API_KEY", None)
        out = pathlib.Path(tempfile.mkdtemp()) / "youtube.jsonl"
        collect_youtube_signals(ROOT / "config/youtube_keywords.json", out, "2026-06-30")
        self.assertTrue(out.exists())
        self.assertEqual(out.read_text(encoding="utf-8"), "")

if __name__ == "__main__": unittest.main()
