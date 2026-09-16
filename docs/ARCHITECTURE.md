# Humanity Grid Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HUMANITY GRID SYSTEM                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                 │
│  │ Research     │    │ Experiment   │    │ Compute      │                 │
│  │ Scout        │───▶│ Engine       │───▶│ Broker       │                 │
│  │              │    │              │    │ (BOINC)      │                 │
│  │ • PubMed     │    │ • JobSpec    │    │              │                 │
│  │ • bioRxiv    │    │ • Datasets   │    │ • Work gen   │                 │
│  │ • arXiv      │    │ • Provenance │    │ • Validation │                 │
│  │ • Hypothesis │    │ • Templates  │    │ • Credits    │                 │
│  └──────────────┘    └──────────────┘    └──────┬───────┘                 │
│                                                  │                          │
│                                                  ▼                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                 │
│  │ Open         │◀───│ Scientific   │◀───│ Volunteer    │                 │
│  │ Results      │    │ Pipeline     │    │ Nodes        │                 │
│  │              │    │              │    │              │                 │
│  │ • Data       │    │ • AutoDock   │    │ • BOINC      │                 │
│  │ • Notebooks  │    │ • OpenMM     │    │ • Docker     │                 │
│  │ • API        │    │ • Containers │    │ • Sandbox    │                 │
│  │ • Citations  │    │ • Reproducible│   │ • Thermal    │                 │
│  └──────────────┘    └──────────────┘    └──────────────┘                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Research Scout (`src/research-scout/`)
- **Purpose**: Ingest scientific literature, extract claims, generate hypotheses
- **Inputs**: PubMed, bioRxiv, arXiv, patents, ChEMBL, PubChem, PDB, UniProt, BindingDB
- **Outputs**: Structured hypotheses with evidence citations
- **Key Models**: `Paper`, `CitationEdge`, `Hypothesis`
- **Human-in-the-loop**: Review queue for scientist approval

### Experiment Engine (`src/experiment-engine/`)
- **Purpose**: Define reproducible computational experiments
- **Core Abstraction**: `JobSpec` — content-addressed, versioned, self-describing
- **Work Unit Splitting**: Deterministic partitioning of compound libraries
- **Validation Spec**: Redundancy, consensus threshold, outlier detection, retry policy
- **Provenance**: Full lineage from hypothesis → job → work unit → result → analysis

### Compute Broker (`src/compute-broker/`)
- **Purpose**: Bridge Experiment Engine → BOINC Central
- **Responsibilities**:
  - Translate `JobSpec` → BOINC work units
  - Stage datasets and container images to BOINC Central
  - Retrieve and validate results (redundancy + consensus)
  - Credit calculation and leaderboard aggregation
- **BOINC Central**: Managed server infrastructure (we don't run our own BOINC server)

### Scientific Pipeline (`src/scientific-pipeline/`)
- **Purpose**: Containerized scientific workloads with standardized interface
- **Containers**:
  - `autodock-gpu`: Virtual screening (CUDA 12.4, AutoDock-GPU, Vina fallback)
  - `openmm`: Molecular dynamics (CUDA 12.4, OpenMM 8.0)
- **Interface**: `/input/work_unit.json` → `/output/results.parquet` + `/output/metadata.json`
- **Content Addressing**: Container SHA256 baked into JobSpec

### Open Results (`src/open-results/`)
- **Purpose**: Public data portal with reproducible analyses
- **Storage**: S3/MinIO/GCS abstraction for raw data, processed results, notebooks
- **API**: FastAPI endpoints for projects, datasets, stats
- **Notebooks**: Auto-generated Quarto templates per experiment type
- **Publishing**: DataCite DOI minting, citation generation, BagIt export

### Volunteer App (`src/volunteer-app/`)
- **Purpose**: Cross-platform desktop client for volunteers
- **Stack**: Tauri 2 (Rust) + React 19 + TypeScript + Tailwind 4
- **Features**: Cause selection, resource controls, thermal/power management, team leaderboards
- **Security**: Sandbox execution, no filesystem/network access beyond work units
- **Offline-first**: SQLite queue, sync when online

## Data Flow: One Experiment

```
1. Research Scout ingests papers
   └─▶ Finds: "New allosteric pocket in KRAS G12C" (PMID:36543210)

2. Hypothesis generated (H-9182)
   └─▶ Target: KRAS G12C, Library: ChEMBL approved, Compute: 280k GPU-hours

3. Human scientist reviews & approves
   └─▶ Signs Research Manifest

4. Experiment Engine creates JobSpec (EXP-H9182-VS-001)
   └─▶ 2000 work units × 1000 compounds each
   └─▶ Input hashes: protein (pdb:6O0M), library (chembl:v32), params
   └─▶ Container: ghcr.io/humanity-grid/autodock-gpu@sha256:abc123...

5. Compute Broker → BOINC Central
   └─▶ Stages inputs, registers Docker image
   └─▶ Generates 2000 BOINC work units (2× redundancy = 4000)

6. Volunteer nodes compute
   └─▶ Download work unit + inputs
   └─▶ Run Docker container (sandboxed)
   └─▶ Upload results + metadata.json

7. Compute Broker validates
   └─▶ Schema check → Consensus (Pearson r > 0.8) → Outlier detection
   └─▶ Failed units re-queued (max 3 retries)

8. Open Results publishes
   └─▶ Raw Parquet + metadata → S3
   └─▶ Auto-generate analysis notebook
   └─▶ Public project page: H-9182
```

## Security Model

### Trust Boundaries
```
┌─────────────────────────────────────────────────────────────┐
│                    TRUSTED CONTROL PLANE                    │
│  Research Scout │ Experiment Engine │ Compute Broker       │
│  (authenticated researchers, signed manifests)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    UNTRUSTED EXECUTION PLANE                │
│  BOINC Central (managed) → Volunteer Nodes (anonymous)      │
│  • Signed Research Manifest required per job                │
│  • Approved container images only (pinned SHA256)           │
│  • Sandbox: no network, no host FS, CPU/GPU/RAM limits      │
│  • Thermal/power limits enforced                            │
│  • Results signed by container                              │
└─────────────────────────────────────────────────────────────┘
```

### Result Validation (Byzantine Fault Tolerance)
- **Redundancy**: Each work unit computed N× (default 2)
- **Consensus**: Pearson correlation between replicates ≥ threshold (default 0.8)
- **Outlier Detection**: IQR method on affinity scores
- **Retry**: Failed units re-queued up to max_retries (default 3)

## Reproducibility Guarantees

| Artifact | Content Addressing | Verification |
|----------|-------------------|--------------|
| JobSpec | SHA256 of canonical JSON | Embedded in provenance |
| Container Image | SHA256 digest (not tag) | Pinned in JobSpec |
| Input Datasets | SHA256 per file | Recorded in work unit |
| Results | SHA256 of output file | Validated on retrieval |
| Analysis Notebook | Git commit hash | Executed in CI |

## Deployment Topology

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Control Plane  │     │  BOINC Central   │     │  Data Plane      │
│  (our infra)    │────▶│  (Berkeley)      │────▶│  (S3/MinIO)      │
│                 │     │                  │     │                  │
│  • Research     │     │  • Scheduler     │     │  • Raw results   │
│    Scout        │     │  • Validator     │     │  • Notebooks     │
│  • Experiment   │     │  • Credit        │     │  • Project pages │
│    Engine       │     │  • Web UI        │     │  • API           │
│  • Compute      │     │                  │     │                  │
│    Broker       │     │                  │     │                  │
└─────────────────┘     └──────────────────┘     └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Volunteer Nodes  │
                    │ (worldwide)      │
                    │                  │
                    │  • BOINC Client  │
                    │  • Docker        │
                    │  • Sandbox       │
                    └──────────────────┘
```

## Technology Choices

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Distributed Compute | BOINC Central | Mature, handles heterogeneity, Docker support, managed |
| Virtual Screening | AutoDock-GPU | BOINC Central native support, proven in drug discovery |
| Molecular Dynamics | OpenMM | CUDA/HIP/OpenCL/Metal, Python API, production-grade |
| ML/Research Scout | Local LLMs + transformers | Privacy, cost control, reproducible |
| Containers | Docker / Podman | BOINC Central support, OCI standard |
| Volunteer App | Tauri 2 | Small binary, native performance, web UI |
| Data Storage | Parquet + SQLite + S3 | Analytical queries, ACID, cloud-native |
| Web Portal | Next.js + React | Existing NextEleven stack, Cloudflare Pages |
| API | FastAPI | Python-native, OpenAPI, async |

## Non-Goals (v1)

- ❌ Custom BOINC server (use BOINC Central)
- ❌ Generative "AI discovers cure" claims
- ❌ Cryptocurrency / tokens / NFTs
- ❌ Wet lab operations
- ❌ Clinical trials or medical advice
- ❌ Proprietary data or paywalled results