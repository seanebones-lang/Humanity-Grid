import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import polars as pl

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "src/compute-broker/scripts"
sys.path.insert(0, str(SCRIPTS))
import witness_bridge as b


class BridgeTests(unittest.TestCase):
    def fixture(self, root):
        for rep, scores in [(1, [-6.0, -7.0, -8.0]), (2, [-6.2, -7.2, -8.2])]:
            d = root / f"rep{rep}" / "unit"
            d.mkdir(parents=True)
            pl.DataFrame(
                {"compound_id": ["a", "b", "c"], "affinity_kcal_mol": scores}
            ).write_parquet(d / "results.parquet")
        report = {
            "job_id": "test-job",
            "redundancy": 2,
            "threshold": 0.8,
            "work_units": [
                {
                    "work_unit_id": "unit",
                    "passed": True,
                    "errors": [],
                    "correlations": {"rep1_vs_rep2": 1.0},
                }
            ],
            "summary": {"total": 1, "passed": 1, "failed": 0, "mean_correlation": 1.0},
        }
        p = root / "report.json"
        p.write_text(json.dumps(report))
        return p

    def test_replicates_keep_distinct_source_values_and_no_fake_model_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = self.fixture(root)
            args = [
                "bridge",
                "--job-id",
                "test-job",
                "--hypothesis",
                "fixture",
                "--results-dir",
                str(root),
                "--report",
                str(report),
            ]
            with (
                patch.object(sys, "argv", args),
                patch.object(
                    b, "_post", side_effect=lambda *a: {"id": str(len(a))}
                ) as post,
            ):
                self.assertEqual(b.main(), 0)
                values = [
                    call.args[2]["value"]
                    for call in post.call_args_list
                    if call.args[1].endswith("/observation")
                ]
                self.assertEqual(values, ["-8.0", "-8.2"])
                self.assertEqual(post.call_count, 3)

    def test_conflicting_report_is_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = self.fixture(root)
            report = json.loads(p.read_text())
            report["summary"]["mean_correlation"] = float("nan")
            p.write_text(json.dumps(report))
            with (
                patch.object(
                    sys,
                    "argv",
                    [
                        "bridge",
                        "--job-id",
                        "test-job",
                        "--hypothesis",
                        "fixture",
                        "--results-dir",
                        str(root),
                        "--report",
                        str(p),
                    ],
                ),
                patch.object(b, "_post") as post,
            ):
                with self.assertRaises(ValueError):
                    b.main()
                post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
