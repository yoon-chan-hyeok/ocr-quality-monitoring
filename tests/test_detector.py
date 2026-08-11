from __future__ import annotations

import unittest

import numpy as np

from ocr_embedding_monitor.detector import DetectionConfig, detect_shift


class DetectorTests(unittest.TestCase):
    def test_orthogonal_candidate_is_prioritized(self) -> None:
        reference = np.asarray(
            [
                [1.0, 0.01, 0.0],
                [1.0, 0.02, 0.0],
                [1.0, 0.03, 0.0],
                [1.0, 0.04, 0.0],
                [1.0, 0.05, 0.0],
            ],
            dtype=np.float32,
        )
        candidate = np.asarray(
            [[1.0, 0.025, 0.0], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        )
        result = detect_shift(
            reference,
            candidate,
            [f"base-{index}" for index in range(5)],
            ["normal", "anomalous"],
            config=DetectionConfig(z_threshold=3.0),
        )
        by_id = {row["record_id"]: row for row in result["records"]}
        self.assertFalse(by_id["normal"]["review_recommended"])
        self.assertTrue(by_id["anomalous"]["review_recommended"])
        self.assertGreater(
            by_id["anomalous"]["anomaly_score"],
            by_id["normal"]["anomaly_score"],
        )


if __name__ == "__main__":
    unittest.main()

