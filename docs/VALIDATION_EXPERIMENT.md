# Validation Experiment: CDK2 Virtual Screening

**Goal**: Prove the pipeline works by rediscovering known CDK2 inhibitors from ChEMBL.

## Target Selection

- **Protein**: Cyclin-dependent kinase 2 (CDK2)
- **PDB**: `1KE7` (CDK2 with inhibitor, 2.0Å resolution)
- **Binding site**: ATP pocket, center ≈ `[25.1, 12.3, 18.7]`, radius `12Å`
- **Known actives**: 47 ChEMBL compounds with IC50 < 100 nM (from ChEMBL v32)
- **Decoys**: 10,000 random ChEMBL compounds (inactive or unknown)

## Experiment Design

```
Job: EXP-VAL-CDK2-VS-001
Type: virtual_screening
Library: ChEMBL v32 (subset: 10,047 compounds)
Work units: 11 (≈1000 compounds each, last has 47)
Redundancy: 2× (22 total work units)
Engine: AutoDock-GPU
Container: ghcr.io/humanity-grid/autodock-gpu:1.2.0
```

## Success Criteria

| Metric | Threshold |
|--------|-----------|
| Enrichment Factor (EF1%) | ≥ 10 |
| AUC-ROC | ≥ 0.80 |
| Top-10 recall | ≥ 5/10 known actives |
| Consensus correlation | ≥ 0.8 between replicates |
| Reproducibility | Same container + same input = identical output |

## Quick Start (Local Validation)

### 1. Prepare Data

```bash
# Download ChEMBL 32 SDF (approved subset)
wget https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/chembl_32_sdf.zip
unzip chembl_32_sdf.zip

# Extract known CDK2 actives (IC50 < 100 nM) - use ChEMBL API or local query
# For now, use a pre-made file:
wget https://data.humanity-grid.org/validation/cdk2_actives.sdf
wget https://data.humanity-grid.org/validation/cdk2_decoys_10k.sdf

# Combine
cat cdk2_actives.sdf cdk2_decoys_10k.sdf > validation_library.sdf

# Prepare protein (PDB 1KE7)
wget https://files.rcsb.org/download/1KE7.pdb
# Convert to PDBQT using MGLTools or our prepare_receptor.py
python -m scientific_pipeline.docker.autodock-gpu.prepare_receptor \
  --input 1KE7.pdb \
  --output 1KE7.pdbqt \
  --center 25.1 12.3 18.7 \
  --radius 12.0
```

### 2. Build Container

```bash
cd src/scientific-pipeline/docker/autodock-gpu
docker build -t humanity-grid/autodock-gpu:val-1 .
# Note: record SHA256 digest for JobSpec
docker images --digests humanity-grid/autodock-gpu:val-1
```

### 3. Create Job Spec

```bash
# Use the experiment-engine CLI
cd src/experiment-engine
python -m experiment_engine.jobs.create \
  --template virtual_screening \
  --job-id EXP-VAL-CDK2-VS-001 \
  --hypothesis-id H-VAL-CDK2 \
  --name "CDK2 Validation Screen" \
  --overrides '{
    "inputs": {
      "protein_structure": {"source": "pdb:1KE7", "sha256": "PROTEIN_SHA256", "binding_site": {"center": [25.1, 12.3, 18.7], "radius": 12.0}},
      "compound_library": {"source": "validation:cdk2_v1", "sha256": "LIBRARY_SHA256", "format": "sdf"}
    },
    "container": {"image": "humanity-grid/autodock-gpu:val-1", "sha256": "CONTAINER_SHA256"},
    "work_units": {"total": 11, "compounds_per_unit": 1000, "compound_library": "validation:cdk2_v1"},
    "provenance": {"hypothesis_id": "H-VAL-CDK2", "researcher_approval": "validator@humanity-grid.org", "approval_timestamp": "2026-09-16T00:00:00Z", "git_commit": "HEAD_SHA"}
  }' \
  --output job-spec.yaml
```

### 4. Run Work Units Locally (Simulate 2 Volunteers)

```bash
# Split library into work units
python -m experiment_engine.jobs.split job-spec.yaml --output work_units/

# Run each work unit twice (simulate redundancy)
for wu in work_units/*.json; do
  for rep in 1 2; do
    docker run --rm --gpus all \
      -v $(pwd)/work_units/$(basename $wu):/input/work_unit.json:ro \
      -v $(pwd)/data:/input/data:ro \
      -v $(pwd)/output/rep$rep/$(basename $wu .json):/output \
      humanity-grid/autodock-gpu:val-1
  done
done
```

### 5. Validate Consensus

```bash
cd src/compute-broker
python -m compute_broker.validation.consensus \
  --job-id EXP-VAL-CDK2-VS-001 \
  --results-dir output/ \
  --redundancy 2 \
  --threshold 0.8 \
  --output validation_report.json
```

### 6. Analyze Results

```bash
cd src/open-results
python -m open_results.notebooks.generator \
  --job-id EXP-VAL-CDK2-VS-001 \
  --template virtual_screening \
  --output notebooks/validation/

# Execute notebook headless
python -m open_results.notebooks.runner \
  notebooks/validation/EXP-VAL-CDK2-VS-001_analysis.qmd
```

### 7. Publish Report

The notebook generates:
- `validation_report.html` — enrichment plots, ROC curves, top hits table
- `validation_report.json` — machine-readable metrics
- `top_candidates.parquet` — ranked compounds with consensus scores

Compare against known actives:

```python
# In the notebook
known_actives = set(load_actives("cdk2_actives.sdf"))
top_100 = results.nlargest(100, "consensus_score")
recall_at_10 = len(known_actives & set(top_100.head(10)["compound_id"])) / 10
ef_1pct = (len(known_actives & set(top_100.head(100)["compound_id"])) / 100) / (len(known_actives) / 10047)
auc_roc = compute_auc(results, known_actives)
print(f"EF1%: {ef_1pct:.1f}, AUC-ROC: {auc_roc:.3f}, Top-10 recall: {recall_at_10:.1f}")
```

## Expected Output

```
VALIDATION REPORT: EXP-VAL-CDK2-VS-001
=========================================
Target: CDK2 (PDB: 1KE7)
Library: 10,047 compounds (47 known actives + 10,000 decoys)
Work units: 11 × 2 replicates = 22 total
Container: humanity-grid/autodock-gpu@sha256:abc123...
Compute: Local GPU (RTX 3080, 10GB) × 2 runs

CONSENSUS
---------
Work units passing consensus (r ≥ 0.8): 11/11 (100%)
Work units failed/retried: 0
Mean replicate correlation: 0.94

ENRICHMENT
----------
EF1% (top 100): 14.2×
AUC-ROC: 0.87
Top-10 recall: 7/10 (70%)
Top-50 recall: 23/47 (49%)

TOP HITS
--------
1. CHEMBL123456  (known: staurosporine analog)     affinity: -11.2  consensus: 0.97
2. CHEMBL234567  (known: roscovitine analog)        affinity: -10.8  consensus: 0.95
3. CHEMBL345678  (known: purvalanol analog)         affinity: -10.5  consensus: 0.93
4. CHEMBL456789  (novel scaffold)                   affinity: -10.3  consensus: 0.91
5. CHEMBL567890  (known: CDK2 inhibitor)            affinity: -10.1  consensus: 0.94
...

REPRODUCIBILITY
---------------
Container digest: sha256:abc123...
JobSpec hash: sha256:def456...
Input hashes: protein=..., library=..., params=...
Result hashes: work_unit_001_rep1=..., work_unit_001_rep2=... (match)
Git commit: a1b2c3d4

CONCLUSION
----------
✅ Pipeline reproduces known CDK2 inhibitors with statistical significance
✅ Consensus validation works (all units passed)
✅ Results are deterministic and content-addressed
✅ Ready for BOINC Central deployment
```

## Files Generated

```
validation/
├── job-spec.yaml              # Experiment definition
├── work_units/                # 11 work unit configs
├── output/
│   ├── rep1/                  # Replicate 1 results
│   └── rep2/                  # Replicate 2 results
├── validation_report.json     # Consensus + metrics
├── notebooks/
│   └── EXP-VAL-CDK2-VS-001_analysis.qmd
└── published/
    ├── validation_report.html
    ├── top_candidates.parquet
    └── validation_report.json
```

## Next Steps After Validation

1. Deploy to BOINC Central test project
2. Recruit 5-10 volunteer GPUs for real distributed run
3. Compare local vs distributed results (should match)
4. Publish project page at `https://humanity-grid.org/projects/H-VAL-CDK2`
5. Move to real scientific target (KRAS G12C, etc.)