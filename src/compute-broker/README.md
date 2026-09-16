# Compute Broker

**BOINC adapter, CPU/GPU workload management, and result validation for Humanity Grid.**

## Responsibilities

- Interface with BOINC (via BOINC Central) for work distribution
- Manage heterogeneous CPU/GPU workloads (CUDA, HIP, OpenCL, Metal)
- Handle work unit assignment, tracking, and result collection
- Validate results through redundant computation and consensus
- Manage volunteer registration, credits, and statistics

## BOINC Integration

We leverage **BOINC Central** (boinc.berkeley.edu/central) which provides:
- Managed BOINC server infrastructure
- Docker workload support
- AutoDock job type support
- Web-based project management
- Volunteer-facing website and account management

### Architecture

```
Humanity Grid Compute Broker
│
├── BOINC Central (managed server)
│   ├── Project configuration
│   ├── Work generation (from our Experiment Engine)
│   ├── Result validation (redundancy + consensus)
│   ├── Credit system
│   └── Volunteer website
│
├── Local Broker Service (our code)
│   ├── Job → BOINC work unit translation
│   ├── Dataset staging to BOINC Central
│   ├── Container image management (Docker Hub / GHCR)
│   ├── Result retrieval and aggregation
│   └── Quality monitoring
│
└── Volunteer Clients
    ├── BOINC Manager (standard)
    └── Humanity Grid Volunteer App (Tauri - custom UI)
```

## Work Unit Translation

Our Experiment Engine job specs → BOINC work units:

```
JobSpec (Experiment Engine)
    ↓
ComputeBroker.translate_job()
    ↓
BOINC Work Units:
  - wu_001: compounds 0-999
  - wu_002: compounds 1000-1999
  ...
  - wu_N: compounds (N-1)*1000 to N*1000
```

Each work unit includes:
- Input files (protein structure, compound subset, parameters)
- Docker image reference
- Resource requirements (CPU, GPU, memory, time)
- Expected output files

## GPU Workload Support

| Platform | API | AutoDock-GPU | OpenMM | Notes |
|----------|-----|--------------|--------|-------|
| NVIDIA | CUDA | ✅ Native | ✅ Native | Primary target |
| AMD | HIP | ✅ Via hipify | ✅ Native | ROCm 5+ |
| Intel/AMD | OpenCL | ✅ | ✅ | Fallback |
| Apple | Metal | ❌ | ✅ Via OpenMM | M-series Macs |

## Result Validation Pipeline

```
Work Unit Completed (×redundancy)
    ↓
Results Retrieved
    ↓
Schema Validation (required fields, ranges)
    ↓
Consensus Check (Pearson correlation between replicates)
    ↓
Outlier Detection (IQR / Z-score)
    ↓
┌─ Pass → Mark Validated → Aggregate
└─ Fail → Re-queue (up to max_retries)
```

## Volunteer Credit System

- **Credit = measured FLOPs × time** (standard BOINC Cobblestones)
- **Validated results only** — failed/outlier units earn no credit
- **Bonus for GPU work** — multiplier based on GPU capability
- **Team/school/company leaderboards** — aggregated from individual credits

## Architecture

```
compute-broker/
├── pyproject.toml
├── src/
│   └── compute_broker/
│       ├── __init__.py
│       ├── boinc/
│       │   ├── client.py          # BOINC Central API client
│       │   ├── workgen.py         # Work unit generation from JobSpec
│       │   ├── result_handler.py  # Result retrieval and parsing
│       │   └── project_config.py  # Project configuration
│       ├── workloads/
│       │   ├── cpu.py             # CPU workload management
│       │   ├── gpu.py             # GPU workload management
│       │   ├── docker.py          # Docker container handling
│       │   └── resources.py       # Resource detection/limits
│       ├── validation/
│       │   ├── consensus.py       # Replicate consensus checking
│       │   ├── schema.py          # Output schema validation
│       │   ├── outliers.py        # Outlier detection
│       │   └── retry.py           # Failed unit re-queue logic
│       ├── credits/
│       │   ├── calculator.py      # Credit calculation
│       │   └── leaderboard.py     # Team/individual rankings
│       └── config.py
├── tests/
└── scripts/
    ├── sync_job.py
    ├── fetch_results.py
    └── monitor.py
```

## Quick Start

```bash
cd src/compute-broker
uv pip install -e .

# Configure BOINC Central project
python -m compute_broker.boinc.project_config \
  --project-key YOUR_KEY \
  --project-url https://boinc.berkeley.edu/central/your-project

# Translate job to BOINC work units
python -m compute_broker.boinc.workgen \
  --job-spec ../../experiment-engine/job-spec.yaml \
  --output-dir /path/to/boinc/workgen

# Fetch and validate results
python -m compute_broker.boinc.result_handler \
  --job-id EXP-H9182-VS-001 \
  --output results/
```