# Scientific Pipeline

**Containerized scientific computing modules: AutoDock for virtual screening, OpenMM for molecular dynamics.**

## Responsibilities

- Provide production-ready Docker containers for scientific workloads
- AutoDock-GPU for high-throughput virtual screening
- OpenMM for molecular dynamics simulations
- Standardized interfaces (inputs/outputs) for Compute Broker
- Versioned, reproducible, content-addressed containers

## Container Specifications

### AutoDock-GPU Container

**Purpose:** High-throughput molecular docking for virtual screening.

**Base:** `nvidia/cuda:12.4-devel-ubuntu22.04`

**Contents:**
- AutoDock-GPU (compiled for CUDA 12.4)
- AutoDock-Vina (CPU fallback)
- MGLTools (for preparation scripts)
- Python 3.12 with NumPy, Pandas, RDKit
- Custom entrypoint for BOINC work units

**Input:**
- Protein structure (PDBQT)
- Compound library subset (SDF/PDBQT)
- Docking parameters (config file)

**Output:**
- Docking results (CSV/Parquet): compound_id, affinity, poses

**Resource Requirements:**
- GPU: NVIDIA CUDA 12+, 8GB+ VRAM
- CPU: 4 cores
- RAM: 16 GB
- Runtime: ~30 min per 1000 compounds

### OpenMM Container

**Purpose:** Molecular dynamics simulations for candidate refinement.

**Base:** `nvidia/cuda:12.4-devel-ubuntu22.04`

**Contents:**
- OpenMM 8.0+ (with CUDA, OpenCL, CPU platforms)
- OpenMM-Tools, PDBFixer
- AmberTools (for force fields)
- GROMACS tools (for analysis)
- Python 3.12 with MDAnalysis, MDTraj
- Custom entrypoint for BOINC work units

**Input:**
- Prepared system (protein + ligand, solvated)
- Simulation parameters (temperature, pressure, steps)
- Force field specification

**Output:**
- Trajectory (DCD/XTC)
- Energies/log (CSV)
- Final structure (PDB)

**Resource Requirements:**
- GPU: NVIDIA CUDA 12+, 8GB+ VRAM (or CPU fallback)
- CPU: 4 cores
- RAM: 16 GB
- Runtime: ~2-24 hours per simulation

## Container Build Process

```bash
# Build AutoDock-GPU container
cd docker/autodock-gpu
docker build -t ghcr.io/humanity-grid/autodock-gpu:1.2.0 .
docker push ghcr.io/humanity-grid/autodock-gpu:1.2.0

# Build OpenMM container
cd docker/openmm
docker build -t ghcr.io/humanity-grid/openmm:8.0.0 .
docker push ghcr.io/humanity-grid/openmm:8.0.0
```

## Content Addressing

Each container image is identified by its SHA256 digest:

```
ghcr.io/humanity-grid/autodock-gpu@sha256:abcdef1234567890...
ghcr.io/humanity-grid/openmm@sha256:fedcba0987654321...
```

These digests are embedded in JobSpecs for full reproducibility.

## Standardized Work Unit Interface

All scientific containers follow a common interface:

### Entrypoint Script (`/app/run.sh`)

```bash
#!/bin/bash
set -euo pipefail

# Input: /input (read-only)
# Output: /output (write)
# Work unit config: /input/work_unit.json

# Parse work unit config
WORK_UNIT_ID=$(jq -r '.work_unit_id' /input/work_unit.json)
JOB_ID=$(jq -r '.job_id' /input/work_unit.json)

# Run computation
python /app/run.py \
  --input-dir /input \
  --output-dir /output \
  --work-unit-id "$WORK_UNIT_ID" \
  --job-id "$JOB_ID"

# Write metadata
cat > /output/metadata.json <<EOF
{
  "work_unit_id": "$WORK_UNIT_ID",
  "job_id": "$JOB_ID",
  "container_hash": "$CONTAINER_SHA256",
  "completed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "exit_code": $?
}
EOF
```

### Work Unit Config (`/input/work_unit.json`)

```json
{
  "work_unit_id": "EXP-H9182-VS-001-WU-0421",
  "job_id": "EXP-H9182-VS-001",
  "index": 421,
  "parameters": {
    "exhaustiveness": 16,
    "num_modes": 10
  },
  "input_files": {
    "protein": "protein.pdbqt",
    "compounds": "compounds_421.sdf",
    "config": "docking_config.txt"
  },
  "output_files": {
    "results": "results_421.parquet",
    "poses": "poses_421.pdbqt"
  }
}
```

## Architecture

```
scientific-pipeline/
├── docker/
│   ├── autodock-gpu/
│   │   ├── Dockerfile
│   │   ├── entrypoint.sh
│   │   ├── run.py
│   │   ├── prepare_receptor.py
│   │   └── prepare_ligands.py
│   ├── openmm/
│   │   ├── Dockerfile
│   │   ├── entrypoint.sh
│   │   ├── run.py
│   │   ├── setup_system.py
│   │   └── analyze.py
│   └── base/
│       └── Dockerfile.base
├── src/
│   └── scientific_pipeline/
│       ├── __init__.py
│       ├── autodock/
│       │   ├── runner.py
│       │   ├── prepare.py
│       │   └── parse_output.py
│       ├── openmm/
│       │   ├── runner.py
│       │   ├── setup.py
│       │   ├── simulate.py
│       │   └── analyze.py
│       └── common/
│           ├── interface.py
│           └── validation.py
├── tests/
└── scripts/
    ├── build_containers.py
    ├── test_autodock.py
    └── test_openmm.py
```

## Quick Start

```bash
# Build containers
cd docker/autodock-gpu
docker build -t ghcr.io/humanity-grid/autodock-gpu:1.2.0 .

cd ../openmm
docker build -t ghcr.io/humanity-grid/openmm:8.0.0 .

# Test AutoDock locally
docker run --rm --gpus all \
  -v $(pwd)/test_data:/input:ro \
  -v $(pwd)/test_output:/output \
  ghcr.io/humanity-grid/autodock-gpu:1.2.0

# Test OpenMM locally
docker run --rm --gpus all \
  -v $(pwd)/test_data:/input:ro \
  -v $(pwd)/test_output:/output \
  ghcr.io/humanity-grid/openmm:8.0.0
```