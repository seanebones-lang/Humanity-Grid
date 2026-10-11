import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("replay", ROOT / "ingest_exp001.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class ReplayTests(unittest.TestCase):
    def test_pagination_checks_beyond_first_page(self):
        pages = [
            r.Response(
                {"nodes": [{"id": str(i)} for i in range(100)], "total_count": 101}, 200
            ),
            r.Response({"nodes": [{"id": "last"}], "total_count": 101}, 200),
        ]
        with patch.object(r.requests, "get", side_effect=pages):
            self.assertEqual(
                r.list_records("http://localhost:8080", "observed")[-1]["id"], "last"
            )

    def test_failed_lookup_does_not_create_record(self):
        with (
            patch.object(r.requests, "get", side_effect=RuntimeError("unavailable")),
            patch.object(r.requests, "post") as post,
        ):
            with self.assertRaises(RuntimeError):
                r.ingest_observation(
                    "http://localhost:8080",
                    "CHEMBL331829",
                    101,
                    -6.927,
                    r.REPLICATES[0]["timestamp"],
                    "replicate-1",
                )
            post.assert_not_called()

    def test_labels_alone_do_not_establish_identity(self):
        fake = {
            "id": "not-valid",
            "labels": ["EXP-001", "CHEMBL331829", "seed-101"],
            "payload": {},
        }
        with (
            patch.object(r, "list_records", return_value=[fake]),
            patch.object(r.requests, "post") as post,
        ):
            with self.assertRaises(RuntimeError):
                r.ingest_observation(
                    "http://localhost:8080",
                    "CHEMBL331829",
                    101,
                    -6.927,
                    r.REPLICATES[0]["timestamp"],
                    "replicate-1",
                )
            post.assert_not_called()

    def test_remote_or_credential_urls_are_rejected(self):
        for url in [
            "https://localhost",
            "http://example.com",
            "http://localhost@evil.com",
            "http://localhost:8080/other",
            "http://localhost?x=1",
        ]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                r.local_url(url)

    def test_incomplete_page_is_not_treated_as_absence(self):
        with patch.object(
            r.requests,
            "get",
            return_value=r.Response({"nodes": [], "total_count": 1}, 200),
        ):
            with self.assertRaises(RuntimeError):
                r.list_records("http://localhost:8080", "observed")


if __name__ == "__main__":
    unittest.main()
