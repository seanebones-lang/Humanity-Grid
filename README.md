<img width="1168" height="784" alt="yxFNg" src="https://github.com/user-attachments/assets/0e5a3dad-498e-44cf-bc63-e43ea8605244" />

# Humanity Grid

**A global, open-source scientific computing network that continuously turns unused computers into experiments aimed at important human problems.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Rust](https://img.shields.io/badge/rust-1.80+-orange.svg)](https://www.rust-lang.org/)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)

---

## Vision

Not: "Download this program and maybe it folds proteins."

Instead: **A continuously operating scientific discovery machine.**

Volunteers install a tiny application, choose a cause (cancer, Alzheimer's, antibiotic resistance, climate, clean energy, rare diseases), and their machine becomes one node in a giant public-benefit supercomputer.

---

## Architecture

```
Humanity Grid
├── Research Scout          # AI + databases → hypotheses
├── Experiment Engine       # Job definitions, datasets, provenance
├── Compute Broker          # BOINC adapter, CPU/GPU workloads, validation
├── Scientific Pipeline     # AutoDock, OpenMM, future modules
├── Open Results            # Raw data, analyses, citations, notebooks
└── Volunteer App           # Cross-platform, beautiful, honest
```

---

## Quick Start (Development)

### Prerequisites

- **Rust** 1.80+ (for Volunteer App)
- **Python** 3.12+ (for Research Scout, Experiment Engine, Scientific Pipeline)
- **Docker** (for containerized workloads)
- **BOINC client** (for local testing)

### Install Dependencies

```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Python (via uv - recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Or with pip
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Project Structure

```
humanity-grid/
├── SPEC.md                 # This specification
├── README.md               # This file
├── LICENSE                 # MIT License
├── docs/                   # Architecture, API, contributor guides
├── src/
│   ├── research-scout/     # Literature ingestion, hypothesis generation
│   ├── experiment-engine/  # Job definitions, datasets, provenance
│   ├── compute-broker/     # BOINC adapter, workload management
│   ├── scientific-pipeline/# AutoDock, OpenMM containers
│   ├── open-results/       # Data portal, notebooks, API
│   └── volunteer-app/      # Tauri (Rust + Web UI) cross-platform app
├── tests/                  # Integration tests
├── scripts/                # Dev ops, deployment, CI helpers
└── docker/                 # Dockerfiles for workloads
```

---

## First Experiment: Validation Pipeline

We start with a **boring but rigorous** experiment:

1. Take a known protein-ligand system with experimentally established results (e.g., CDK2 with known inhibitors from ChEMBL)
2. Run our distributed virtual screening pipeline
3. Verify we rediscover the expected active compounds with statistical significance
4. Publish all data, code, and analysis openly

This proves: **scheduler → machines → calculation → verification → aggregation → scientific reproducibility.**

---

## Volunteer App Preview

```
What do you want your computer working on tonight?

🧬 Cancer Research        ● Selected
🧠 Alzheimer's Research   ○
🦠 Antibiotic Discovery   ○
🌎 Climate Modeling       ○
🔋 Clean Energy           ○

Use my computer:       While idle  ▼
Maximum CPU:           30%         ████████░░
Maximum GPU:           40%         ██████████░░
Run on battery:        No
Pause above:           75°C
Electricity preference: Only during my chosen hours  ▼
```

**Then:**
> **Tonight your computer screened 18,421 candidate molecules for a pediatric cancer study.**

---

## No Bullshit Policy

- ❌ No cryptocurrency
- ❌ No NFTs
- ❌ No tokens
- ❌ No "AI discovers cure" claims
- ❌ No data selling
- ❌ No premium features

**Just: You helped science.**

---

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development setup, coding standards, and pull request process.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Links

- **Specification:** [SPEC.md](SPEC.md)
- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **API Reference:** [docs/API.md](docs/API.md)
- **Volunteer App:** [src/volunteer-app/README.md](src/volunteer-app/README.md)
- **Research Scout:** [src/research-scout/README.md](src/research-scout/README.md)
