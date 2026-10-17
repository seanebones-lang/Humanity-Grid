import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "proofs/EXP-001-v1"
V2 = ROOT / "proofs/EXP-001-v2"


class CorrectedPackageTests(unittest.TestCase):
    def test_original_artifact_bytes_are_preserved_in_new_package(self):
        old = json.loads((V1 / "manifest.json").read_text())
        new = json.loads((V2 / "manifest.json").read_text())
        self.assertEqual(len(new["artifacts"]), 45)
        for item in old["artifacts"]:
            name = item["path"]
            if name == "outputs/consensus.json":
                name = "outputs/consensus-historical-v1.json"
            data = (V2 / name).read_bytes()
            self.assertEqual(len(data), item["bytes"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), item["sha256"])

    def test_byte_verifier_fails_if_a_manifested_pose_is_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(V2, package)
            next((package / "outputs/vina/rep1").rglob("*_docked.pdbqt")).unlink()
            result = subprocess.run([sys.executable, str(package / "tools/verify.py")],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing", result.stderr)

    def test_current_report_matches_pinned_parquet_reanalysis(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            subprocess.run([
                sys.executable, str(ROOT / "src/compute-broker/scripts/validate_consensus.py"),
                "--job-id", "EXP-001", "--threshold", "0.8", "--results-dir",
                str(V2 / "outputs/vina"), "--output", str(output),
            ], check=True, capture_output=True)
            self.assertEqual(json.loads(output.read_text()),
                             json.loads((V2 / "outputs/consensus.json").read_text()))


if __name__ == "__main__":
    unittest.main()
