"""Command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .detector import DetectionConfig
from .embedding import build_embedder
from .runner import compare_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ocr-embedding-monitor",
        description="Rank suspicious OCR text without token-level error labels.",
    )
    parser.add_argument("--baseline", required=True, help="Accepted baseline OCR JSONL")
    parser.add_argument("--candidate", required=True, help="New OCR JSONL to inspect")
    parser.add_argument("--output-dir", default="outputs/latest")
    parser.add_argument(
        "--backend",
        choices=["sentence-transformers", "hash"],
        default="sentence-transformers",
    )
    parser.add_argument("--model", default="BAAI/bge-m3")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--dimensions", type=int, default=1024, help="Hash backend only")
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument("--z-threshold", type=float, default=3.0)
    parser.add_argument("--text-field", default="text")
    parser.add_argument("--id-field", default="block_id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    embedder = build_embedder(
        args.backend,
        model_name=args.model,
        dimensions=args.dimensions,
        device=args.device,
        batch_size=args.batch_size,
        local_files_only=args.local_files_only,
    )
    result = compare_files(
        args.baseline,
        args.candidate,
        args.output_dir,
        embedder,
        config=DetectionConfig(z_threshold=args.z_threshold),
        text_field=args.text_field,
        id_field=args.id_field,
    )
    summary = result["summary"]
    print(f"risk_level={summary['risk_level']}")
    print(
        "review_recommended="
        f"{summary['review_recommended_count']}/{summary['candidate_count']}"
    )
    print(f"report={Path(args.output_dir) / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

