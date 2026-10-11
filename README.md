<img width="1168" height="784" alt="yxFNg" src="https://github.com/user-attachments/assets/0e5a3dad-498e-44cf-bc63-e43ea8605244" />

# Humanity Grid

**A pre-alpha toolkit for reviewing local computational experiments and preserving their evidence in Witness. The long-term goal is a public-benefit volunteer computing network.**

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

Independent reviewers should use the [external review guide](docs/EXTERNAL_REVIEW.md).
The current invitation is to inspect and criticize the frozen proof, then help
define an independently designed Proof B — not to endorse a scientific result.

For attribution, reuse, and packaged-artifact boundaries, see
[CITATION.cff](CITATION.cff), [NOTICE](NOTICE),
[LICENSE-POLICY.md](LICENSE-POLICY.md), and
[the EXP-001 artifact-rights note](proofs/EXP-001-v1/LICENSES.md).

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
or volunteer platform release artifact yet. A pinned `requirements-review.txt` now covers the bounded local reviewer tools. Use the component documentation only for focused
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

## First experiment: what is available today

The frozen EXP-001 package contains two local Vina runs over six compounds, score files, a correlation report, and a Witness snapshot. The reviewer path verifies all 43 artifacts, compares every stored field in the snapshot and export, reanalyses the scores, and replays 12 Observed / 2 Inferred / 1 Generated records into a fresh local Witness database. It does not prove docking enrichment, biological efficacy, independent execution, or an operating distributed scheduler.

## Volunteer interface preview

The web interface is a design preview. Its resource and cause controls describe planned preferences; they do not start computing, change machine settings, or connect to BOINC. No volunteer contributions or published research are claimed. The native Tauri wrapper remains unsupported development scaffolding and is outside the supported reviewer launch. See [its current status](src/volunteer-app/README.md).

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
