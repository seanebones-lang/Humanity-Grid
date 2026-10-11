#!/usr/bin/env python3
"""Exercise historical replay against a real disposable loopback Witness binary."""

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import ingest_exp001 as replay


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    args = parser.parse_args()
    binary = args.binary.resolve()
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    with tempfile.TemporaryDirectory(prefix="humanity-grid-replay-") as tmp:
        directory = Path(tmp)
        env = dict(
            os.environ,
            DATABASE_URL="sqlite://" + str(directory / "review.db"),
            HOST="127.0.0.1",
            PORT=str(port),
        )
        with (directory / "api.log").open("w") as log:
            server = subprocess.Popen(
                [str(binary)], cwd=directory, env=env, stdout=log, stderr=log
            )
            try:
                for attempt in range(100):
                    if server.poll() is not None:
                        raise RuntimeError(
                            "Witness exited before readiness: "
                            + (directory / "api.log").read_text()
                        )
                    try:
                        with urllib.request.urlopen(
                            base + "/health", timeout=0.5
                        ) as response:
                            if response.status == 200:
                                break
                    except OSError:
                        time.sleep(0.1)
                else:
                    raise RuntimeError("Witness readiness timed out")
                snapshots = []
                for iteration in range(2):
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(ROOT / "ingest_exp001.py"),
                            "--witness",
                            base,
                        ],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.returncode:
                        raise RuntimeError(result.stderr + result.stdout)
                    snapshots.append(
                        {
                            kind: replay.list_records(base, kind)
                            for kind in ["observed", "inferred", "generated"]
                        }
                    )
                if snapshots[0] != snapshots[1]:
                    raise RuntimeError("Replay changed records on reuse")
                if not replay.verify_ingestion(base):
                    raise RuntimeError("Replay graph validation failed")
                # Add a valid API record that conflicts with the replay identity. A later replay must refuse it without adding anything.
                replay.requests.post(
                    base + "/api/ingest/observation",
                    json={
                        "quantity": "conflicting-fixture",
                        "value": "999",
                        "unit": "kcal/mol",
                        "instrument_id": "synthetic-fixture",
                        "author_id": "synthetic:test",
                        "labels": ["EXP-001", "CHEMBL331829", "seed-101"],
                        "domain": "synthetic-test",
                    },
                )
                before = {
                    kind: replay.list_records(base, kind) for kind in snapshots[0]
                }
                rejected = subprocess.run(
                    [sys.executable, str(ROOT / "ingest_exp001.py"), "--witness", base],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                after = {kind: replay.list_records(base, kind) for kind in snapshots[0]}
                if rejected.returncode == 0 or before != after:
                    raise RuntimeError(
                        "Conflicting replay was not rejected without new writes"
                    )
                print(
                    json.dumps(
                        {
                            "status": "passed",
                            "first_replay_counts": {
                                k: len(v) for k, v in snapshots[0].items()
                            },
                            "second_replay": "same records and fields",
                            "conflicting_identity": "rejected without writes",
                            "working_directory": "outside source",
                            "boundary": "historical replay only; no docking or model calls",
                        },
                        indent=2,
                    )
                )
            finally:
                server.terminate()
                try:
                    server.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()


if __name__ == "__main__":
    main()
