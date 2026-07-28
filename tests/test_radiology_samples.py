from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CASE_LIBRARY = ROOT / "data" / "radiology_case_library.json"
SAMPLE_MANIFEST = ROOT / "data" / "radiology_sample_manifest.json"
ATTRIBUTION = ROOT / "assets" / "radiology_samples" / "ATTRIBUTION.md"


class RadiologySampleLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = json.loads(CASE_LIBRARY.read_text(encoding="utf-8"))
        cls.manifest = json.loads(SAMPLE_MANIFEST.read_text(encoding="utf-8"))
        cls.samples = cls.manifest["samples"]

    def test_every_case_has_at_least_five_samples(self) -> None:
        counts = Counter(sample["case_id"] for sample in self.samples)
        expected_case_ids = {case["case_id"] for case in self.cases}
        self.assertEqual(set(counts), expected_case_ids)
        for case_id in expected_case_ids:
            self.assertGreaterEqual(counts[case_id], 5, case_id)

    def test_sample_ids_paths_and_sources_are_unique(self) -> None:
        for field in ("sample_id", "local_path", "source_page"):
            values = [sample[field] for sample in self.samples]
            self.assertEqual(len(values), len(set(values)), field)

    def test_every_sample_is_a_readable_local_image(self) -> None:
        for sample in self.samples:
            path = ROOT / sample["local_path"]
            self.assertTrue(path.is_file(), path)
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                self.assertGreater(image.width, 100, path)
                self.assertGreater(image.height, 100, path)
                self.assertEqual(image.format, "JPEG", path)
                self.assertFalse(image.getexif(), path)

    def test_every_sample_has_open_license_and_attribution(self) -> None:
        attribution = ATTRIBUTION.read_text(encoding="utf-8")
        for sample in self.samples:
            self.assertTrue(
                sample["license"].startswith(("CC0", "CC BY", "Public domain")),
                sample["sample_id"],
            )
            self.assertIn(sample["title"], attribution)
            self.assertTrue(sample["source_page"].startswith("https://commons.wikimedia.org/"))


if __name__ == "__main__":
    unittest.main()
