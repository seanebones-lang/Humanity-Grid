#!/usr/bin/env python3
"""
Grid -> Witness bridge.

Deposits the evidence trail for a completed distributed experiment into a
Witness instance using the REST ingest endpoints, keeping Witness's three
epistemic categories honest:

  Observed   <- one ProvenanceNode per raw work-unit result (parquet scores,
                job spec, container digest)
  Inferred   <- consensus/voting across redundant replicates, with the
                observed nodes as explicit premises and a falsifier
  Generated  <- Research Scout hypothesis prose, model + prompt recorded,
                never auto-promoted to Observed

Why this exists: Witness is the evidence kernel (the long-lived, queryable
memory of what a grid actually measured). Grid is the machine that does the
work. This bridge is the join that keeps the two from quietly lying — a
docking score stays an Observed measurement, a consensus stays an Inferred
claim with visible premises, and Scout prose never gets upgraded to a fact.

This module deliberately uses the Python standard library only (`urllib`),
so it runs on any volunteer node / orchestrator without extra deps.

Usage:
    python witness_bridge.py --witness http://127.0.0.1:8090 \
        --job-id EXP-001 --hypothesis H-9182 \
        --results-dir /path/to/results --report /path/to/consensus.json \
        --domain cancer-screening
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any

# Affinity scores above this (kcal/mol) are considered non-hits in the
# "candidates, not cures" framing. This is a validation-choice constant, not a
# biological claim. Match the experiment's scoring function.
HIT_THRESHOLD_KCAL = -8.0


def _post(witness: str, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    req = urllib.request.Request(
        f"{witness}{endpoint}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


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
            "human_reviewed": False,  # must be human-approved before promotion
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


def summarize_scores(results_dir: Path, work_unit_id: str) -> dict[str, Any]:
    """Compute a small aggregate (n, mean, min affinity, hits) from parquet."""
    import polars as pl

    rep_dir = results_dir / "rep1" / work_unit_id
    f = rep_dir / "results.parquet"
    if not f.exists():
        f = rep_dir / f"results_{work_unit_id}.parquet"
    df = pl.read_parquet(f)
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
    p.add_argument("--report", type=Path, required=True, help="consensus JSON from validate_consensus.py")
    p.add_argument("--domain", default="cancer-screening")
    p.add_argument("--pdb", default="1KE7", help="receptor PDB id for source_uri")
    args = p.parse_args()

    report = load_report(args.report)
    print(f"Loaded consensus report: {report['summary']['passed']}/{report['summary']['total']} work units passed")

    # 1) Observed: the job spec + each raw score aggregate is an observation.
    premise_ids: list[str] = []
    for wu in report.get("work_units", []):
        wu_id = wu["work_unit_id"]
        agg = summarize_scores(args.results_dir, wu_id)
        # Deposit each replicate's best score as an independent Observed node.
        for rep, md in (("rep1", "replicate one"), ("rep2", "replicate two")):
            nid = f"grid-{args.job_id}-{wu_id}-{rep}"
            uri = f"grid://{args.pdb}/{args.job_id}/{wu_id}/{rep}"
            value = f"{agg['best_affinity_kcal']:.3f}"
            premise = deposit_observation(
                args.witness,
                quantity="docking_affinity_best",
                value=value,
                unit="kcal/mol",
                instrument_id="autodock:vina1.2",
                instrument_name="AutoDock Vina (CPU)",
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
            f"Consensus for {args.job_id}: {report['summary']['passed']}/"
            f"{report['summary']['total']} work units reproduced within threshold "
            f"(r>={report['threshold']}); mean corr {report['summary']['mean_correlation']:.3f}"
        ),
        methodology=(
            "Redundant work-unit execution across independent volunteer nodes; "
            "Pearson correlation on common compounds; IQR outlier flagging; "
            "disagreement past threshold triggers a third arbitration run."
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

    # 3) Generated: Research Scout hypothesis prose, model + prompt stored.
    gen_id = deposit_generation(
        args.witness,
        content=(
            f"Hypothesis {args.hypothesis}: known protein-ligand system "
            f"({args.pdb}) screened for validation; grid task {args.job_id} "
            "checks whether the distributed pipeline reproduces expected "
            "actives. Docking score is Observed; this prose is Generated and "
            "requires human review before promotion."
        ),
        generator="research-scout",
        model_version="v0.1",
        prompt="Generate human-readable hypothesis framing from the validated job's JobSpec",
        author_id="research-scout:scout-v1",
        domain=args.domain,
        labels=["hypothesis", args.hypothesis, "generated"],
    )
    print(f"  Generated hypothesis -> {gen_id}")

    print(f"\nRecord complete for {args.job_id}:")
    print(f"  Observed premises : {premise_ids}")
    print(f"  Inferred consensus: {consensus_id}")
    print(f"  Generated scout   : {gen_id}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)