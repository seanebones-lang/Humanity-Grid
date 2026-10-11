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
import os
import ipaddress
import urllib.request
from urllib.parse import urlsplit, urlencode
import sys
from datetime import datetime

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


def local_url(base):
    target = urlsplit(base)
    if (
        target.scheme != "http"
        or target.username
        or target.password
        or target.path not in ("", "/")
        or target.query
        or target.fragment
    ):
        raise ValueError("Use a plain loopback HTTP base URL")
    if (
        target.hostname != "localhost"
        and not ipaddress.ip_address(target.hostname or "").is_loopback
    ):
        raise ValueError("Unauthenticated replay supports loopback Witness only")
    return base.rstrip("/")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise RuntimeError("Redirects are not allowed during local replay")


class Transport:
    @staticmethod
    def send(url, params=None, json=None, timeout=10):
        if params:
            url += "?" + urlencode(params)
        data = (
            None
            if json is None
            else globals()["json"].dumps(json, allow_nan=False).encode()
        )
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"} if data else {}
        )
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), NoRedirect()
        )
        with opener.open(req, timeout=timeout) as response:
            body = response.read(2_000_001)
            if len(body) > 2_000_000:
                raise RuntimeError("Response exceeds bounded replay limit")
            result = (
                globals()["json"].loads(body)
                if body.startswith((b"{", b"["))
                else body.decode()
            )
            return Response(result, response.status)

    get = send

    @staticmethod
    def post(url, json, timeout=30):
        return Transport.send(url, json=json, timeout=timeout)


class Response:
    def __init__(self, data, status):
        self.data, self.status_code, self.ok, self.text = (
            data,
            status,
            200 <= status < 300,
            "",
        )

    def json(self):
        return self.data


requests = Transport()


def list_records(witness_api, kind, label="EXP-001"):
    nodes = []
    total = None
    for offset in range(0, 1000, 100):
        response = requests.get(
            witness_api + "/api/nodes",
            params={"type": kind, "label": label, "limit": 100, "offset": offset},
            timeout=10,
        )
        if not response.ok:
            raise RuntimeError("Record lookup failed; refusing to write")
        data = response.json()
        if not isinstance(data.get("nodes"), list) or not isinstance(
            data.get("total_count"), int
        ):
            raise RuntimeError("Malformed record lookup")
        if total is None:
            total = data["total_count"]
        if total != data["total_count"] or total > 1000:
            raise RuntimeError(
                "Changing or oversized record set; use a fresh isolated database"
            )
        nodes.extend(data["nodes"])
        if len(nodes) == total:
            return nodes
        if not data["nodes"]:
            raise RuntimeError("Incomplete pagination; refusing to write")
    raise RuntimeError("Record limit exceeded")


def existing_match(base, kind, required_labels, expected):
    matches = [
        n
        for n in list_records(base, kind)
        if set(required_labels) <= set(n.get("labels", []))
    ]
    if len(matches) > 1:
        raise RuntimeError("Duplicate replay identity; use a fresh isolated database")
    if not matches:
        return None
    node = matches[0]
    if not matches_payload(node, kind, expected):
        raise RuntimeError(
            "Existing record labels match but payload/provenance differs; no overwrite attempted. Use a fresh database."
        )
    return node["id"]


def matches_payload(node, kind, expected):
    try:
        if (
            node["epistemic_type"].lower() != kind
            or node["author"]["id"] != expected["author_id"]
            or node["author"].get("name") != expected.get("author_name")
            or node.get("domain") != expected.get("domain")
            or node.get("source_uri") != expected.get("source_uri")
            or set(node["labels"]) != set(expected["labels"])
        ):
            return False
        p = node["payload"]
        if kind == "observed":
            m = p["measurement"]
            return (
                not node["parents"]
                and m["quantity"] == expected["quantity"]
                and m["value"]["numeric"] == float(expected["value"])
                and m["value"]["unit"] == expected["unit"]
                and m["instrument"]["id"] == expected["instrument_id"]
                and m["instrument"]["name"] == expected["instrument_name"]
                and datetime.fromisoformat(m["measured_at"].replace("Z", "+00:00"))
                == datetime.fromisoformat(
                    expected["measured_at"].replace("Z", "+00:00")
                )
            )
        if kind == "inferred":
            d = p["derivation"]
            actual_f = [
                {
                    k: f.get(k)
                    for k in ["description", "measurement_type", "timeframe", "status"]
                }
                for f in d["falsifiers"]
            ]
            return (
                node["parents"] == expected["premises"] == d["premises"]
                and d["methodology"] == expected["methodology"]
                and d["claim"]["statement"] == expected["claim"]
                and d["claim"]["claim_type"] == expected["claim_type"]
                and d["claim"]["scope"] == expected["claim_scope"]
                and actual_f == expected["falsifiers"]
                and d["inference_uncertainty"] == expected["inference_uncertainty"]
            )
        return (
            not node["parents"]
            and p["node"]["payload"]["content"] == expected["content"]
            and p["model"]["id"] == expected["generator"]
            and p["model"]["version"] == expected["model_version"]
            and p["prompt"] == expected["prompt"]
            and p["human_reviewed"] is expected["human_reviewed"]
        )
    except (KeyError, TypeError, ValueError):
        return False


def ingest_observation(
    witness_api: str,
    compound_id: str,
    seed: int,
    affinity: float,
    timestamp: str,
    label: str,
) -> str:
    """Ingest a single observed docking measurement."""
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

    existing = existing_match(
        witness_api, "observed", ["EXP-001", compound_id, f"seed-{seed}"], payload
    )
    if existing:
        print(f"  [REUSE] {existing}")
        return existing

    resp = requests.post(
        f"{witness_api}/api/ingest/observation", json=payload, timeout=30
    )
    if not resp.ok:
        raise RuntimeError(
            f"Failed to ingest observation: {resp.status_code} {resp.text}"
        )

    result = resp.json()
    print(
        f"  [CREATE] {compound_id} seed={seed} -> {result['id']} (CID: {result['cid'][:16]}...)"
    )
    return result["id"]


def ingest_consensus_inference(witness_api: str, observed_ids: list[str]) -> str:
    """Ingest the consensus inference."""
    payload = {
        "premises": observed_ids,
        "methodology": "Pearson correlation between two specified local AutoDock Vina replicates (seeds 101 and 202) on six known CDK2 actives. Consensus threshold r >= 0.80. Outlier detection via IQR on per-compound replicate differences.",
        "claim": "The two specified Vina runs (seeds 101 and 202) have Pearson r = 0.885 across six docking scores, exceeding the predeclared r >= 0.80 agreement threshold. This establishes agreement between those runs only; it does not establish biological efficacy or predictive validity.",
        "claim_type": "correlative",
        "claim_scope": "specific",
        "falsifiers": [
            {
                "description": "A third independent Vina replicate with a different seed produces docking scores that correlate with the first two replicates at r < 0.80",
                "measurement_type": "docking_affinity",
                "timeframe": "Any future replication",
                "status": "pending",
            },
            {
                "description": "Experimental binding assays (ITC, SPR) for the six compounds contradict the predicted rank order from the consensus docking scores",
                "measurement_type": "experimental_binding_affinity",
                "timeframe": "When experimental data available",
                "status": "pending",
            },
            {
                "description": "Using a different binding-site center (e.g., the earlier incorrect fabricated center) yields r < 0.80 or reversed rank order",
                "measurement_type": "docking_affinity",
                "timeframe": "Already observed in failed attempt",
                "status": "completed-falsified",
            },
        ],
        "inference_uncertainty": 0.115,
        "author_id": ANALYST_AUTHOR["author_id"],
        "author_name": ANALYST_AUTHOR["author_name"],
        "author_type": ANALYST_AUTHOR["author_type"],
        "labels": [
            "EXP-001",
            "consensus",
            "validation",
            "pearson-r=0.885",
            "threshold=0.80",
            "passed",
            "outliers=1",
        ],
        "domain": "computational-chemistry",
        "source_uri": "humanity-grid://EXP-001/validation/output/results/consensus.json",
    }

    existing = existing_match(
        witness_api, "inferred", ["EXP-001", "consensus"], payload
    )
    if existing:
        print(f"  [REUSE] {existing}")
        return existing

    resp = requests.post(
        f"{witness_api}/api/ingest/inference", json=payload, timeout=30
    )
    if not resp.ok:
        raise RuntimeError(
            f"Failed to ingest consensus inference: {resp.status_code} {resp.text}"
        )

    result = resp.json()
    print(
        f"  [CREATE] consensus inference -> {result['id']} (CID: {result['cid'][:16]}...)"
    )
    return result["id"]


def ingest_failed_attempt_inference(witness_api: str) -> str:
    """Ingest the failed attempt inference (provenance)."""
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
                "status": "completed-falsified",
            }
        ],
        "inference_uncertainty": None,
        "author_id": ANALYST_AUTHOR["author_id"],
        "author_name": ANALYST_AUTHOR["author_name"],
        "author_type": ANALYST_AUTHOR["author_type"],
        "labels": [
            "EXP-001",
            "failed-attempt",
            "provenance",
            "correction",
            "binding-site-error",
        ],
        "domain": "computational-chemistry",
        "source_uri": "humanity-grid://EXP-001/validation/output/results/consensus.json",
    }

    existing = existing_match(
        witness_api, "inferred", ["EXP-001", "failed-attempt"], payload
    )
    if existing:
        print(f"  [REUSE] {existing}")
        return existing

    resp = requests.post(
        f"{witness_api}/api/ingest/inference", json=payload, timeout=30
    )
    if not resp.ok:
        raise RuntimeError(
            f"Failed to ingest failed attempt inference: {resp.status_code} {resp.text}"
        )

    result = resp.json()
    print(
        f"  [CREATE] failed attempt inference -> {result['id']} (CID: {result['cid'][:16]}...)"
    )
    return result["id"]


def ingest_generation(witness_api: str) -> str:
    """Ingest the Research Scout hypothesis."""
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

    existing = existing_match(
        witness_api, "generated", ["EXP-001", "hypothesis"], payload
    )
    if existing:
        print(f"  [REUSE] {existing}")
        return existing

    resp = requests.post(
        f"{witness_api}/api/ingest/generation", json=payload, timeout=30
    )
    if not resp.ok:
        raise RuntimeError(
            f"Failed to ingest generation: {resp.status_code} {resp.text}"
        )

    result = resp.json()
    print(
        f"  [CREATE] hypothesis generation -> {result['id']} (CID: {result['cid'][:16]}...)"
    )
    return result["id"]


def verify_ingestion(witness_api: str) -> bool:
    groups = {
        kind: list_records(witness_api, kind)
        for kind in ["observed", "inferred", "generated"]
    }
    if [len(groups[k]) for k in groups] != [12, 2, 1]:
        return False
    observed_ids = {n["id"] for n in groups["observed"]}
    consensus = [n for n in groups["inferred"] if "consensus" in n["labels"]]
    return (
        len(consensus) == 1
        and set(consensus[0]["parents"]) == observed_ids
        and len(consensus[0]["parents"]) == 12
        and groups["generated"][0]["payload"].get("human_reviewed") is False
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Idempotently deposit and verify the frozen EXP-001 Proof A record in Witness."
    )
    parser.add_argument(
        "--witness",
        default=os.environ.get("WITNESS_API", DEFAULT_WITNESS_API),
        help="Witness API base URL (default: %(default)s)",
    )
    args = parser.parse_args()
    witness_api = local_url(args.witness)
    print("=== EXP-001 Idempotent Witness Ingestion ===\n")

    # Check server
    try:
        resp = requests.get(f"{witness_api}/health", timeout=5)
        if not resp.ok:
            print(f"Witness API not healthy: {resp.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"Cannot reach Witness API at {witness_api}: {e}")
        print(
            "Start Witness first; see Witness INSTALL.md for the one-command local server."
        )
        return 1

    print(
        "Witness API reachable. Replay copies a historical example; no new model or docking run occurs.\n"
    )
    # Complete all bounded lookups before writing; individual writes remain non-transactional.
    for kind in ["observed", "inferred", "generated"]:
        list_records(witness_api, kind)

    # 1. Ingest 12 Observed records
    print("1. Ingesting 12 Observed records (6 compounds × 2 replicates)...")
    observed_ids = []
    for compound_id, r1, r2 in COMPOUNDS:
        for rep in REPLICATES:
            affinity = r1 if rep["seed"] == 101 else r2
            oid = ingest_observation(
                witness_api,
                compound_id,
                rep["seed"],
                affinity,
                rep["timestamp"],
                rep["label"],
            )
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
    print("Generated: 1 record")
    print("\nIdempotent: Re-run this script to verify no duplicates created")

    if success:
        print("\n✓ All records verified successfully!")
        return 0
    else:
        print("\n✗ Verification failed")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, ValueError, OSError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
