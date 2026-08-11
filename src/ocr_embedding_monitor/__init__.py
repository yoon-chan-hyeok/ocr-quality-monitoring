"""Label-free OCR anomaly monitoring from text embeddings."""

from .detector import DetectionConfig, detect_shift
from .embedding import build_embedder

__all__ = ["DetectionConfig", "build_embedder", "detect_shift"]
__version__ = "0.1.0"

