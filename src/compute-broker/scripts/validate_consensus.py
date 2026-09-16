#!/usr/bin/env python3
"""
Consensus validation for redundant work unit results.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl


def load_results(results_dir: Path, work_unit_id: str, replicate: int) -> pl.DataFrame:
    """Load results from a work unit replicate."""
    rep_dir = results_dir / f"rep{replicate}" / work_unit_id
    result_file = rep_dir / "results.parquet"
    if not result_file.exists():
        # Try alternative naming
        result_file = rep_dir / f"results_{work_unit_id}.parquet"
    if not result_file.exists():
        raise FileNotFoundError(f"Results not found: {result_file}")
    return pl.read_parquet(result_file)


def compute_consensus(df1: pl.DataFrame, df2: pl.DataFrame, key: str = "compound_id", score: str = "affinity_kcal_mol") -> float:
    """Compute Pearson correlation between two result sets on common compounds."""
    # Join on compound_id
    merged = df1.select([key, score]).join(
        df2.select([key, score]),
        on=key,
        how="inner",
        suffix="_rep2"
    )
    
    if len(merged) < 2:
        return 0.0
    
    scores1 = merged[score].to_numpy()
    scores2 = merged[f"{score}_rep2"].to_numpy()
    
    # Pearson correlation
    corr = np.corrcoef(scores1, scores2)[0, 1]
    return float(corr) if not np.isnan(corr) else 0.0


def detect_outliers_iqr(df: pl.DataFrame, score: str = "affinity_kcal_mol", factor: float = 1.5) -> pl.DataFrame:
    """Flag outliers using IQR method."""
    q1 = df[score].quantile(0.25)
    q3 = df[score].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - factor * iqr
    upper = q3 + factor * iqr
    
    return df.with_columns(
        pl.when((pl.col(score) < lower) | (pl.col(score) > upper))
        .then(True)
        .otherwise(False)
        .alias("is_outlier")
    )


def main():
    parser = argparse.ArgumentParser(description="Validate consensus between replicates")
    parser.add_argument("--job-id", required=True, help="Job ID")
    parser.add_argument("--results-dir", type=Path, required=True, help="Results directory with rep1/, rep2/, etc.")
    parser.add_argument("--redundancy", type=int, default=2, help="Number of replicates")
    parser.add_argument("--threshold", type=float, default=0.8, help="Consensus correlation threshold")
    parser.add_argument("--output", type=Path, help="Output JSON report")
    args = parser.parse_args()

    results_dir = args.results_dir
    redundancy = args.redundancy
    threshold = args.threshold

    # Find all work unit directories in rep1
    rep1_dir = results_dir / "rep1"
    if not rep1_dir.exists():
        print(f"ERROR: {rep1_dir} not found", file=sys.stderr)
        sys.exit(1)

    work_unit_dirs = [d for d in rep1_dir.iterdir() if d.is_dir()]
    print(f"Found {len(work_unit_dirs)} work units")

    report = {
        "job_id": args.job_id,
        "redundancy": redundancy,
        "threshold": threshold,
        "work_units": [],
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "mean_correlation": 0.0,
        }
    }

    correlations = []

    for wu_dir in work_unit_dirs:
        work_unit_id = wu_dir.name
        print(f"\nValidating {work_unit_id}...")

        wu_report = {
            "work_unit_id": work_unit_id,
            "replicates": redundancy,
            "correlations": {},
            "passed": True,
            "errors": []
        }

        try:
            # Load all replicates
            replicates = []
            for rep in range(1, redundancy + 1):
                df = load_results(results_dir, work_unit_id, rep)
                replicates.append(df)
                print(f"  Rep {rep}: {len(df)} compounds")

            # Pairwise correlations
            for i in range(redundancy):
                for j in range(i + 1, redundancy):
                    corr = compute_consensus(replicates[i], replicates[j])
                    pair_key = f"rep{i+1}_vs_rep{j+1}"
                    wu_report["correlations"][pair_key] = corr
                    correlations.append(corr)
                    print(f"  {pair_key}: r = {corr:.4f}")

            # Check if all pairs pass threshold
            min_corr = min(wu_report["correlations"].values()) if wu_report["correlations"] else 0.0
            if min_corr < threshold:
                wu_report["passed"] = False
                wu_report["errors"].append(f"Consensus below threshold: {min_corr:.4f} < {threshold}")

            # Outlier detection on first replicate (representative)
            if replicates:
                df_with_outliers = detect_outliers_iqr(replicates[0])
                n_outliers = df_with_outliers["is_outlier"].sum()
                wu_report["outliers"] = int(n_outliers)
                if n_outliers > 0:
                    print(f"  Outliers detected: {n_outliers}")

        except Exception as e:
            wu_report["passed"] = False
            wu_report["errors"].append(str(e))
            print(f"  ERROR: {e}")

        report["work_units"].append(wu_report)

    # Summary
    report["summary"]["total"] = len(report["work_units"])
    report["summary"]["passed"] = sum(1 for wu in report["work_units"] if wu["passed"])
    report["summary"]["failed"] = report["summary"]["total"] - report["summary"]["passed"]
    report["summary"]["mean_correlation"] = float(np.mean(correlations)) if correlations else 0.0

    print(f"\n{'='*50}")
    print(f"SUMMARY: {report['summary']['passed']}/{report['summary']['total']} work units passed consensus")
    print(f"Mean correlation: {report['summary']['mean_correlation']:.4f}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"Report written to {args.output}")

    # Exit code: 0 if all passed, 1 if any failed
    sys.exit(0 if report["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()