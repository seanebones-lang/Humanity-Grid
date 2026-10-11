# Experiment Engine: local job specifications

This component validates, hashes, saves, and reloads job specifications. Its two
CLI scripts create a draft from the `virtual_screening` template and emit
sequential work-unit configuration ranges. They do not run or dispatch work.

## Install the supported package

From the repository root, using the tested Python 3.12 environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-review.txt
.venv/bin/python -m pip install ./src/experiment-engine
.venv/bin/python -m pip check
```

The installed import is `experiment_engine.jobs.spec`. There are no installed
`jobs.create`, `jobs.validate`, `jobs.split`, or dataset registration commands.
The actual CLI scripts below are run from the source checkout.

## Create and inspect a synthetic draft

Run these commands from the repository root. The approval and software fields
in this example are **synthetic declarations**, not a research authorization or
attestation. The template's `TODO` input/container hashes remain placeholders;
this output is a draft for review and must not be dispatched.

```bash
.venv/bin/python src/experiment-engine/scripts/create_job.py \
  --template virtual_screening \
  --job-id DEMO-001 --hypothesis-id H-DEMO --name 'Synthetic configuration review' \
  --overrides '{"work_units":{"total":2,"compounds_per_unit":3},"provenance":{"hypothesis_id":"H-DEMO","researcher_approval":"synthetic:unapproved","approval_timestamp":"2026-10-01T00:00:00Z","git_commit":"synthetic-fixture"}}' \
  --output /tmp/humanity-grid-job-demo.yaml

.venv/bin/python src/experiment-engine/scripts/split_work_units.py \
  /tmp/humanity-grid-job-demo.yaml --output /tmp/humanity-grid-work-unit-demo
```

The first command prints a computed job hash. The second emits two JSON files
with inclusive ranges `[0, 2]` and `[3, 5]`. Each preserves the job hash, declared
input hashes, container specification, binding site, and docking parameters.
It does not open a compound library or materialize those ranges.

## Validation and trust boundaries

- Reloading a saved specification recomputes its hash and rejects a mismatch.
- The top-level and provenance hypothesis IDs must agree.
- Runtime estimates and caps are finite and positive; estimates cannot exceed
  the cap. Consensus thresholds are between zero and one, with redundancy of
  at least two.
- Input metadata rejects unknown fields. Inline docking parameters belong in
  the input's `parameters` object, not beside `source` and `sha256`.
- The splitter rejects random/stratified strategies, `--library-path`, and
  external JSON parameter files without explicit inline parameters.

A hash detects a change to a saved specification. It does not verify declared
source bytes, authenticate a researcher, approve scientific work, or establish
that a container exists or ran. Before execution, independently source and
verify input bytes, seal the software environment, obtain real authorization,
and implement a reviewed execution boundary.

## Implemented source

- `src/experiment_engine/jobs/spec.py`: Pydantic models, template, validation,
  serialization, and job hash computation.
- `scripts/create_job.py`: create a draft YAML specification.
- `scripts/split_work_units.py`: emit sequential JSON configurations.

Dataset download/cataloguing, job registration, scheduling, provenance stores,
retry execution, and distributed worker management are planned features. They
are not present in this package. For the currently supported evidence review
workflow, see [Proof A review](../../docs/PROOF_A_REVIEW.md).
