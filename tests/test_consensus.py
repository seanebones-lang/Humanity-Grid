import importlib.util
from pathlib import Path
import unittest
import polars as pl

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "consensus", ROOT / "src/compute-broker/scripts/validate_consensus.py"
)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def frame(ids=("a", "b", "c"), scores=(-6.0, -7.0, -8.0)):
    return pl.DataFrame({"compound_id": list(ids), "affinity_kcal_mol": list(scores)})


class ConsensusTests(unittest.TestCase):
    def test_invalid_sets_cannot_pass(self):
        for bad in [
            frame(("a", "a", "c")),
            frame(("a", "b", "d")),
            frame(scores=(1.0, 1.0, 1.0)),
            frame(scores=(None, -7.0, -8.0)),
            frame(scores=(float("nan"), -7.0, -8.0)),
            frame(("a",), (1.0,)),
        ]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                c.compute_consensus(frame(), bad)

    def test_matching_ignores_row_order(self):
        self.assertAlmostEqual(
            c.compute_consensus(frame(), frame(("c", "a", "b"), (-8.0, -6.0, -7.0))),
            1.0,
        )

    def test_frozen_scores_and_difference_outlier(self):
        directory = ROOT / "proofs/EXP-001-v1/outputs/vina"
        unit = next((directory / "rep1").iterdir()).name
        a, b = c.load_results(directory, unit, 1), c.load_results(directory, unit, 2)
        self.assertAlmostEqual(c.compute_consensus(a, b), 0.8849788400337059)
        self.assertEqual(
            c.difference_outliers(a, b)
            .filter(pl.col("is_outlier"))["compound_id"]
            .to_list(),
            ["CHEMBL495686"],
        )


if __name__ == "__main__":
    unittest.main()
