"""Use fictional docking results to check output isolation, not docking science."""

import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "vina_runner", ROOT / "validation/run_vina_replicate.py"
)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class ReplicatePreservationTests(unittest.TestCase):
    def invoke(self, output, seed):
        argv = ["runner", "--receptor", "fixture.pdbqt", "--out", str(output),
                "--seed", str(seed)]
        with patch.object(sys, "argv", argv):
            return runner.main()

    def test_seeds_have_distinct_outputs_and_rerun_cannot_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(runner, "obabel_pdbqt", return_value=True), patch.object(
                runner, "run_vina", side_effect=lambda *args: -float(args[-1])
            ) as docking:
                self.assertEqual(self.invoke(root / "rep1", 101), 0)
                self.assertEqual(self.invoke(root / "rep2", 202), 0)
                first = root / "rep1/cdk2-wu-001/results.parquet"
                second = root / "rep2/cdk2-wu-001/results.parquet"
                self.assertNotEqual(first.read_bytes(), second.read_bytes())
                self.assertEqual(pl.read_parquet(first).height, 6)
                before = first.read_bytes()
                docking.reset_mock()
                self.assertEqual(self.invoke(root / "rep1", 202), 1)
                docking.assert_not_called()
                self.assertEqual(first.read_bytes(), before)

    def test_partial_run_does_not_publish_a_score_set(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(runner, "obabel_pdbqt", return_value=True), patch.object(
                runner, "run_vina", side_effect=[-7.0, None]
            ):
                self.assertEqual(self.invoke(root, 101), 1)
            self.assertFalse((root / "cdk2-wu-001/results.parquet").exists())

    def test_success_can_print_to_a_legacy_windows_console(self):
        with tempfile.TemporaryDirectory() as directory:
            with io.TextIOWrapper(io.BytesIO(), encoding="cp1252") as console:
                with patch.object(sys, "stdout", console), patch.object(
                    runner, "obabel_pdbqt", return_value=True
                ), patch.object(runner, "run_vina", return_value=-7.0):
                    self.assertEqual(self.invoke(Path(directory), 101), 0)

    def test_failed_process_does_not_accept_a_written_pose(self):
        with tempfile.TemporaryDirectory() as directory:
            docked = Path(directory) / "pose.pdbqt"
            def failed_process(*args, **kwargs):
                docked.write_text("REMARK VINA RESULT: -7.0 0 0\n")
                return subprocess.CompletedProcess(args[0], 1)
            with patch.object(runner.subprocess, "run", side_effect=failed_process):
                self.assertIsNone(runner.run_vina(Path("r"), Path("l"), docked, 8, 101))

    def test_existing_pose_is_preserved_without_running_process(self):
        with tempfile.TemporaryDirectory() as directory:
            docked = Path(directory) / "pose.pdbqt"
            docked.write_text("historical pose")
            with patch.object(runner.subprocess, "run") as process:
                with self.assertRaises(FileExistsError):
                    runner.run_vina(Path("r"), Path("l"), docked, 8, 101)
                process.assert_not_called()
            self.assertEqual(docked.read_text(), "historical pose")

    def test_nonfinite_affinity_is_not_a_result(self):
        with tempfile.TemporaryDirectory() as directory:
            docked = Path(directory) / "pose.pdbqt"
            def nonfinite_process(*args, **kwargs):
                docked.write_text("REMARK VINA RESULT: nan 0 0\n")
                return subprocess.CompletedProcess(args[0], 0)
            with patch.object(runner.subprocess, "run", side_effect=nonfinite_process):
                self.assertIsNone(runner.run_vina(Path("r"), Path("l"), docked, 8, 101))

    def test_cli_reports_outlier_variable_fences_and_compound(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "consensus.json"
            subprocess.run([
                sys.executable, str(ROOT / "src/compute-broker/scripts/validate_consensus.py"),
                "--job-id", "EXP-001", "--results-dir",
                str(ROOT / "proofs/EXP-001-v1/outputs/vina"), "--output", str(report),
            ], check=True, capture_output=True)
            unit = json.loads(report.read_text())["work_units"][0]
            details = unit["outlier_details"]["rep1_vs_rep2"]
            self.assertEqual(details["variable"], "absolute_difference")
            self.assertEqual(details["quantile_interpolation"], "linear")
            self.assertEqual(details["factor"], 1.5)
            self.assertLess(details["upper_fence"], 0.570)
            self.assertEqual(details["flagged_compounds"][0]["compound_id"], "CHEMBL495686")
            self.assertAlmostEqual(details["flagged_compounds"][0]["absolute_difference"], 0.570)


if __name__ == "__main__":
    unittest.main()
