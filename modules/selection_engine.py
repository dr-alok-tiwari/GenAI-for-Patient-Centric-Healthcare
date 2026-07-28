from __future__ import annotations

from collections.abc import Iterable
from typing import Any

ALL = "All supported options"


def _as_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(";") if item.strip()]


def records_matching(
    records: Iterable[dict[str, Any]],
    selections: dict[str, str | None],
) -> list[dict[str, Any]]:
    """Return catalog rows supporting every non-All selection."""
    result: list[dict[str, Any]] = []
    for record in records:
        if all(
            not selected
            or selected == ALL
            or selected in _as_values(record.get(field))
            for field, selected in selections.items()
        ):
            result.append(record)
    return result


def supported_options(
    records: Iterable[dict[str, Any]],
    field: str,
    selections: dict[str, str | None] | None = None,
) -> list[str]:
    """Build options only from rows still reachable through prior selections."""
    pool = records_matching(records, selections or {})
    return sorted({item for record in pool for item in _as_values(record.get(field))})


def closest_alternative(
    records: list[dict[str, Any]],
    query: str,
    fields: tuple[str, ...] = ("title", "task", "case_context", "pillar"),
) -> dict[str, Any] | None:
    """Return a deterministic verified alternative for unmatched free text."""
    if not records:
        return None
    tokens = {token for token in query.lower().replace("/", " ").split() if len(token) > 2}
    if not tokens:
        return records[0]

    def score(record: dict[str, Any]) -> tuple[int, str]:
        text = " ".join(str(record.get(field, "")) for field in fields).lower()
        return (sum(token in text for token in tokens), str(record.get("title", "")))

    return max(records, key=score)


def coverage_matrix(records: list[dict[str, Any]], fields: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for field in fields:
        for option in supported_options(records, field):
            count = len(records_matching(records, {field: option}))
            rows.append({"Field": field, "Visible option": option, "Workflows": str(count), "Status": "Covered"})
    return rows
