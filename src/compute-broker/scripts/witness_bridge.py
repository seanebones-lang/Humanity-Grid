#!/usr/bin/env python3
"""
Grid -> Witness bridge.

Deposits a local score-file review into a
Witness instance using the REST ingest endpoints, keeping Witness's three
epistemic categories honest:

  Observed   <- one minimum-score aggregate per supplied replicate file
  Inferred   <- consensus/voting across redundant replicates, with the
                observed nodes as explicit premises and a falsifier
  Generated  <- none; this script does not invoke a model

Why this exists: Witness is the evidence kernel (the long-lived, queryable
memory of what a grid actually measured). Grid is the machine that does the
work. This bridge is the join that keeps the two from quietly lying — a
docking score stays an Observed measurement, a consensus stays an Inferred
claim with visible premises, and Scout prose never gets upgraded to a fact.

HTTP transport uses urllib; score analysis requires the locked reviewer Python dependencies. This local bridge does not dispatch volunteer work or verify operator identity.

Usage:
    python witness_bridge.py --witness http://127.0.0.1:8090 \
        --job-id EXP-001 --hypothesis H-9182 \
        --results-dir /path/to/results --report /path/to/consensus.json \
        --domain cancer-screening
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
import ipaddress
from uuid import UUID

# Affinity scores above this (kcal/mol) are considered non-hits in the
# "candidates, not cures" framing. This is a validation-choice constant, not a
# biological claim. Match the experiment's scoring function.
HIT_THRESHOLD_KCAL = -8.0


def local_url(base: str) -> str:
    target = urlsplit(base)
    if (
        target.scheme != "http"
        or target.username
        or target.password
        or target.path not in ("", "/")
        or target.query
        or target.fragment
        or not target.hostname
    ):
        raise ValueError("Witness must be a plain loopback HTTP base URL")
    # Access port to reject malformed port numbers before any request.
    target.port
    if (
        target.hostname != "localhost"
        and not ipaddress.ip_address(target.hostname).is_loopback
    ):
        raise ValueError("This unauthenticated bridge supports loopback Witness only")
    return base.rstrip("/")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise RuntimeError("Redirects are not allowed during local deposit")


def _post(witness: str, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    if endpoint not in (
        "/api/ingest/observation",
        "/api/ingest/inference",
        "/api/ingest/generation",
    ):
        raise ValueError("Unsupported ingest endpoint")
    req = urllib.request.Request(
        f"{local_url(witness)}{endpoint}",
        data=json.dumps(payload, allow_nan=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(req, timeout=30) as resp:
        body = resp.read(2_000_001)
        if len(body) > 2_000_000:
            raise RuntimeError("Witness response exceeds bounded deposit limit")
        result = json.loads(body)
        if not isinstance(result, dict) or not isinstance(result.get("id"), str):
            raise ValueError("Witness ingest response must contain a node UUID")
        UUID(result["id"])
        return result


def deposit_observation(
    witness: str,
    *,
    quantity: str,
    value: str,
    unit: str,
    instrument_id: str,
    instrument_name: str,
    node_id: str,
    domain: str,
    source_uri: str,
    labels: list[str],
) -> str:
    """Deposit one Observed node; returns its Witness node UUID (premise)."""
    res = _post(
        witness,
        "/api/ingest/observation",
        {
            "quantity": quantity,
            "value": value,
            "unit": unit,
            "instrument_id": instrument_id,
            "instrument_name": instrument_name,
            "author_id": f"compute:{node_id}",
            "author_type": "instrument",
            "domain": domain,
            "source_uri": source_uri,
            "labels": labels,
        },
    )
    return res["id"]


def deposit_inference(
    witness: str,
    *,
    claim: str,
    methodology: str,
    premises: list[str],
    falsifiers: list[dict[str, str]],
    author_id: str,
    domain: str,
    labels: list[str],
    inference_uncertainty: float | None = None,
) -> str:
    """Deposit one Inferred node (consensus) referencing observed premises."""
    res = _post(
        witness,
        "/api/ingest/inference",
        {
            "claim": claim,
            "methodology": methodology,
            "premises": premises,
            "claim_type": "correlative",
            "claim_scope": "specific",
            "falsifiers": falsifiers,
            "inference_uncertainty": inference_uncertainty,
            "author_id": author_id,
            "author_type": "software",
            "domain": domain,
            "labels": labels,
        },
    )
    return res["id"]


def deposit_generation(
    witness: str,
    *,
    content: str,
    generator: str,
    model_version: str,
    prompt: str,
    author_id: str,
    domain: str,
    labels: list[str],
) -> str:
    """Deposit one Generated node (Research Scout hypothesis)."""
    res = _post(
        witness,
        "/api/ingest/generation",
        {
            "content": content,
            "generator": generator,
            "model_version": model_version,
            "prompt": prompt,
            "human_reviewed": False,  # review does not change epistemic type
            "author_id": author_id,
            "author_name": generator,
            "domain": domain,
            "labels": labels,
        },
    )
    return res["id"]


def load_report(report_path: Path) -> dict[str, Any]:
    with open(report_path) as f:
        return json.load(f)


def summarize_scores(
    results_dir: Path, work_unit_id: str, replicate: int
) -> dict[str, Any]:
    """Compute a small aggregate (n, mean, min affinity, hits) from parquet."""
    import polars as pl

    rep_dir = results_dir / f"rep{replicate}" / work_unit_id
    f = rep_dir / "results.parquet"
    if not f.exists():
        f = rep_dir / f"results_{work_unit_id}.parquet"
    df = pl.read_parquet(f)
    from validate_consensus import validate_scores

    validate_scores(df)
    affinity = df["affinity_kcal_mol"]
    hits = int((affinity < HIT_THRESHOLD_KCAL).sum())
    return {
        "n_compounds": int(len(df)),
        "mean_affinity_kcal": float(affinity.mean()),
        "best_affinity_kcal": float(affinity.min()),
        "hits_below_threshold": hits,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Grid -> Witness evidence bridge")
    p.add_argument("--witness", default="http://127.0.0.1:8090")
    p.add_argument("--job-id", required=True)
    p.add_argument("--hypothesis", required=True)
    p.add_argument("--results-dir", type=Path, required=True)
    p.add_argument(
        "--report",
        type=Path,
        required=True,
        help="consensus JSON from validate_consensus.py",
    )
    p.add_argument("--domain", default="cancer-screening")
    p.add_argument("--pdb", default="1KE7", help="receptor PDB id for source_uri")
    p.add_argument(
        "--instrument-id",
        default="local:score-file-review",
        help="Declared source instrument identity; not verified by this bridge",
    )
    p.add_argument("--instrument-name", default="Local supplied score files")
    args = p.parse_args()

    from validate_consensus import compute_consensus, load_results

    args.witness = local_url(args.witness)
    if (
        not args.instrument_id.strip()
        or not args.instrument_name.strip()
        or not args.hypothesis.strip()
    ):
        raise ValueError(
            "Nonblank source instrument and hypothesis identifiers required"
        )
    report = load_report(args.report)
    units = report.get("work_units", [])
    redundancy = report.get("redundancy", 0)
    if (
        report.get("job_id") != args.job_id
        or not units
        or not isinstance(redundancy, int)
        or redundancy < 2
    ):
        raise ValueError(
            "Nonempty report for this job with at least two replicates required"
        )
    threshold = report.get("threshold")
    if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
        raise ValueError("Finite threshold in [0, 1] required")
    prepared = {}
    recomputed = []
    for wu in units:
        uid = wu["work_unit_id"]
        if uid in prepared or Path(uid).name != uid or uid in (".", ".."):
            raise ValueError("Unique safe work-unit identifiers required")
        dfs = [
            load_results(args.results_dir, uid, rep) for rep in range(1, redundancy + 1)
        ]
        correlations = {}
        for i in range(redundancy):
            for j in range(i + 1, redundancy):
                correlations[f"rep{i + 1}_vs_rep{j + 1}"] = compute_consensus(
                    dfs[i], dfs[j]
                )
        if set(wu.get("correlations", {})) != set(correlations) or any(
            not math.isfinite(wu["correlations"][key])
            or abs(wu["correlations"][key] - value) > 1e-12
            for key, value in correlations.items()
        ):
            raise ValueError("Report correlations do not match source scores")
        passed = all(r >= threshold for r in correlations.values())
        if wu.get("passed") is not passed or wu.get("errors"):
            raise ValueError("Report status/errors disagree with source score analysis")
        prepared[uid] = [
            summarize_scores(args.results_dir, uid, rep)
            for rep in range(1, redundancy + 1)
        ]
        recomputed.extend(correlations.values())
    passed_count = sum(wu["passed"] for wu in units)
    expected_summary = {
        "total": len(units),
        "passed": passed_count,
        "failed": len(units) - passed_count,
    }
    if (
        any(report["summary"].get(k) != v for k, v in expected_summary.items())
        or not math.isfinite(report["summary"].get("mean_correlation", float("inf")))
        or abs(
            report["summary"].get("mean_correlation", float("inf"))
            - sum(recomputed) / len(recomputed)
        )
        > 1e-12
    ):
        raise ValueError("Report summary disagrees with source scores")
    print(
        f"Loaded consensus report: {report['summary']['passed']}/{report['summary']['total']} work units passed"
    )

    # 1) Observed: each supplied replicate's minimum-score aggregate.
    premise_ids: list[str] = []
    for wu in report.get("work_units", []):
        wu_id = wu["work_unit_id"]
        # All source scores are validated before the first write.
        for index, agg in enumerate(prepared[wu_id], 1):
            rep = f"rep{index}"
            nid = f"grid-{args.job_id}-{wu_id}-{rep}"
            uri = f"grid://{args.pdb}/{args.job_id}/{wu_id}/{rep}"
            value = str(agg["best_affinity_kcal"])
            premise = deposit_observation(
                args.witness,
                quantity="docking_affinity_best",
                value=value,
                unit="kcal/mol",
                instrument_id=args.instrument_id,
                instrument_name=args.instrument_name,
                node_id=nid,
                domain=args.domain,
                source_uri=uri,
                labels=["raw-score", rep, wu_id],
            )
            premise_ids.append(premise)
            print(f"  Observed [{rep}] {wu_id}: {value} kcal/mol -> {premise}")

    # 2) Inferred: consensus outcome over the observed premises, with falsifier.
    passed = report["summary"]["passed"] == report["summary"]["total"]
    consensus_id = deposit_inference(
        args.witness,
        claim=(
            f"Score-file consensus for {args.job_id} (hypothesis {args.hypothesis}): {report['summary']['passed']}/"
            f"{report['summary']['total']} work units reproduced within threshold "
            f"(r>={report['threshold']}); mean corr {report['summary']['mean_correlation']:.3f}"
        ),
        methodology=(
            "Local score-file review; Pearson correlation across complete matching compound sets. "
            "Premises are per-replicate minimum score aggregates, not the complete raw vectors. "
            "The source report was recomputed before deposit. No independent operators, volunteer dispatch, "
            "automatic arbitration, biological efficacy, or predictive validity are established."
        ),
        premises=premise_ids,
        falsifiers=[
            {
                "description": "A third independent work-unit run on the same slice disagrees past the consensus threshold",
                "measurement_type": "docking_affinity",
                "timeframe": "immediate",
                "status": "pending",
            }
        ],
        author_id="humanity-grid:consensus-engine",
        domain=args.domain,
        labels=["consensus", "passed" if passed else "failed"],
        inference_uncertainty=round(1.0 - report["summary"]["mean_correlation"], 3),
    )
    print(f"  Inferred consensus -> {consensus_id}")

    # No model call occurs here. Hand-written report framing is not falsely attributed to Research Scout.
    print(f"\nRecord complete for {args.job_id}:")
    print(f"  Observed premises : {premise_ids}")
    print(f"  Inferred consensus: {consensus_id}")
    print("  No Generated record: this bridge did not invoke a model")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
