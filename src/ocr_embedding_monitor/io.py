"""JSONL input and reproducible artifact helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


def read_records(
    path: str | Path,
    *,
    text_field: str = "text",
    id_field: str = "block_id",
) -> list[dict[str, Any]]:
    """Read validated OCR records from a UTF-8 JSONL file."""
    source = Path(path)
    records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    with source.open("r", encoding="utf-8-sig") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at {source.name}:{line_number}") from exc
            if not isinstance(item, dict):
                raise ValueError(f"Row {line_number} must be a JSON object")
            text = item.get(text_field)
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Row {line_number} needs non-empty '{text_field}'")
            record_id = str(item.get(id_field) or f"row-{line_number:06d}")
            if record_id in seen_ids:
                raise ValueError(f"Duplicate '{id_field}' value: {record_id}")
            seen_ids.add(record_id)
            normalized = dict(item)
            normalized[id_field] = record_id
            normalized[text_field] = text.strip()
            records.append(normalized)
    if not records:
        raise ValueError(f"No records found in {source}")
    return records


def write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(dict(payload), ensure_ascii=False, indent=2, default=_json_default) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: str | Path, rows: Iterable[Mapping[str, Any]]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), ensure_ascii=False, default=_json_default) + "\n")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    raise TypeError(f"Cannot serialize {type(value).__name__}")

