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

if __name__ == "__main__": unittest.main()
