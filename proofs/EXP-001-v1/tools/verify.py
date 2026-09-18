#!/usr/bin/env python3
"""Verify the frozen EXP-001 Proof A package without network access."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    print(f"FAILED: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "manifest.json").read_text())
    for artifact in manifest["artifacts"]:
        path = root / artifact["path"]
        if not path.is_file():
            fail(f"missing {artifact['path']}")
        if path.stat().st_size != artifact["bytes"]:
            fail(f"size mismatch for {artifact['path']}")
        if sha256(path) != artifact["sha256"]:
            fail(f"SHA-256 mismatch for {artifact['path']}")
    print(f"VERIFIED: {len(manifest['artifacts'])} package artifacts match SHA-256 and byte counts")

    consensus = json.loads((root / "outputs/consensus.json").read_text())
    unit = consensus["work_units"][0]
    correlation = unit["correlations"]["rep1_vs_rep2"]
    if consensus["summary"] != {"total": 1, "passed": 1, "failed": 0, "mean_correlation": correlation}:
        fail("unexpected consensus summary")
    if not unit["passed"] or unit["outliers"] != 1 or abs(correlation - 0.8849788400337059) > 1e-15:
        fail("unexpected frozen consensus result")
    print("VERIFIED: frozen consensus reports 1/1 pass, r=0.8849788400337059, and one outlier")

    records = json.loads((root / "outputs/witness/records.json").read_text())
    counts = {kind: sum(r["epistemic_type"] == kind for r in records) for kind in ("observed", "inferred", "generated")}
    if counts != {"observed": 12, "inferred": 2, "generated": 1}:
        fail(f"unexpected Witness record counts: {counts}")
    consensus_records = [r for r in records if "consensus" in json.loads(r["labels"])]
    if len(consensus_records) != 1 or len(json.loads(consensus_records[0]["parents"])) != 12:
        fail("consensus record does not link exactly twelve premises")
    generated = [r for r in records if r["epistemic_type"] == "generated"]
    if "human_reviewed:false" not in json.loads(generated[0]["labels"]):
        fail("generated hypothesis lacks human_reviewed:false label")
    print("VERIFIED: Witness export contains 12 Observed, 2 Inferred, 1 Generated; consensus links 12 premises")

    database = root / "outputs/witness/proof-a-review.db"
    with sqlite3.connect(database) as connection:
        database_ids = {row[0] for row in connection.execute("SELECT id FROM nodes WHERE labels LIKE '%EXP-001%'")}
    if database_ids != {record["id"] for record in records}:
        fail("Witness database and JSON export identify different EXP-001 records")
    print("VERIFIED: Witness SQLite snapshot and JSON export identify the same EXP-001 records")
    print("NOT VERIFIED: source identity, molecular-docking correctness, independent execution, biological activity, efficacy, or truth")


if __name__ == "__main__":
    main()
