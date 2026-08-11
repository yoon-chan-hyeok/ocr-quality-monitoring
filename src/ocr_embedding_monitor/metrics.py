"""Embedding geometry metrics for label-free OCR monitoring."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import pairwise_distances
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.neighbors import NearestNeighbors


def l2_normalize(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=np.float64)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.where(norms == 0.0, 1.0, norms)


def nearest_neighbor_profile(
    reference: np.ndarray,
    candidate: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return reference leave-one-out distances and candidate nearest matches."""
    reference = l2_normalize(reference)
    candidate = l2_normalize(candidate)
    if len(reference) < 2:
        raise ValueError("The baseline needs at least two OCR records")
    index = NearestNeighbors(metric="cosine", algorithm="brute")
    index.fit(reference)
    reference_distances, _ = index.kneighbors(reference, n_neighbors=2)
    candidate_distances, candidate_indices = index.kneighbors(candidate, n_neighbors=1)
    return (
        reference_distances[:, 1],
        candidate_distances[:, 0],
        candidate_indices[:, 0],
    )


def robust_positive_z(values: np.ndarray, baseline: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    """Scale distances against the baseline using median and MAD."""
    values = np.asarray(values, dtype=np.float64)
    baseline = np.asarray(baseline, dtype=np.float64)
    center = float(np.median(baseline))
    mad = float(np.median(np.abs(baseline - center)))
    scale = 1.4826 * mad
    if scale < 1e-8:
        scale = float(np.std(baseline, ddof=1)) if len(baseline) > 1 else 0.0
    scale = max(scale, 1e-8)
    scores = np.maximum(0.0, (values - center) / scale)
    return scores, {"median": center, "mad": mad, "scale": scale}


def centroid_cosine_distance(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref_center = l2_normalize(reference).mean(axis=0, keepdims=True)
    cand_center = l2_normalize(candidate).mean(axis=0, keepdims=True)
    ref_norm = float(np.linalg.norm(ref_center))
    cand_norm = float(np.linalg.norm(cand_center))
    if ref_norm == 0.0 or cand_norm == 0.0:
        return 0.0
    similarity = float((ref_center @ cand_center.T)[0, 0] / (ref_norm * cand_norm))
    return float(np.clip(1.0 - similarity, 0.0, 2.0))


def rbf_mmd(
    reference: np.ndarray,
    candidate: np.ndarray,
    *,
    max_samples: int = 1000,
    seed: int = 17,
) -> tuple[float, float]:
    """Biased RBF MMD with a pooled median-distance bandwidth."""
    rng = np.random.default_rng(seed)
    reference = _subsample(l2_normalize(reference), max_samples, rng)
    candidate = _subsample(l2_normalize(candidate), max_samples, rng)
    pooled = np.vstack([reference, candidate])
    bandwidth_sample = _subsample(pooled, min(500, len(pooled)), rng)
    squared = pairwise_distances(bandwidth_sample, metric="euclidean", squared=True)
    positive = squared[squared > 1e-12]
    median_squared = float(np.median(positive)) if positive.size else 1.0
    gamma = 1.0 / max(2.0 * median_squared, 1e-12)
    xx = rbf_kernel(reference, reference, gamma=gamma).mean()
    yy = rbf_kernel(candidate, candidate, gamma=gamma).mean()
    xy = rbf_kernel(reference, candidate, gamma=gamma).mean()
    return float(max(0.0, xx + yy - 2.0 * xy)), float(gamma)


def _subsample(values: np.ndarray, limit: int, rng: np.random.Generator) -> np.ndarray:
    if len(values) <= limit:
        return values
    indices = rng.choice(len(values), size=limit, replace=False)
    return values[np.sort(indices)]

