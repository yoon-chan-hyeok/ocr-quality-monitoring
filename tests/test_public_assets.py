"""Keep locally present but ignored figures out of published Markdown links."""

from pathlib import Path
import re
import subprocess
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


class PublicAssetsTests(unittest.TestCase):
    def test_linked_local_images_are_present_and_tracked(self) -> None:
        self.assertTrue((ROOT / ".git").exists(), "Run this check in a Git checkout")
        tracked = set(subprocess.check_output(
            ["git", "-c", f"safe.directory={ROOT.as_posix()}", "ls-files", "-z"],
            cwd=ROOT,
        ).decode("utf-8").split("\0"))
        checked = 0
        for relative in sorted(tracked):
            if not relative.endswith(".md"):
                continue
            document = ROOT / relative
            for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc:
                    continue
                asset = (document.parent / unquote(parsed.path)).resolve()
                asset_path = asset.relative_to(ROOT).as_posix()
                with self.subTest(document=relative, asset=asset_path):
                    self.assertIn(asset_path, tracked, "Image exists only locally, not in Git")
                    self.assertTrue(asset.is_file())
                    if asset.suffix == ".png":
                        self.assertTrue(asset.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
                checked += 1
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
