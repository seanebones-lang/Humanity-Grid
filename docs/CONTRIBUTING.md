# Contributing to Humanity Grid

Thank you for helping build a global scientific computing network. This document covers how to contribute code, report issues, and participate in the community.

## Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Be respectful, inclusive, and constructive.

## Ways to Contribute

| Area | Skills Needed | Entry Points |
|------|---------------|--------------|
| **Research Scout** | Python, NLP, bioinformatics | Literature clients, entity extraction, hypothesis templates |
| **Experiment Engine** | Python, Pydantic, data engineering | JobSpec validation, dataset providers, provenance tracking |
| **Compute Broker** | Python, BOINC, distributed systems | Work generation, result validation, consensus algorithms |
| **Scientific Pipeline** | Docker, CUDA, OpenMM, AutoDock | Container optimization, new workload types, GPU portability |
| **Open Results** | FastAPI, S3, Quarto, Jupyter | Data portal, notebook templates, DOI minting |
| **Volunteer App** | Rust, React, Tauri, TypeScript | UI components, system monitoring, BOINC integration |
| **Documentation** | Technical writing, science communication | Tutorials, API docs, architecture guides |
| **Science** | Computational biology, chemistry | Validation experiments, target selection, result interpretation |

## Development Setup

### Prerequisites

```bash
# Rust (for Volunteer App)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Python 3.12+ with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Docker
# https://docs.docker.com/get-docker/

# Node.js 22+ (for Volunteer App frontend)
fnm install 22
```

### Clone and Install

```bash
git clone https://github.com/seanebones-lang/Humanity-Grid.git
cd Humanity-Grid

# Python packages (each component is independent)
cd src/research-scout && uv pip install -e .[dev]
cd ../experiment-engine && uv pip install -e .[dev]
cd ../compute-broker && uv pip install -e .[dev]
cd ../scientific-pipeline && uv pip install -e .[dev]
cd ../open-results && uv pip install -e .[dev]

# Volunteer App
cd ../volunteer-app
npm install
# For Tauri development:
cargo install tauri-cli
```

### Run Tests

```bash
# Python components
cd src/research-scout && pytest -v
cd src/experiment-engine && pytest -v
# etc.

# Volunteer App
cd src/volunteer-app
npm run test        # frontend tests
cargo test          # Rust tests
npm run tauri dev   # dev server
```

## Project Structure

```
Humanity-Grid/
├── SPEC.md                 # Constitution — read first
├── README.md
├── LICENSE
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── CONTRIBUTING.md    # This file
├── src/
│   ├── research-scout/     # Literature ingestion + hypothesis gen
│   ├── experiment-engine/  # Job specs, datasets, provenance
│   ├── compute-broker/     # BOINC adapter + validation
│   ├── scientific-pipeline/# AutoDock/OpenMM containers
│   ├── open-results/       # Data portal + notebooks
│   └── volunteer-app/      # Tauri desktop app
└── tests/                  # Integration tests (planned)
```

Each `src/*` component is an independent Python package (or Rust for volunteer-app) with its own `pyproject.toml`/`Cargo.toml`.

## Pull Request Process

1. **Fork** the repo and create a feature branch: `git checkout -b feat/your-feature`
2. **Read SPEC.md** — ensure your change aligns with the vision and non-goals
3. **Write tests** — new code needs coverage; bug fixes need regression tests
4. **Run linters** — `ruff check . && mypy .` (Python), `cargo clippy` (Rust), `npm run lint` (TS)
5. **Update docs** — if you change behavior, update relevant `.md` files
6. **Commit** — conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
7. **Push and PR** — fill the PR template, link related issues

### PR Checklist

- [ ] Tests pass locally
- [ ] Linters clean
- [ ] No `node_modules`, `target/`, `__pycache__/`, `.venv/` in diff
- [ ] Docs updated if user-facing change
- [ ] CHANGELOG entry (for significant changes)
- [ ] Related issue linked

## Coding Standards

### Python
- **Formatter**: `ruff format` (Black-compatible)
- **Linter**: `ruff check` (strict)
- **Types**: `mypy --strict` — all public APIs must be typed
- **Imports**: `ruff` handles isort; use absolute imports from package root
- **Testing**: `pytest` with `pytest-asyncio` for async code
- **Dependencies**: Pin in `pyproject.toml`; use `uv` for lockfile

### Rust (Volunteer App)
- **Edition**: 2021
- **Linter**: `cargo clippy -- -D warnings`
- **Formatter**: `cargo fmt`
- **Async**: `tokio` with `#[tauri::command]` for IPC
- **Error Handling**: `anyhow` for app errors, `thiserror` for library errors

### TypeScript (Volunteer App Frontend)
- **Strict mode**: Enabled in `tsconfig.json`
- **Formatter**: Prettier (via `ruff` equivalent)
- **Components**: Functional + hooks, Tailwind for styling
- **State**: React Context + `useReducer` for complex state

### Docker
- **Multi-stage builds**: Builder → Runtime
- **Base images**: Official NVIDIA CUDA images for GPU workloads
- **Non-root user**: Always `USER appuser`
- **Entrypoint**: Single `/app/entrypoint.sh` → Python runner
- **Content addressing**: Publish with `sha256` digest, not tags

## Scientific Rigor Requirements

This is a **scientific computing** project. Code that produces or validates results has higher standards:

1. **Determinism**: Same input + same container = same output (bitwise where possible)
2. **Provenance**: Every result carries full lineage (JobSpec hash, container digest, input hashes)
3. **Validation**: Redundancy and consensus are not optional — they are the product
4. **Reproducibility**: Analysis notebooks must execute headless in CI
5. **Honesty**: "We rediscovered X" > "AI discovered cure for Y"

## Adding a New Scientific Workload

1. Add container in `src/scientific-pipeline/docker/<name>/`
2. Implement standardized interface (`/input/work_unit.json` → `/output/`)
3. Add JobSpec template in `experiment-engine/src/experiment_engine/jobs/spec.py`
4. Add validation logic in `compute-broker/src/compute_broker/validation/`
5. Add analysis notebook template in `open-results/quarto/templates/`
6. **Validation experiment**: Run known benchmark before merge

## Reporting Issues

Use GitHub Issues with these templates:

- **Bug Report**: Steps to reproduce, expected vs actual, logs, environment
- **Feature Request**: Use case, alignment with SPEC.md, implementation sketch
- **Science Question**: Target, literature, proposed computation, compute estimate
- **Security**: Email security@humanity-grid.org (do not file public issue)

## Community

- **Discussions**: GitHub Discussions for questions, ideas, science talk
- **Discord**: [invite link TBD] — real-time chat for contributors
- **Office Hours**: Monthly video call (announced in Discussions)
- **Mailing List**: `humanity-grid-announce@googlegroups.com` (low traffic)

## Recognition

Contributors are listed in:
- `AUTHORS.md` (code contributors)
- Project pages (science contributors: hypothesis authors, validators, lab partners)
- Papers (co-authorship for substantial scientific contributions)

## License

By contributing, you agree your contributions are licensed under the MIT License (see `LICENSE`).

---

**Questions?** Open a Discussion or email `contrib@humanity-grid.org`.