"""Cohort and record-level OCR embedding anomaly detector."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from .metrics import (
    centroid_cosine_distance,
    nearest_neighbor_profile,
    rbf_mmd,
    robust_positive_z,
)


@dataclass(frozen=True)
class DetectionConfig:
    z_threshold: float = 3.0
    review_rate_threshold: float = 0.05
    high_rate_threshold: float = 0.20
    mmd_max_samples: int = 1000
    seed: int = 17


def detect_shift(
    reference_embeddings: np.ndarray,
    candidate_embeddings: np.ndarray,
    reference_ids: Sequence[str],
    candidate_ids: Sequence[str],
    *,
    config: DetectionConfig | None = None,
) -> dict[str, Any]:
    """Score a new OCR cohort against a previously accepted baseline cohort."""
    config = config or DetectionConfig()
    reference = np.asarray(reference_embeddings, dtype=np.float32)
    candidate = np.asarray(candidate_embeddings, dtype=np.float32)
    _validate_shapes(reference, candidate, reference_ids, candidate_ids)

    baseline_nn, candidate_nn, nearest_indices = nearest_neighbor_profile(reference, candidate)
    anomaly_scores, calibration = robust_positive_z(candidate_nn, baseline_nn)
    mmd_value, mmd_gamma = rbf_mmd(
        reference,
        candidate,
        max_samples=config.mmd_max_samples,
        seed=config.seed,
    )
    flagged = anomaly_scores >= config.z_threshold
    flag_rate = float(flagged.mean())
    risk_level = _risk_level(flag_rate, anomaly_scores, config)
    baseline_mean = float(np.mean(baseline_nn))
    candidate_mean = float(np.mean(candidate_nn))

    records = []
    for index, candidate_id in enumerate(candidate_ids):
        records.append(
            {
                "record_id": str(candidate_id),
                "anomaly_score": float(anomaly_scores[index]),
                "review_recommended": bool(flagged[index]),
                "nearest_baseline_id": str(reference_ids[int(nearest_indices[index])]),
                "nearest_baseline_cosine_distance": float(candidate_nn[index]),
            }
        )
    records.sort(key=lambda row: row["anomaly_score"], reverse=True)

    return {
        "summary": {
            "risk_level": risk_level,
            "reference_count": len(reference_ids),
            "candidate_count": len(candidate_ids),
            "embedding_dimension": int(reference.shape[1]),
            "review_recommended_count": int(flagged.sum()),
            "review_recommended_rate": flag_rate,
            "anomaly_score_median": float(np.median(anomaly_scores)),
            "anomaly_score_p95": float(np.quantile(anomaly_scores, 0.95)),
            "centroid_cosine_distance": centroid_cosine_distance(reference, candidate),
            "rbf_mmd": mmd_value,
            "rbf_gamma": mmd_gamma,
            "baseline_nn_distance_mean": baseline_mean,
            "candidate_nn_distance_mean": candidate_mean,
            "nn_distance_ratio": candidate_mean / max(baseline_mean, 1e-12),
            "z_threshold": config.z_threshold,
            "calibration": calibration,
        },
        "records": records,
    }


def _risk_level(flag_rate: float, scores: np.ndarray, config: DetectionConfig) -> str:
    p95 = float(np.quantile(scores, 0.95))
    if flag_rate >= config.high_rate_threshold or p95 >= config.z_threshold * 2.0:
        return "high"
    if flag_rate >= config.review_rate_threshold or p95 >= config.z_threshold:
        return "review"
    return "low"


def _validate_shapes(
    reference: np.ndarray,
    candidate: np.ndarray,
    reference_ids: Sequence[str],
    candidate_ids: Sequence[str],
) -> None:
    if reference.ndim != 2 or candidate.ndim != 2:
        raise ValueError("Embeddings must be two-dimensional matrices")
    if len(reference) != len(reference_ids) or len(candidate) != len(candidate_ids):
        raise ValueError("Embedding rows and record IDs must have matching lengths")
    if len(reference) < 2 or len(candidate) < 1:
        raise ValueError("Use at least two baseline records and one candidate record")
    if reference.shape[1] != candidate.shape[1]:
        raise ValueError("Baseline and candidate embedding dimensions differ")

