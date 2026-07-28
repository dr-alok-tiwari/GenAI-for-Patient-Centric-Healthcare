# Dropdown Coverage Report

Verified: 2026-07-28

## Result

- Complete workflows: 24
- Programme pillars: 4
- Professional roles: 16
- Distinct tasks: 24
- Visible selector options enumerated: 92
- Visible options without a response: 0
- Coverage: 100%

## Method

The Prompt Studio, Tool Directory, and Tool Demo Lab use options derived from complete data records. Each selector is populated from records still reachable after prior selections. Unsupported intersections are therefore removed before selection.

Every complete workflow includes:

- pillar, role, task, input, output, language, and risk
- synthetic dataset
- primary and alternative tools
- medical or pharma case context
- bounded prompt template
- expected output
- verification checklist
- prohibited actions
- qualified human reviewer
- verification date

Free-text queries are handled separately. Exact matches are shown when available; otherwise the interface returns a clearly labelled closest verified alternative.

## Automated evidence

`tests/test_dropdown_coverage.py` enumerates every visible option and every complete ordered workflow path. `tests/test_app_integrity.py` verifies tools, URLs, datasets, assets, labs, downloads, and the absence of legacy terminal empty-state messages.

The downloadable `assets/downloads/Dropdown_Coverage_Report.pdf` contains the full option-by-option matrix.
