from __future__ import annotations

import json
import unittest
from pathlib import Path

from modules.selection_engine import records_matching, supported_options

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ASSETS = ROOT / "assets"


class DropdownCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflows = json.loads((DATA / "workflow_catalog.json").read_text(encoding="utf-8"))

    def test_catalog_has_four_balanced_pillars(self) -> None:
        counts: dict[str, int] = {}
        for item in self.workflows:
            counts[item["pillar"]] = counts.get(item["pillar"], 0) + 1
        self.assertEqual(len(counts), 4)
        self.assertTrue(all(count >= 5 for count in counts.values()), counts)

    def test_every_workflow_is_complete(self) -> None:
        required = [
            "workflow_id", "title", "pillar", "roles", "task", "input_type",
            "output_type", "risk_level", "data_sensitivity", "languages",
            "primary_tool", "dataset", "case_context", "prompt_template",
            "expected_output", "verification", "prohibited_actions",
            "human_reviewer", "last_verified",
        ]
        for item in self.workflows:
            with self.subTest(workflow=item["workflow_id"]):
                for field in required:
                    self.assertIn(field, item)
                    self.assertNotIn(item[field], ("", None, []))
                self.assertTrue((DATA / item["dataset"]).exists(), item["dataset"])
                self.assertIn("qualified", item["prompt_template"].lower())
                self.assertGreaterEqual(len(item["verification"]), 4)

    def test_every_visible_option_returns_a_workflow(self) -> None:
        fields = ["pillar", "roles", "task", "input_type", "output_type", "languages", "risk_level"]
        for field in fields:
            options = supported_options(self.workflows, field)
            self.assertTrue(options, field)
            for option in options:
                with self.subTest(field=field, option=option):
                    self.assertTrue(records_matching(self.workflows, {field: option}))

    def test_every_complete_cascade_path_stays_selectable(self) -> None:
        ordered_fields = ["pillar", "roles", "task", "input_type", "languages"]
        for item in self.workflows:
            for role in item["roles"]:
                for language in item["languages"]:
                    selections: dict[str, str] = {}
                    expected = {
                        "pillar": item["pillar"],
                        "roles": role,
                        "task": item["task"],
                        "input_type": item["input_type"],
                        "languages": language,
                    }
                    for field in ordered_fields:
                        option = expected[field]
                        with self.subTest(workflow=item["workflow_id"], field=field, option=option):
                            self.assertIn(option, supported_options(self.workflows, field, selections))
                            selections[field] = option
                            self.assertTrue(records_matching(self.workflows, selections))

    def test_medical_assets_exist_and_are_synthetic(self) -> None:
        prescriptions = (DATA / "prescription_cases.csv").read_text(encoding="utf-8")
        imaging = (DATA / "imaging_cases.csv").read_text(encoding="utf-8")
        for name in [f"synthetic_prescription_{index:02d}.png" for index in range(1, 7)]:
            self.assertTrue((ASSETS / "medical" / name).exists(), name)
            self.assertIn(name, prescriptions)
        self.assertTrue((ASSETS / "medical" / "synthetic_chest_xray.png").exists())
        self.assertIn("synthetic_chest_xray.png", imaging)
        self.assertIn("no diagnostic ground truth", imaging.lower())


if __name__ == "__main__":
    unittest.main()
