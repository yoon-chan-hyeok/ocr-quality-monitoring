from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ocr_embedding_monitor.io import read_records


class IoTests(unittest.TestCase):
    def test_missing_id_gets_stable_row_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.jsonl"
            path.write_text('{"text":"hello"}\n', encoding="utf-8")
            rows = read_records(path)
        self.assertEqual(rows[0]["block_id"], "row-000001")

    def test_empty_text_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.jsonl"
            path.write_text('{"block_id":"a","text":""}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-empty"):
                read_records(path)


if __name__ == "__main__":
    unittest.main()

