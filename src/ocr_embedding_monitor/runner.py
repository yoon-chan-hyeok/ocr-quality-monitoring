"""End-to-end comparison runner and artifact writer."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .detector import DetectionConfig, detect_shift
from .embedding import Embedder
from .io import read_records, sha256_file, write_json, write_jsonl


def compare_files(
    baseline_path: str | Path,
    candidate_path: str | Path,
    output_dir: str | Path,
    embedder: Embedder,
    *,
    config: DetectionConfig | None = None,
    text_field: str = "text",
    id_field: str = "block_id",
) -> dict[str, Any]:
    baseline_path = Path(baseline_path)
    candidate_path = Path(candidate_path)
    output_dir = Path(output_dir)
    baseline = read_records(baseline_path, text_field=text_field, id_field=id_field)
    candidate = read_records(candidate_path, text_field=text_field, id_field=id_field)

    baseline_embeddings = embedder.encode([row[text_field] for row in baseline])
    candidate_embeddings = embedder.encode([row[text_field] for row in candidate])
    result = detect_shift(
        baseline_embeddings,
        candidate_embeddings,
        [str(row[id_field]) for row in baseline],
        [str(row[id_field]) for row in candidate],
        config=config,
    )

    by_id = {str(row[id_field]): row for row in candidate}
    scored_rows = []
    for score in result["records"]:
        source = by_id[score["record_id"]]
        scored_rows.append({**source, **score})

    result["run"] = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "backend": embedder.backend_name,
        "model": embedder.model_name,
        "baseline_file": baseline_path.name,
        "baseline_sha256": sha256_file(baseline_path),
        "candidate_file": candidate_path.name,
        "candidate_sha256": sha256_file(candidate_path),
        "text_field": text_field,
        "id_field": id_field,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "summary.json", result)
    write_jsonl(output_dir / "scored_records.jsonl", scored_rows)
    (output_dir / "report.md").write_text(_render_report(result), encoding="utf-8")
    return result


def _render_report(result: dict[str, Any]) -> str:
    summary = result["summary"]
    run = result["run"]
    lines = [
        "# OCR Embedding Monitor Report",
        "",
        f"- Risk level: **{summary['risk_level'].upper()}**",
        f"- Backend: `{run['backend']}` / `{run['model']}`",
        f"- Baseline records: {summary['reference_count']}",
        f"- Candidate records: {summary['candidate_count']}",
        f"- Review recommended: {summary['review_recommended_count']} "
        f"({summary['review_recommended_rate']:.1%})",
        f"- Centroid cosine distance: {summary['centroid_cosine_distance']:.6f}",
        f"- RBF MMD: {summary['rbf_mmd']:.6f}",
        f"- Nearest-neighbor distance ratio: {summary['nn_distance_ratio']:.3f}",
        "",
        "## Highest-Risk OCR Records",
        "",
        "| Record | Score | NN distance | Nearest baseline | Review |",
        "|---|---:|---:|---|---|",
    ]
    for row in result["records"][:20]:
        lines.append(
            f"| {row['record_id']} | {row['anomaly_score']:.3f} | "
            f"{row['nearest_baseline_cosine_distance']:.4f} | "
            f"{row['nearest_baseline_id']} | "
            f"{'yes' if row['review_recommended'] else 'no'} |"
        )
    lines.extend(
        [
            "",
            "> This is an anomaly and review-priority report, not proof that an OCR token is wrong.",
            "",
        ]
    )
    return "\n".join(lines)

