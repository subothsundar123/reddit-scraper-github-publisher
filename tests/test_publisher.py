import gzip
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class PublishedSnapshotTests(unittest.TestCase):
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
        retail_keywords = json.dumps(cfg["partitions"]["retail"]["keyword_buckets"]).lower()
        api_keywords = json.dumps(cfg["partitions"]["api"]["keyword_buckets"]).lower()
        self.assertIn("nubra", retail_keywords)
        self.assertIn("nubra", api_keywords)
        self.assertIn("option chain", retail_keywords)
        self.assertIn("websocket", api_keywords)

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
