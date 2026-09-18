# Archived design draft: large-scale CDK2 virtual screening

> **Do not use this document as an installation guide, evidence package, or
> statement of current implementation.** It describes a proposed future Proof B
> style screen involving AutoDock-GPU, 10,047 compounds, attested volunteer
> nodes, and a `r >= 0.95` rule. Those controls are not implemented by the
> current Witness protocol or the frozen EXP-001 demonstration.
>
> For the actual supported review path, including the six-compound AutoDock Vina
> CPU demonstration, its `r >= 0.80` agreement rule, local record replay, and
> known limitations, read [Proof A: scientific review and local replay](PROOF_A_REVIEW.md).

**Goal**: Prove the pipeline infrastructure works by demonstrating reproducible, content-addressed, consensus-validated compute on a known target.

**Non-goal**: Prove docking enrichment works. That is a scientific question separate from infrastructure validation.

---

## Two-Stage Validation

### Proof A: Infrastructure (this experiment)
- **Question**: Does the same work unit, run twice on independent nodes with pinned parameters, produce bitwise-identical or numerically-close results that survive consensus validation?
- **Success**: ≥ 95% of work units pass consensus (Pearson r ≥ 0.95 on pinned seed/cpu=1), Record completeness verified, re-execution possible from Record.
- **Failure mode**: If this fails, the substrate (volunteer compute + containers + consensus) is not viable for this workload.

### Proof B: Scientific Enrichment (separate, later)
- **Question**: Does virtual screening on this target enrich known actives?
- **Expectation**: Docking enrichment is mediocre (AUC ~0.6-0.8 typical). State this upfront.
- **Dataset**: Bias-controlled (LIT-PCBA or curated), not DUD-E.
- **Timing**: After Proof A passes.

---

## Target & Data (Proof A)

| Item | Value |
|------|-------|
| **Protein** | CDK2 (Cyclin-dependent kinase 2) |
| **PDB** | `1KE7` (2.0Å, CDK2 + inhibitor) |
| **Binding site** | ATP pocket, center `[-9.11, 48.31, 11.80]` (LS3 co-ligand), radius `12Å` |
| **Library** | 10,047 compounds: 47 known CDK2 actives (ChEMBL IC50 < 100 nM) + 10,000 decoys |
| **Work units** | 11 (≈1000 compounds each, last = 47) |
| **Redundancy** | 2× (22 total work unit executions) |

---

## Pinned Parameters (Reproducibility Contract)

Every work unit execution MUST use:

```json
{
  "engine": "autodock-gpu",
  "container": "humanity-grid/autodock-gpu@sha256:<DIGEST>",
  "exhaustiveness": 16,
  "num_modes": 10,
  "energy_range": 3.0,
  "cpu": 1,
  "seed": 42,
  "box_center": [-9.11, 48.31, 11.80],
  "box_radius": 12.0
}
```

**Rationale**: AutoDock-GPU is stochastic and multi-threaded. Different CPU counts or seeds produce different scores. Pinning eliminates legitimate variance so consensus failures reflect actual faults.

---

## Witness Integration (The Novelty)

### Four Epistemic States

| State | Producer | Meaning |
|-------|----------|---------|
| **Observed** | Coordinator (after quorum) | "This result passed consensus and is accepted as the measurement." |
| **Attested** | Volunteer node | "This node produced this output, signed by its key." |
| **Inferred** | Consensus algorithm | "Replicates A and B agree within threshold; premise = both raw outputs." |
| **Generated** | LLM / summary | "Human-readable story; not evidence." |

### Flow

```
1. JobSpec + input hashes → ingest as Observed (CID of spec)
   └─ Witness record: type=Observed, domain=humanity-grid, cid=...

2. Each work unit execution (×2) → Attested
   ├─ Node A: raw output + signature → Witness Attested
   └─ Node B: raw output + signature → Witness Attested

3. Consensus check (Pearson r ≥ 0.95 on pinned params)
   ├─ Pass → Coordinator writes Observed (consensus result)
   │         Witness Inferred: premises = [Attested_A, Attested_B], method=consensus_v1, falsifier="r < 0.95"
   └─ Fail → Re-queue (max 3), then flag

4. Research Scout hypothesis H-VAL-CDK2 → Generated (model + papers)
   └─ Human approval → Inferred (author=reviewer, premises=paper CIDs)

5. Open Results page = Witness query: domain=humanity-grid project=H-VAL-CDK2
```

### Falsifier (Explicit)

> **If replicate agreement on pinned containers (seed=42, cpu=1, exhaustiveness=16) falls below Pearson r = 0.95 for > 5% of work units, volunteer compute is not a viable substrate for deterministic docking workloads.**

---

## Consensus Thresholds

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Pearson correlation (affinity scores) | r ≥ 0.95 | Pinned params should give near-identical results |
| Score difference (mean absolute) | < 0.1 kcal/mol | Numerical stability |
| Bitwise output identity | Not required | Floating point non-determinism across arches |
| Work unit pass rate | ≥ 95% | Allow rare hardware faults |

---

## Licensing

| Artifact | License | Redistribution |
|----------|---------|----------------|
| ChEMBL data | CC BY-SA 4.0 | Share-alike → derived datasets must be CC BY-SA |
| PDB structures | Public domain | Unrestricted |
| AutoDock-GPU | LGPL-2.1+ | Binary redistribution OK with source offer |
| AutoDock-Vina | Apache-2.0 | Permissive |
| OpenMM | MIT/LGPL | Permissive |
| Our code | MIT | Permissive |
| Witness records | MPL-2.0 | File-level copyleft |

**Published datasets** (enrichment results, top hits) inherit CC BY-SA from ChEMBL.

---

## Carbon Cost Estimate (Ready for Reviewer)

| Workload | GPU-hours | kWh (est.) | kg CO₂ (US grid avg 0.385 kg/kWh) |
|----------|-----------|------------|-----------------------------------|
| 1 work unit (1000 cmpds) | 0.5 | 0.15 | 0.058 |
| Full screen (22 runs) | 11 | 3.3 | 1.27 |
| Spot instance equivalent (p3.2xlarge) | 11 | 3.3 | 1.27 |

**Note**: Volunteer compute uses existing hardware (no marginal embodied carbon). Marginal cost = electricity only. Compare to spot: similar kWh, but volunteer avoids data center overhead (cooling, networking, admin).

---

## Quick Start (Local Validation)

### 1. Prepare Data

```bash
# CDK2 actives (ChEMBL IC50 < 100 nM, curated)
wget https://data.humanity-grid.org/validation/cdk2_actives_47.sdf

# Decoys (10K random ChEMBL, property-matched)
wget https://data.humanity-grid.org/validation/cdk2_decoys_10k.sdf

# Combine
cat cdk2_actives_47.sdf cdk2_decoys_10k.sdf > validation_library.sdf

# Protein
wget https://files.rcsb.org/download/1KE7.pdb
```

### 2. Build Container

```bash
cd src/scientific-pipeline/docker/autodock-gpu
docker build -t humanity-grid/autodock-gpu:val-1 .
CONTAINER_DIGEST=$(docker images --digests humanity-grid/autodock-gpu:val-1 --format "{{.Digest}}")
echo "Container: $CONTAINER_DIGEST"
```

### 3. Create JobSpec

```bash
cd src/experiment-engine
python scripts/create_job.py \
  --template virtual_screening \
  --job-id EXP-VAL-CDK2-VS-001 \
  --hypothesis-id H-VAL-CDK2 \
  --name "CDK2 Infrastructure Validation" \
  --overrides "{
    \"inputs\": {
      \"protein_structure\": {\"source\": \"pdb:1KE7\", \"sha256\": \"PROTEIN_SHA256\", \"binding_site\": {\"center\": [-9.11, 48.31, 11.80], \"radius\": 12.0}},
      \"compound_library\": {\"source\": \"validation:cdk2_v1\", \"sha256\": \"LIBRARY_SHA256\", \"format\": \"sdf\"}
    },
    \"container\": {\"image\": \"humanity-grid/autodock-gpu:val-1\", \"sha256\": \"$CONTAINER_DIGEST\"},
    \"work_units\": {\"total\": 11, \"compounds_per_unit\": 1000, \"compound_library\": \"validation:cdk2_v1\"},
    \"provenance\": {\"hypothesis_id\": \"H-VAL-CDK2\", \"researcher_approval\": \"validator@humanity-grid.org\", \"approval_timestamp\": \"2026-09-16T00:00:00Z\", \"git_commit\": \"HEAD_SHA\"}
  }" \
  --output job-spec.yaml
```

### 4. Split Work Units

```bash
python scripts/split_work_units.py job-spec.yaml --output work_units/
```

### 5. Run Locally (Simulate 2 Volunteers)

```bash
# Prepare receptor once
docker run --rm \
  -v $(pwd)/data:/input/data:ro \
  -v $(pwd)/output/prep:/output \
  humanity-grid/autodock-gpu:val-1 \
  python /app/prepare_receptor.py \
  --input /input/data/1KE7.pdb \
  --output /output/1KE7.pdbqt \
  --center 25.1 12.3 18.7 \
  --radius 12.0

# Prepare ligands once
docker run --rm \
  -v $(pwd)/data:/input/data:ro \
  -v $(pwd)/output/prep:/output \
  humanity-grid/autodock-gpu:val-1 \
  python /app/prepare_ligands.py \
  --input /input/data/validation_library.sdf \
  --output-dir /output/ligands \
  --max-ligands 10047

# Run each work unit twice (rep1, rep2)
for rep in 1 2; do
  mkdir -p output/rep$rep
  for wu in work_units/*.json; do
    docker run --rm --gpus all \
      -v $(pwd)/$wu:/input/work_unit.json:ro \
      -v $(pwd)/output/prep:/input/data:ro \
      -v $(pwd)/output/rep$rep/$(basename $wu .json):/output \
      humanity-grid/autodock-gpu:val-1
  done
done
```

### 6. Validate Consensus

```bash
cd src/compute-broker
python scripts/validate_consensus.py \
  --job-id EXP-VAL-CDK2-VS-001 \
  --results-dir ../experiment-engine/output/ \
  --redundancy 2 \
  --threshold 0.95 \
  --output validation_report.json
```

### 7. Generate Witness Records

```bash
# Each Attested (raw node output)
witness-ingest observe \
  --domain humanity-grid \
  --type Attested \
  --payload output/rep1/wu_0000/results.parquet \
  --metadata '{"work_unit": "wu_0000", "replicate": 1, "node_key": "volunteer_A_pubkey"}'

witness-ingest observe \
  --domain humanity-grid \
  --type Attested \
  --payload output/rep2/wu_0000/results.parquet \
  --metadata '{"work_unit": "wu_0000", "replicate": 2, "node_key": "volunteer_B_pubkey"}'

# Inferred (consensus)
witness-ingest infer \
  --domain humanity-grid \
  --premises <CID_attested_A> <CID_attested_B> \
  --method consensus_v1 \
  --falsifier "pearson_r < 0.95" \
  --output <CID_observed>
```

### 8. Publish Report

The validation report includes:

```json
{
  "job_id": "EXP-VAL-CDK2-VS-001",
  "container_digest": "sha256:...",
  "pinned_params": {...},
  "work_units": 11,
  "redundancy": 2,
  "consensus_passed": 11,
  "consensus_failed": 0,
  "mean_pearson_r": 0.998,
  "mean_abs_diff_kcal": 0.003,
  "witness_records": {
    "attested": 22,
    "inferred": 11,
    "observed": 11
  },
  "falsifier_status": "NOT TRIGGERED",
  "conclusion": "Infrastructure validated. Substrate viable for deterministic docking."
}
```

---

## Files Generated

```
validation/
├── job-spec.yaml              # Experiment definition (Observed)
├── work_units/                # 11 work unit configs
├── output/
│   ├── prep/                  # Receptor + ligands (shared)
│   ├── rep1/                  # Replicate 1 (11 Attested)
│   └── rep2/                  # Replicate 2 (11 Attested)
├── validation_report.json     # Consensus metrics
├── witness_records/           # 44 Witness records (Attested + Inferred + Observed)
└── published/
    ├── validation_report.html
    ├── consensus_results.parquet
    └── validation_report.json
```

---

## Next Steps After Proof A Passes

1. Deploy to BOINC Central test project
2. Recruit 5-10 volunteer GPUs for real distributed run
3. Compare local vs distributed consensus (should match)
4. Publish project page at `https://humanity-grid.org/projects/H-VAL-CDK2`
5. **Then** design Proof B (scientific enrichment) with bias-controlled dataset
