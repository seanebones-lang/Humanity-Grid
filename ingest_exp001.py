#!/usr/bin/env python3
"""
Idempotent EXP-001 ingestion into Witness.

Ingests:
- 12 Observed records (6 compounds × 2 replicates)
- 2 Inferred records (consensus + failed attempt)
- 1 Generated record (Research Scout hypothesis)

Uses Witness REST ingest endpoints. Detects existing records to avoid duplication.
"""

import argparse
import json
import os
import requests
import sys
from datetime import datetime, timezone
from typing import Optional

DEFAULT_WITNESS_API = "http://127.0.0.1:8080"

# EXP-001 data
COMPOUNDS = [
    ("CHEMBL331829", -6.927, -6.740),
    ("CHEMBL434844", -6.856, -6.865),
    ("CHEMBL2106406", -7.847, -7.847),
    ("CHEMBL363112", -6.567, -6.542),
    ("CHEMBL495686", -7.027, -7.597),
    ("CHEMBL1234501", -6.593, -6.532),
]

REPLICATES = [
    {"seed": 101, "timestamp": "2026-09-16T20:15:00Z", "label": "replicate-1"},
    {"seed": 202, "timestamp": "2026-09-16T20:18:00Z", "label": "replicate-2"},
]

INSTRUMENT_AUTHOR = {
    "author_id": "instrument:autodock-vina-1.2.5",
    "author_name": "AutoDock Vina 1.2.5",
    "author_type": "instrument",
}

ANALYST_AUTHOR = {
    "author_id": "human:validation-pipeline",
    "author_name": "Humanity Grid Validation Pipeline",
    "author_type": "software",
}

SCOUT_AUTHOR = {
    "author_id": "model:research-scout",
    "author_name": "Research Scout (phi-3-mini-4k-instruct)",
    "author_type": "model",
}

def check_existing_observed(witness_api: str, compound_id: str, seed: int) -> Optional[str]:
    """Check if an observed record for this compound+seed already exists."""
    try:
        resp = requests.get(
            f"{witness_api}/api/nodes",
            params={"label": compound_id, "limit": 5, "type": "observed"},
            timeout=10
        )
        if resp.ok:
            data = resp.json()
            for node in data.get("nodes", []):
                labels = node.get("labels", [])
                if "EXP-001" in labels and compound_id in labels and f"seed-{seed}" in labels:
                    return node["id"]
    except Exception as e:
        print(f"Warning: Could not check existing records: {e}")
    return None

def ingest_observation(witness_api: str, compound_id: str, seed: int, affinity: float, timestamp: str, label: str) -> str:
    """Ingest a single observed docking measurement."""
    existing = check_existing_observed(witness_api, compound_id, seed)
    if existing:
        print(f"  [REUSE] {compound_id} seed={seed} -> {existing}")
        return existing

    payload = {
        "quantity": "docking_affinity",
        "value": str(affinity),
        "unit": "kcal/mol",
        "measured_at": timestamp,
        "instrument_id": "autodock-vina-1.2.5",
        "instrument_name": "AutoDock Vina",
        "author_id": INSTRUMENT_AUTHOR["author_id"],
        "author_name": INSTRUMENT_AUTHOR["author_name"],
        "author_type": INSTRUMENT_AUTHOR["author_type"],
        "labels": ["EXP-001", label, f"seed-{seed}", "cdk2", "1KE7", compound_id],
        "domain": "computational-chemistry",
        "source_uri": f"humanity-grid://EXP-001/{label}/cdk2-wu-001/results.parquet",
    }

    resp = requests.post(f"{witness_api}/api/ingest/observation", json=payload, timeout=30)
    if not resp.ok:
        raise RuntimeError(f"Failed to ingest observation: {resp.status_code} {resp.text}")
    
    result = resp.json()
    print(f"  [CREATE] {compound_id} seed={seed} -> {result['id']} (CID: {result['cid'][:16]}...)")
    return result["id"]

def check_existing_inference(witness_api: str, label: str) -> Optional[str]:
    """Check if an inferred record with this label exists."""
    try:
        resp = requests.get(
            f"{witness_api}/api/nodes",
            params={"label": label, "limit": 5, "type": "inferred"},
            timeout=10
        )
        if resp.ok:
            data = resp.json()
            for node in data.get("nodes", []):
                labels = node.get("labels", [])
                if "EXP-001" in labels and label in labels:
                    return node["id"]
    except Exception as e:
        print(f"Warning: Could not check existing inference: {e}")
    return None

def ingest_consensus_inference(witness_api: str, observed_ids: list[str]) -> str:
    """Ingest the consensus inference."""
    existing = check_existing_inference(witness_api, "consensus")
    if existing:
        print(f"  [REUSE] consensus inference -> {existing}")
        return existing

    payload = {
        "premises": observed_ids,
        "methodology": "Pearson correlation between two independent AutoDock Vina replicates (seeds 101 and 202) on six known CDK2 actives. Consensus threshold r >= 0.80. Outlier detection via IQR on per-compound replicate differences.",
        "claim": "The two specified Vina runs (seeds 101 and 202) have Pearson r = 0.885 across six docking scores, exceeding the predeclared r >= 0.80 agreement threshold. This establishes agreement between those runs only; it does not establish biological efficacy or predictive validity.",
        "claim_type": "correlative",
        "claim_scope": "specific",
        "falsifiers": [
            {
                "description": "A third independent Vina replicate with a different seed produces docking scores that correlate with the first two replicates at r < 0.80",
                "measurement_type": "docking_affinity",
                "timeframe": "Any future replication",
                "status": "pending"
            },
            {
                "description": "Experimental binding assays (ITC, SPR) for the six compounds contradict the predicted rank order from the consensus docking scores",
                "measurement_type": "experimental_binding_affinity",
                "timeframe": "When experimental data available",
                "status": "pending"
            },
            {
                "description": "Using a different binding-site center (e.g., the earlier incorrect fabricated center) yields r < 0.80 or reversed rank order",
                "measurement_type": "docking_affinity",
                "timeframe": "Already observed in failed attempt",
                "status": "completed-falsified"
            }
        ],
        "inference_uncertainty": 0.115,
        "author_id": ANALYST_AUTHOR["author_id"],
        "author_name": ANALYST_AUTHOR["author_name"],
        "author_type": ANALYST_AUTHOR["author_type"],
        "labels": ["EXP-001", "consensus", "validation", "pearson-r=0.885", "threshold=0.80", "passed", "outliers=1"],
        "domain": "computational-chemistry",
        "source_uri": "humanity-grid://EXP-001/validation/output/results/consensus.json",
    }

    resp = requests.post(f"{witness_api}/api/ingest/inference", json=payload, timeout=30)
    if not resp.ok:
        raise RuntimeError(f"Failed to ingest consensus inference: {resp.status_code} {resp.text}")
    
    result = resp.json()
    print(f"  [CREATE] consensus inference -> {result['id']} (CID: {result['cid'][:16]}...)")
    return result["id"]

def ingest_failed_attempt_inference(witness_api: str) -> str:
    """Ingest the failed attempt inference (provenance)."""
    existing = check_existing_inference(witness_api, "failed-attempt")
    if existing:
        print(f"  [REUSE] failed attempt inference -> {existing}")
        return existing

    payload = {
        "premises": [],
        "methodology": "AutoDock Vina with an incorrect/fabricated binding-site center (not the LS3 co-crystallized pocket). Produced near-zero/meaningless docking scores with no correlation to known actives. The assumption was challenged by comparing to the actual LS3 pocket coordinates from the 1KE7 structure. Experiment was rerun with corrected center.",
        "claim": "An earlier docking attempt used an incorrect binding-site center and was superseded after comparison with the LS3 co-crystallized ligand pocket in PDB 1KE7.",
        "claim_type": "descriptive",
        "claim_scope": "specific",
        "falsifiers": [
            {
                "description": "Evidence that the original incorrect center was actually valid for CDK2 docking",
                "measurement_type": "structural_biology",
                "timeframe": "Historical",
                "status": "completed-falsified"
            }
        ],
        "inference_uncertainty": None,
        "author_id": ANALYST_AUTHOR["author_id"],
        "author_name": ANALYST_AUTHOR["author_name"],
        "author_type": ANALYST_AUTHOR["author_type"],
        "labels": ["EXP-001", "failed-attempt", "provenance", "correction", "binding-site-error"],
        "domain": "computational-chemistry",
        "source_uri": "humanity-grid://EXP-001/validation/output/results/consensus.json",
    }

    resp = requests.post(f"{witness_api}/api/ingest/inference", json=payload, timeout=30)
    if not resp.ok:
        raise RuntimeError(f"Failed to ingest failed attempt inference: {resp.status_code} {resp.text}")
    
    result = resp.json()
    print(f"  [CREATE] failed attempt inference -> {result['id']} (CID: {result['cid'][:16]}...)")
    return result["id"]

def check_existing_generation(witness_api: str) -> Optional[str]:
    """Check if the hypothesis generation already exists."""
    try:
        resp = requests.get(
            f"{witness_api}/api/nodes",
            params={"label": "hypothesis", "limit": 5, "type": "generated"},
            timeout=10
        )
        if resp.ok:
            data = resp.json()
            for node in data.get("nodes", []):
                labels = node.get("labels", [])
                if "EXP-001" in labels and "hypothesis" in labels and "research-scout" in labels:
                    return node["id"]
    except Exception as e:
        print(f"Warning: Could not check existing generation: {e}")
    return None

def ingest_generation(witness_api: str) -> str:
    """Ingest the Research Scout hypothesis."""
    existing = check_existing_generation(witness_api)
    if existing:
        print(f"  [REUSE] hypothesis generation -> {existing}")
        return existing

    payload = {
        "content": "Hypothesis: six known CDK2 inhibitors from ChEMBL will show agreement between two specified AutoDock Vina runs using the LS3 pocket in PDB 1KE7.",
        "generator": "microsoft/phi-3-mini-4k-instruct",
        "model_version": "phi-3-mini-4k-instruct",
        "prompt": "Generate a testable hypothesis for CDK2 inhibition validation using known actives from ChEMBL",
        "human_reviewed": False,
        "author_id": SCOUT_AUTHOR["author_id"],
        "author_name": SCOUT_AUTHOR["author_name"],
        "labels": ["EXP-001", "hypothesis", "research-scout", "human_reviewed:false"],
        "domain": "computational-chemistry",
        "source_uri": "humanity-grid://EXP-001/research-scout",
    }

    resp = requests.post(f"{witness_api}/api/ingest/generation", json=payload, timeout=30)
    if not resp.ok:
        raise RuntimeError(f"Failed to ingest generation: {resp.status_code} {resp.text}")
    
    result = resp.json()
    print(f"  [CREATE] hypothesis generation -> {result['id']} (CID: {result['cid'][:16]}...)")
    return result["id"]

def verify_ingestion(witness_api: str) -> bool:
    """Verify all EXP-001 records are in Witness."""
    print("\n=== VERIFICATION ===")
    
    # Count observed
    resp = requests.get(f"{witness_api}/api/nodes", params={"label": "EXP-001", "type": "observed", "limit": 50})
    observed = resp.json()["nodes"] if resp.ok else []
    print(f"Observed EXP-001 records: {len(observed)} (expected 12)")
    
    # Count inferred
    resp = requests.get(f"{witness_api}/api/nodes", params={"label": "EXP-001", "type": "inferred", "limit": 50})
    inferred = resp.json()["nodes"] if resp.ok else []
    print(f"Inferred EXP-001 records: {len(inferred)} (expected 2)")
    
    # Count generated
    resp = requests.get(f"{witness_api}/api/nodes", params={"label": "EXP-001", "type": "generated", "limit": 50})
    generated = resp.json()["nodes"] if resp.ok else []
    print(f"Generated EXP-001 records: {len(generated)} (expected 1)")
    
    # Verify hypothesis human_reviewed=false
    if generated:
        node = generated[0]
        if "human_reviewed:false" in node.get("labels", []):
            print("✓ Hypothesis correctly marked human_reviewed:false")
        else:
            print("✗ Hypothesis missing human_reviewed:false label")
    
    # Verify outlier compound exists in data
    for node in observed:
        labels = node.get("labels", [])
        if "CHEMBL495686" in labels:
            print(f"✓ CHEMBL495686 outlier present in Witness")
            break
    
    # Check premises
    consensus = next((inf for inf in inferred if "consensus" in inf.get("labels", [])), None)
    if consensus:
        parents = consensus.get("parents", [])
        print(f"Inference {consensus['id'][:8]}... has {len(parents)} premises")

    if consensus and len(consensus.get("parents", [])) != 12:
        print("✗ Consensus inference does not link all 12 observed records")
        return False
    
    return len(observed) == 12 and len(inferred) == 2 and len(generated) == 1

def main() -> int:
    parser = argparse.ArgumentParser(description="Idempotently deposit and verify the frozen EXP-001 Proof A record in Witness.")
    parser.add_argument("--witness", default=os.environ.get("WITNESS_API", DEFAULT_WITNESS_API), help="Witness API base URL (default: %(default)s)")
    args = parser.parse_args()
    witness_api = args.witness.rstrip("/")
    print("=== EXP-001 Idempotent Witness Ingestion ===\n")
    
    # Check server
    try:
        resp = requests.get(f"{witness_api}/health", timeout=5)
        if not resp.ok:
            print(f"Witness API not healthy: {resp.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"Cannot reach Witness API at {witness_api}: {e}")
        print("Start Witness first; see Witness INSTALL.md for the one-command local server.")
        return 1
    
    print("Witness API reachable.\n")
    
    # 1. Ingest 12 Observed records
    print("1. Ingesting 12 Observed records (6 compounds × 2 replicates)...")
    observed_ids = []
    for compound_id, r1, r2 in COMPOUNDS:
        for rep in REPLICATES:
            affinity = r1 if rep["seed"] == 101 else r2
            oid = ingest_observation(witness_api, compound_id, rep["seed"], affinity, rep["timestamp"], rep["label"])
            observed_ids.append(oid)
    
    # 2. Ingest 2 Inferred records
    print("\n2. Ingesting Inferred records...")
    consensus_id = ingest_consensus_inference(witness_api, observed_ids)
    failed_id = ingest_failed_attempt_inference(witness_api)
    inferred_ids = [consensus_id, failed_id]
    
    # 3. Ingest 1 Generated record
    print("\n3. Ingesting Generated record...")
    hypothesis_id = ingest_generation(witness_api)
    
    # 4. Verify
    print("\n4. Verifying ingestion...")
    success = verify_ingestion(witness_api)
    
    print("\n=== SUMMARY ===")
    print(f"Observed:  {len(observed_ids)} records")
    print(f"Inferred:  {len(inferred_ids)} records")  
    print(f"Generated: 1 record")
    print(f"\nIdempotent: Re-run this script to verify no duplicates created")
    
    if success:
        print("\n✓ All records verified successfully!")
        return 0
    else:
        print("\n✗ Verification failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
