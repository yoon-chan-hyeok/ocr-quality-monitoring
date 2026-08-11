"""Embedding backends used by the monitor."""

from __future__ import annotations

from typing import Protocol, Sequence

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer


class Embedder(Protocol):
    backend_name: str
    model_name: str

    def encode(self, texts: Sequence[str]) -> np.ndarray: ...


class HashEmbedder:
    """Deterministic local backend for tests and pipeline smoke runs."""

    backend_name = "hash"

    def __init__(self, dimensions: int = 1024) -> None:
        self.model_name = f"char-hashing-{dimensions}d"
        self._vectorizer = HashingVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            n_features=dimensions,
            alternate_sign=False,
            norm="l2",
        )

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        matrix = self._vectorizer.transform(list(texts))
        return matrix.astype(np.float32).toarray()


class SentenceTransformerEmbedder:
    backend_name = "sentence-transformers"

    def __init__(
        self,
        model_name: str,
        *,
        device: str | None = None,
        batch_size: int = 32,
        local_files_only: bool = False,
    ) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "Install the semantic extra first: pip install -e \".[semantic]\""
            ) from exc
        resolved_device = None if device in {None, "auto"} else device
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = SentenceTransformer(
            model_name,
            device=resolved_device,
            local_files_only=local_files_only,
        )

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        values = self._model.encode(
            list(texts),
            batch_size=self.batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        return np.asarray(values, dtype=np.float32)


def build_embedder(
    backend: str,
    *,
    model_name: str = "BAAI/bge-m3",
    dimensions: int = 1024,
    device: str | None = "auto",
    batch_size: int = 32,
    local_files_only: bool = False,
) -> Embedder:
    """Construct an explicit embedding backend without silent fallback."""
    normalized = backend.strip().lower()
    if normalized == "hash":
        return HashEmbedder(dimensions=dimensions)
    if normalized in {"sentence-transformers", "semantic", "local"}:
        return SentenceTransformerEmbedder(
            model_name,
            device=device,
            batch_size=batch_size,
            local_files_only=local_files_only,
        )
    raise ValueError(f"Unknown embedding backend: {backend}")

