from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ocr_embedding_monitor.embedding import HashEmbedder
from ocr_embedding_monitor.runner import compare_files


class RunnerTests(unittest.TestCase):
    def test_example_run_writes_all_artifacts(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            result = compare_files(
                root / "examples" / "baseline.jsonl",
                root / "examples" / "candidate_corrupted.jsonl",
                output,
                HashEmbedder(dimensions=256),
            )
            self.assertTrue((output / "summary.json").exists())
            self.assertTrue((output / "scored_records.jsonl").exists())
            self.assertTrue((output / "report.md").exists())
            self.assertEqual(result["run"]["backend"], "hash")
            self.assertGreater(result["summary"]["candidate_count"], 0)


if __name__ == "__main__":
    unittest.main()

