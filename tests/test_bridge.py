import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from contextlib import contextmanager
from threading import Thread
import os
import polars as pl

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "src/compute-broker/scripts"
sys.path.insert(0, str(SCRIPTS))
import witness_bridge as b


class BridgeTests(unittest.TestCase):
    @contextmanager
    def server(self, handler):
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_transport_rejects_redirects_without_following_them(self):
        calls = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers.get("Content-Length", "0")))
                calls.append(self.path)
                self.send_response(307)
                self.send_header("Location", "/redirect-target")
                self.end_headers()

            def log_message(self, *args):
                pass

        with self.server(Handler) as base:
            with self.assertRaises(RuntimeError):
                b._post(base, "/api/ingest/observation", {"fixture": True})
        self.assertEqual(calls, ["/api/ingest/observation"])

    def test_transport_ignores_environment_proxy_and_bounds_response(self):
        class Handler(BaseHTTPRequestHandler):
            oversized = False

            def do_POST(self):
                self.rfile.read(int(self.headers.get("Content-Length", "0")))
                body = (
                    b"x" * 2_000_001
                    if self.oversized
                    else b'{"id":"00000000-0000-0000-0000-000000000001"}'
                )
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        with (
            self.server(Handler) as base,
            patch.dict(
                os.environ,
                {
                    "http_proxy": "http://127.0.0.1:1",
                    "HTTP_PROXY": "http://127.0.0.1:1",
                    "no_proxy": "",
                    "NO_PROXY": "",
                },
            ),
        ):
            self.assertEqual(
                b._post(base, "/api/ingest/observation", {})["id"],
                "00000000-0000-0000-0000-000000000001",
            )
            Handler.oversized = True
            with self.assertRaises(RuntimeError):
                b._post(base, "/api/ingest/observation", {})

    def test_transport_rejects_nonlocal_targets_and_nonfinite_payloads(self):
        with patch.object(b.urllib.request, "build_opener") as opener:
            for target in [
                "https://127.0.0.1",
                "http://example.com",
                "http://localhost:bad",
                "http://localhost?x=1",
                "http://user@localhost",
            ]:
                with self.assertRaises(ValueError):
                    b._post(target, "/api/ingest/observation", {})
            with self.assertRaises(ValueError):
                b._post(
                    "http://127.0.0.1",
                    "/api/ingest/observation",
                    {"value": float("nan")},
                )
            opener.assert_not_called()

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
