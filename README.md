<img width="1168" height="784" alt="yxFNg" src="https://github.com/user-attachments/assets/0e5a3dad-498e-44cf-bc63-e43ea8605244" />

# Humanity Grid

**A global, open-source scientific computing network that continuously turns unused computers into experiments aimed at important human problems.**

> **Current review status:** Humanity Grid is pre-alpha. The supported scientific
> review path is the frozen local EXP-001 infrastructure demonstration, not a
> public volunteer network or drug-discovery result. Start with
> [Proof A: scientific review and local replay](docs/PROOF_A_REVIEW.md).

## Start here

There is not yet a supported installer for a volunteer-computing platform. The
supported path for researchers and technical reviewers is a local, loopback-only
Proof A replay that verifies the Grid-to-Witness record contract:

```bash
git clone https://github.com/seanebones-lang/witness.git && \
git clone https://github.com/seanebones-lang/Humanity-Grid.git
```

Then follow the two-terminal commands in
[Proof A: scientific review and local replay](docs/PROOF_A_REVIEW.md). The
guide states exactly what the replay verifies, what it does not verify, how to
inspect the result, and how to report a failure.

The frozen local artifacts and Witness record snapshot are also available in the
[checksummed EXP-001 Proof A package](proofs/EXP-001-v1/README.md).

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

## Component development status

The repository contains early component scaffolds for compute brokerage,
experiment definition, research scouting, open results, and a volunteer app.
They are not one installed platform and must not be represented as an operating
global compute network.

Each Python component has its own `pyproject.toml`; there is no repository-root
`requirements.txt`, unified dependency lock, provisioned BOINC control plane,
or release artifact yet. Use the component documentation only for focused
development work after completing the Proof A review path.

See [Proof A: scientific review and local replay](docs/PROOF_A_REVIEW.md) for
the only currently supported installation and use instructions.

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
