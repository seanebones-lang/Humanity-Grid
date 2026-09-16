# Experiment Engine

**Job definitions, dataset management, reproducibility, and provenance tracking for distributed scientific experiments.**

## Responsibilities

- Define computational experiments as structured job specifications
- Manage datasets (compound libraries, protein structures, parameter sets)
- Ensure reproducibility through container hashes, environment pins, and deterministic execution
- Track full provenance from hypothesis → job → results → analysis

## Job Specification Format

```yaml
# job-spec.yaml
job_id: "EXP-H9182-VS-001"
hypothesis_id: "H-9182"
created_at: "2026-09-16T14:30:00Z"
experiment_type: "virtual_screening"
name: "KRAS G12C covalent inhibitor screen"
description: "Screen ChEMBL approved drugs against KRAS G12C pocket"

# Compute requirements
compute:
  engine: "autodock-gpu"
  gpu_required: true
  gpu_memory_gb: 8
  cpus: 4
  memory_gb: 16
  estimated_runtime_hours: 0.5  # per work unit
  max_runtime_hours: 2

# Work unit definition
work_units:
  total: 2000
  compounds_per_unit: 1000
  compound_library: "chembl_approved_v32"
  split_strategy: "sequential"  # sequential, random, stratified

# Input data (content-addressed)
inputs:
  protein_structure:
    source: "pdb:6O0M"
    sha256: "a1b2c3d4..."
    binding_site:
      center: [12.3, -4.5, 8.7]
      radius: 15.0
  compound_library:
    source: "chembl:v32:approved"
    sha256: "e5f6g7h8..."
    format: "sdf"
  docking_parameters:
    exhaustiveness: 16
    num_modes: 10
    energy_range: 3.0

# Container specification
container:
  image: "ghcr.io/humanity-grid/autodock-gpu:1.2.0"
  sha256: "sha256:abcdef123456..."
  entrypoint: "/app/run_docking.sh"
  environment:
    - OMP_NUM_THREADS=4
    - CUDA_VISIBLE_DEVICES=0

# Output specification
outputs:
  - name: "docking_results"
    format: "parquet"
    schema:
      - compound_id: string
      - affinity_kcal_mol: float
      - rmsd_lb: float
      - rmsd_ub: float
      - pose_coords: binary
    validation:
      - required_fields: ["compound_id", "affinity_kcal_mol"]
      - affinity_range: [-20, 10]

# Validation & Quality Control
validation:
  redundancy: 2  # each work unit computed twice
  consensus_threshold: 0.8  # Pearson correlation between replicates
  outlier_detection: "iqr"
  failed_unit_retry: 3

# Provenance
provenance:
  hypothesis_id: "H-9182"
  researcher_approval: "dr_smith@university.edu"
  approval_timestamp: "2026-09-15T10:00:00Z"
  git_commit: "a1b2c3d4"
  spec_hash: "sha256:fedcba9876..."
```

## Dataset Management

| Dataset | Source | Format | Size | SHA256 |
|---------|--------|--------|------|--------|
| ChEMBL Approved Drugs | EBI ChEMBL v32 | SDF | ~2M compounds | `abc123...` |
| PDBbind Refined | PDBbind v2020 | SDF + CSV | ~5k complexes | `def456...` |
| BindingDB Ki/Kd | BindingDB 2024 | TSV | ~2M affinities | `ghi789...` |
| AlphaFold DB Structures | EBI AlphaFold | PDB | ~200M predictions | `jkl012...` |
| ZINC20 Library | ZINC20 | SDF/CSV | ~1.4B compounds | `mno345...` |

Datasets are:
- Content-addressed (SHA256)
- Versioned
- Mirrored to IPFS / cloud storage
- Referenced by immutable identifier

## Provenance Tracking

Every result carries full lineage:

```
Result
├── job_spec_hash: "sha256:..."
├── work_unit_id: "EXP-H9182-VS-001-WU-0421"
├── container_hash: "sha256:..."
├── input_hashes:
│   ├── protein: "sha256:a1b2..."
│   ├── compounds: "sha256:e5f6..."
│   └── parameters: "sha256:..."
├── compute_node:
│   ├── volunteer_id: "anon-hash-123"
│   ├── gpu: "NVIDIA RTX 3080"
│   ├── driver: "535.154.05"
│   └── boinc_client: "7.24.1"
├── execution:
│   ├── started: "2026-09-16T15:00:00Z"
│   ├── finished: "2026-09-16T15:23:45Z"
│   ├── cpu_time_sec: 1245
│   └── gpu_time_sec: 987
├── validation:
│   ├── replicate_id: "EXP-H9182-VS-001-WU-0421-rep2"
│   ├── consensus_score: 0.94
│   └── status: "validated"
└── output_hash: "sha256:result-file-hash"
```

## Architecture

```
experiment-engine/
├── pyproject.toml
├── src/
│   └── experiment_engine/
│       ├── __init__.py
│       ├── jobs/
│       │   ├── spec.py          # JobSpec model, validation
│       │   ├── registry.py      # Job registry, persistence
│       │   ├── splitter.py      # Work unit splitting
│       │   └── templates.py     # Common experiment templates
│       ├── datasets/
│       │   ├── manager.py       # Dataset download, verify, cache
│       │   ├── registry.py      # Dataset catalog
│       │   └── providers.py     # ChEMBL, PDB, BindingDB, ZINC, etc.
│       ├── provenance/
│       │   ├── tracker.py       # Provenance recording
│       │   ├── models.py        # Provenance data models
│       │   └── store.py         # Provenance storage (SQLite/Parquet)
│       ├── validation/
│       │   ├── consensus.py     # Replicate comparison
│       │   ├── quality.py       # Output quality checks
│       │   └── retry.py         # Failed unit handling
│       └── config.py
├── tests/
└── scripts/
    ├── create_job.py
    ├── validate_job.py
    └── split_work_units.py
```

## Quick Start

```bash
cd src/experiment-engine
uv pip install -e .

# Create a job from template
python -m experiment_engine.jobs.create \
  --template virtual_screening \
  --target pdb:6O0M \
  --library chembl_approved \
  --output job-spec.yaml

# Validate job spec
python -m experiment_engine.jobs.validate job-spec.yaml

# Split into work units
python -m experiment_engine.jobs.split job-spec.yaml --output work_units/

# Register dataset
python -m experiment_engine.datasets.register \
  --name chembl_approved \
  --version v32 \
  --source https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/chembl_32_sdf.zip
```