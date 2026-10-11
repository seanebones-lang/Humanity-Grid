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


def check_bridge(base, directory):
    """Deposit distinct synthetic replica files through the real HTTP API."""
    import polars as pl

    results = directory / "synthetic-scores"
    for replicate, scores in [(1, [-6.0, -7.0, -8.0]), (2, [-6.2, -7.2, -8.2])]:
        unit = results / f"rep{replicate}" / "fixture"
        unit.mkdir(parents=True)
        pl.DataFrame(
            {"compound_id": ["a", "b", "c"], "affinity_kcal_mol": scores}
        ).write_parquet(unit / "results.parquet")
    report = directory / "synthetic-consensus.json"
    common = ["--job-id", "synthetic-integration", "--results-dir", str(results)]
    for arguments in [
        [
            str(ROOT / "src/compute-broker/scripts/validate_consensus.py"),
            *common,
            "--output",
            str(report),
        ],
        [
            str(ROOT / "src/compute-broker/scripts/witness_bridge.py"),
            *common,
            "--hypothesis",
            "synthetic-fixture",
            "--report",
            str(report),
            "--witness",
            base,
            "--domain",
            "synthetic-integration",
        ],
    ]:
        process = subprocess.run(
            [sys.executable, *arguments], capture_output=True, text=True, timeout=30
        )
        if process.returncode:
            raise RuntimeError(process.stderr + process.stdout)
    records = {}
    for kind in ("observed", "inferred", "generated"):
        records[kind] = replay.requests.get(
            base + "/api/nodes",
            params={"type": kind, "domain": "synthetic-integration", "limit": 100},
        ).json()["nodes"]
    if {kind: len(nodes) for kind, nodes in records.items()} != {
        "observed": 2,
        "inferred": 1,
        "generated": 0,
    }:
        raise RuntimeError("Generic bridge produced unexpected node types/counts")
    observed = records["observed"]
    if sorted(
        node["payload"]["measurement"]["value"]["numeric"] for node in observed
    ) != [-8.2, -8.0]:
        raise RuntimeError("Generic bridge lost the distinct source replicate values")
    if any(
        node["payload"]["measurement"]["instrument"]["id"] != "local:score-file-review"
        for node in observed
    ):
        raise RuntimeError("Generic bridge misattributed the supplied score files")
    inference = records["inferred"][0]
    expected = {node["id"] for node in observed}
    if (
        set(inference["parents"]) != expected
        or set(inference["payload"]["derivation"]["premises"]) != expected
    ):
        raise RuntimeError("Generic bridge inference lost its actual source premises")
    return {
        "counts": {kind: len(nodes) for kind, nodes in records.items()},
        "distinct_replicates": [-8.0, -8.2],
        "premises": "actual observation IDs",
        "boundary": "synthetic local files; no model or docking run",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument(
        "--check-bridge",
        action="store_true",
        help="Also check generic bridge with locked reviewer dependencies",
    )
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
                    if iteration == 0:
                        # A similarly named experiment must not enter the exact-label replay.
                        replay.requests.post(
                            base + "/api/ingest/observation",
                            json={
                                "quantity": "synthetic-prefix-fixture",
                                "value": "123",
                                "unit": "fixture",
                                "instrument_id": "synthetic-fixture",
                                "author_id": "synthetic:test",
                                "labels": ["EXP-001-backup"],
                                "domain": "synthetic-test",
                            },
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
                bridge_result = (
                    check_bridge(base, directory)
                    if args.check_bridge
                    else "not requested"
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
                            "prefix_label": "EXP-001-backup excluded from EXP-001 replay",
                            "working_directory": "outside source",
                            "boundary": "historical replay only; no docking or model calls",
                            "generic_bridge": bridge_result,
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
