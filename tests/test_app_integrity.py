from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

from modules.content import LABS, QUIZ

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOWNLOADS = ROOT / "assets" / "downloads"


class AppIntegrityTests(unittest.TestCase):
    def test_tool_matrix_is_complete(self) -> None:
        with (DATA / "tool_comparison_matrix.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 29)
        required = [
            "Tool", "Category", "Access", "Dataset", "Risk level",
            "Risk / privacy warning", "Official URL", "Verified on", "Pillars",
            "Roles", "Input modalities", "Output types", "Human reviewer",
            "Evidence capability", "Verified source",
        ]
        for row in rows:
            with self.subTest(tool=row["Tool"]):
                for field in required:
                    self.assertTrue(row[field].strip(), field)
                self.assertTrue(row["Official URL"].startswith("https://"))
                self.assertTrue((DATA / row["Dataset"]).exists(), row["Dataset"])

    def test_tool_demo_playbook_covers_all_tools(self) -> None:
        rows = json.loads((DATA / "tool_demo_playbook.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 29)
        for row in rows:
            self.assertTrue(row["Pillars"])
            self.assertTrue(row["Roles"])
            self.assertTrue(row["Input types"])
            self.assertTrue(row["Workflow IDs"])
            self.assertTrue((DATA / row["Dataset"]).exists())

    def test_six_labs_and_twenty_questions(self) -> None:
        self.assertEqual(len(LABS), 6)
        self.assertEqual(len(QUIZ), 20)
        expected = {
            "prescription_cases.csv", "imaging_cases.csv", "discharge_summaries.csv",
            "clinical_reasoning_cases.csv", "adverse_event_reports.csv",
            "research_questions.csv",
        }
        self.assertEqual({lab["dataset"] for lab in LABS}, expected)
        for lab in LABS:
            self.assertTrue((DATA / lab["dataset"]).exists())
            self.assertGreaterEqual(len(lab["review"]), 4)
            self.assertGreaterEqual(len(lab["tool_options"]), 2)

    def test_legacy_terminal_empty_states_are_absent(self) -> None:
        directory = (ROOT / "modules" / "tool_directory.py").read_text(encoding="utf-8")
        demos = (ROOT / "modules" / "tool_demos.py").read_text(encoding="utf-8")
        self.assertNotIn("No tool matches the selected filters", directory)
        self.assertNotIn("No demo matches the selected filters", demos)
        self.assertIn("closest verified alternative", directory.lower())
        self.assertIn("closest verified demo", demos.lower())

    def test_primary_downloads_exist(self) -> None:
        expected = [
            "Alkem_AI_Masterclass_Healthcare.pptx",
            "Alkem_AI_Masterclass_Healthcare.pdf",
            "Alkem_AI_Masterclass_Participant_Workbook.docx",
            "Alkem_AI_Masterclass_Participant_Workbook.pdf",
            "Alkem_AI_Masterclass_Facilitator_Handbook.docx",
            "Alkem_AI_Masterclass_Facilitator_Handbook.pdf",
            "Alkem_AI_Masterclass_Healthcare_Tool_Matrix.xlsx",
            "Dropdown_Coverage_Report.pdf",
        ]
        for filename in expected:
            with self.subTest(filename=filename):
                self.assertTrue((DOWNLOADS / filename).exists())

    def test_slide_metadata_and_previews_match(self) -> None:
        slides = ROOT / "assets" / "slides"
        meta = json.loads((slides / "slides_meta.json").read_text(encoding="utf-8"))
        self.assertEqual(len(meta), 12)
        for index, item in enumerate(meta, 1):
            self.assertEqual(item["number"], index)
            self.assertTrue((slides / item["image"]).exists())


if __name__ == "__main__":
    unittest.main()
