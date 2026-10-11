from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import json

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/experiment-engine/src"))
from experiment_engine.jobs.spec import create_job_from_template, JobSpec

OVERRIDES = {
    "provenance": {
        "hypothesis_id": "test-hypothesis",
        "researcher_approval": "synthetic-test-only",
        "approval_timestamp": "2026-01-01T00:00:00Z",
        "git_commit": "synthetic",
    }
}


class JobTests(unittest.TestCase):
    def job(self):
        return create_job_from_template(
            "virtual_screening",
            "test-job",
            "test-hypothesis",
            "Synthetic test",
            OVERRIDES,
        )

    def test_hash_roundtrip_and_content_changes_are_rejected(self):
        job = self.job()
        copy = JobSpec.model_validate_json(job.to_json())
        self.assertEqual(job.provenance.spec_hash, copy.provenance.spec_hash)
        changed = json.loads(job.to_json())
        changed["compute"]["cpus"] = 100
        with self.assertRaises(ValueError):
            JobSpec.model_validate(changed)
        self.assertEqual(
            job.inputs["docking_parameters"].parameters["exhaustiveness"], 16
        )

    def test_creator_cli_preserves_provenance_and_computed_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "job.yml"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "src/experiment-engine/scripts/create_job.py"),
                    "--job-id",
                    "test-job",
                    "--hypothesis-id",
                    "test-hypothesis",
                    "--name",
                    "Synthetic test",
                    "--overrides",
                    json.dumps(OVERRIDES),
                    "--output",
                    str(output),
                ],
                check=True,
                capture_output=True,
            )
            job = JobSpec.from_yaml(output)
            self.assertEqual(job.provenance.researcher_approval, "synthetic-test-only")
            self.assertEqual(len(job.provenance.spec_hash), 64)

    def test_splitter_preserves_parameters_hashes_and_rejects_unimplemented_library_mode(
        self,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job = self.job()
            job.inputs["docking_parameters"].parameters["exhaustiveness"] = 23
            data = json.loads(job.to_json())
            data["provenance"]["spec_hash"] = None
            data["work_units"]["total"] = 2
            job = JobSpec.model_validate(data)
            source = root / "job.yaml"
            job.to_yaml(source)
            script = ROOT / "src/experiment-engine/scripts/split_work_units.py"
            subprocess.run(
                [
                    sys.executable,
                    str(script),
                    str(source),
                    "--output",
                    str(root / "units"),
                ],
                check=True,
                capture_output=True,
            )
            unit = json.loads((root / "units/wu_0000.json").read_text())
            self.assertEqual(unit["parameters"]["exhaustiveness"], 23)
            self.assertEqual(unit["job_spec_hash"], job.provenance.spec_hash)
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    str(source),
                    "--library-path",
                    "anything",
                ],
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_invalid_resources_and_redundancy(self):
        for key, value in [
            ("cpus", 0),
            ("memory_gb", 0),
            ("estimated_runtime_hours", float("inf")),
        ]:
            data = json.loads(self.job().to_json())
            data["compute"][key] = value
            data["provenance"]["spec_hash"] = None
            with self.assertRaises(ValueError):
                JobSpec.model_validate(data)


if __name__ == "__main__":
    unittest.main()
