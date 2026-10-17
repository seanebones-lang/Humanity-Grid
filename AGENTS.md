# Working on Humanity Grid

## Orientation

Read [README.md](README.md), [Proof A review](docs/PROOF_A_REVIEW.md) and
[the frozen package](proofs/EXP-001-v1/README.md). This is a pre-alpha local
infrastructure/review kit, not an installed volunteer-compute network or a
validated scientific discovery. Check Git status and preserve unrelated work.

## Begin with the offline byte check

From the root, with Python 3.9 or later:

```sh
python3 proofs/EXP-001-v1/tools/verify.py
python3 proofs/EXP-001-v2/tools/verify.py
python3 ingest_exp001.py --help
```

The verifier checks manifested byte lengths/digests and frozen consensus/Witness
record relationships. It does not rerun docking, establish source identity or
prove biological activity. A missing artifact is a failure to report, never an
invitation to invent replacement historical evidence.

The original `proof-a-v1` tag is incomplete; current main and the separately
versioned v2 review package contain the exact archived files. Read
[the correction record](docs/PROOF_A_CORRECTIONS.md) before claiming that an
older review target passed. V2 score reanalysis is not a new docking run.

For the fuller reviewer checks use Python 3.12 in a disposable virtual environment:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-review.txt
python -m pip install ./src/experiment-engine
python -m pip check
python -m unittest discover -s tests -v
```

[CI](.github/workflows/ci.yml) defines package, consensus, web preview and Witness
replay gates. Individual components have their own manifests; there is no single
root app installer. Installs may download dependencies. Docking execution needs
separate Docker/Vina/Open Babel preparation; do not silently start paid compute.

## Evidence and interoperability boundaries

- Keep the frozen `proof-a-v1` history and `proofs/EXP-001-v1` evidence immutable.
  New experiments need new identities/manifests and declared criteria, not edits
  that make historical receipts appear to have passed a later check.
- Preserve Observed/Inferred/Generated distinctions and complete premise links.
  Replaying saved records is not an independent computational replication.
- Use a separate fresh local Witness store for replay. The current Witness API
  has unauthenticated mutation and must remain on loopback for this workflow.
- Repository MIT licensing does not relicense every upstream dataset or artifact.
  Read [artifact rights](proofs/EXP-001-v1/LICENSES.md) before redistribution.
- External review, scientific validity, source custody and operational readiness
  remain distinct from checksum checks and successful local CI.

## Handoff

Record revision, exact inputs and commands, results, environment and remaining
proof gaps. Do not claim a drug candidate, efficacy or independently verified
science from the two-run local agreement statistic. Keep private credentials,
personal data and unreviewed generated claims out of evidence packages.
