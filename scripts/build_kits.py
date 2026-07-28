from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
DOWNLOADS = ASSETS / "downloads"


def add_file(archive: ZipFile, source: Path, target: str) -> None:
    if source.exists():
        archive.write(source, target)


def main() -> None:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    dataset_zip = DOWNLOADS / "Synthetic_Healthcare_Pharma_Datasets_Expanded.zip"
    with ZipFile(dataset_zip, "w", ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(DATA.glob("*.csv")):
            if not path.name.startswith("tool_"):
                add_file(archive, path, f"data/{path.name}")
        for name in ["dataset_registry.json", "workflow_catalog.json", "prompt_bank.md", "discussion_cases.md"]:
            add_file(archive, DATA / name, f"data/{name}")
        for path in sorted((ASSETS / "medical").glob("*")):
            if path.is_file():
                add_file(archive, path, f"assets/medical/{path.name}")
        add_file(archive, ROOT / "ASSET_ATTRIBUTION.md", "ASSET_ATTRIBUTION.md")

    kit_zip = DOWNLOADS / "Alkem_AI_Masterclass_Healthcare_Kit.zip"
    downloadable = [
        "Alkem_AI_Masterclass_Healthcare.pptx",
        "Alkem_AI_Masterclass_Healthcare.pdf",
        "Alkem_AI_Masterclass_Participant_Workbook.docx",
        "Alkem_AI_Masterclass_Participant_Workbook.pdf",
        "Alkem_AI_Masterclass_Facilitator_Handbook.docx",
        "Alkem_AI_Masterclass_Facilitator_Handbook.pdf",
        "Alkem_AI_Masterclass_Healthcare_Tool_Matrix.xlsx",
        "Dropdown_Coverage_Report.docx",
        "Dropdown_Coverage_Report.pdf",
        "Synthetic_Healthcare_Pharma_Datasets_Expanded.zip",
        "tool_demo_playbook.csv",
    ]
    root_docs = [
        "README.md", "CHANGELOG.md", "IMPLEMENTATION_REPORT.md",
        "DROPDOWN_COVERAGE_REPORT.md", "ASSET_ATTRIBUTION.md",
    ]
    with ZipFile(kit_zip, "w", ZIP_DEFLATED, compresslevel=9) as archive:
        for name in downloadable:
            add_file(archive, DOWNLOADS / name, name)
        for name in root_docs:
            add_file(archive, ROOT / name, name)
        add_file(archive, DATA / "workflow_catalog.json", "data/workflow_catalog.json")
        add_file(archive, DATA / "tool_comparison_matrix.csv", "data/tool_comparison_matrix.csv")
        for path in sorted((ASSETS / "medical").glob("*")):
            if path.is_file():
                add_file(archive, path, f"assets/medical/{path.name}")
    print(f"Built {dataset_zip.name} and {kit_zip.name}.")


if __name__ == "__main__":
    main()
