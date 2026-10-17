# Proof A: scientific review and local replay

**Status:** frozen local infrastructure demonstration, not an independently
reviewed scientific result.

**Review correction:** Use the [version 2 package](../proofs/EXP-001-v2/README.md)
and [correction record](PROOF_A_CORRECTIONS.md). The original `proof-a-v1` tag
is retained with its known defects. V2 restores the complete review target,
distinguishes score outliers from difference outliers, and documents the safer
seed-specific rerun path. It is not a new molecular-docking experiment.

Proof A exercises the boundary between the three systems:

1. Research Scout proposes a hypothesis and it remains **Generated**.
2. Humanity Grid records two specified AutoDock Vina CPU runs as computational
   outputs.
3. Witness stores the outputs as **Observed** records, their bounded agreement
   as **Inferred**, and the Scout text separately as **Generated**.

The demonstration does not establish a drug candidate, biological efficacy,
clinical relevance, docking enrichment, external validity, or independent
reproduction.

## What the frozen demonstration contains

| Item | Frozen value |
| --- | --- |
| Target | CDK2, PDB `1KE7` |
| Pocket | LS3 co-crystallized ligand pocket, `[-9.11, 48.31, 11.80]` |
| Engine | AutoDock Vina CPU 1.2.5 |
| Compounds | Six ChEMBL-labelled CDK2 actives |
| Runs | Seeds `101` and `202` |
| Agreement statistic | Pearson `r = 0.8849788400337059` |
| Rule | Predeclared local agreement threshold `r >= 0.80` |
| Current difference reanalysis | `CHEMBL495686`, absolute delta `0.570`; IQR of between-run absolute differences |
| Historical single-run score outlier | `CHEMBL2106406`; different variable from the difference reanalysis |
| Witness graph | 12 Observed, 2 Inferred, 1 Generated |

The claim is only that these two specified runs agree under this statistic and
that the resulting record graph can be deposited and inspected. A correlation
of six docking scores does not validate biological affinity predictions.

## Install prerequisites

- Git
- Python 3.9 or later; record replay uses only the standard library
- Current stable Rust and Cargo for Witness
- Docker, AutoDock Vina, Open Babel, and the scientific Python dependencies
  only if you intend to re-execute the docking run. Re-execution is not a
  one-command supported workflow yet.

Clone both repositories beside each other:

```bash
git clone https://github.com/seanebones-lang/witness.git && \
git clone https://github.com/seanebones-lang/Humanity-Grid.git
```

## One-command record replay

This verifies that the frozen Proof A record topology can be written through the
current public Witness REST API. It does **not** rerun docking and does not turn
the embedded frozen values into newly independently observed scientific data.

Terminal 1, from the Witness checkout:

```bash
DATABASE_URL="sqlite://$PWD/proof-a-review.db" HOST=127.0.0.1 PORT=18080 \
  cargo run --release --locked --package witness-api
```

Terminal 2, from the Humanity Grid checkout:

```bash
python3 ingest_exp001.py --witness http://127.0.0.1:18080
```

Expected terminal summary:

```text
Observed EXP-001 records: 12 (expected 12)
Inferred EXP-001 records: 2 (expected 2)
Generated EXP-001 records: 1 (expected 1)
All records verified successfully
```

Run the same command again to confirm idempotent reuse rather than duplicate
creation. The consensus record must list twelve parent UUIDs.

## Inspect the record

With Witness still running, open:

```text
http://127.0.0.1:18080/experiments/EXP-001
```

The page is a review aid. Inspect the dynamic record list and the REST API;
do not treat static text on the page as proof that the database contains the
records. To inspect the result without the page:

```bash
curl -s 'http://127.0.0.1:18080/api/nodes?label=EXP-001&type=inferred&limit=50'
```

## Re-executing the computation

The implementation and the frozen local outputs are documented in
[EXP-001-REPRODUCED.md](EXP-001-REPRODUCED.md). The committed consensus report
is at `validation/output/results/consensus.json`.

The raw receptor preparation, ligand PDBQT files, and result artifacts are now
preserved as the versioned, checksummed
[EXP-001 Proof A package](../proofs/EXP-001-v1/README.md). A reviewer can
verify its digests, consensus report, and exported Witness graph offline from a
clone. The package does not yet permit a fully independent re-execution because
the execution environment, container digest, and independent input sourcing
remain incomplete. Closing those gaps is the first Proof B readiness task.

## Troubleshooting

| Symptom | Resolution |
| --- | --- |
| `Cannot reach Witness API` | Start the Witness server first and make sure the replay URL and `PORT` match. |
| Lookup, pagination, or matching-payload error | Replay refuses to guess or overwrite; use an isolated fresh database and preserve the failure. |
| `400` from an ingest route | Confirm the Witness checkout contains the current REST-ingest API and that the server was restarted after building. |
| `500` from an ingest route | Preserve the terminal output and request context. Do not retry against a shared database until the cause is understood. |
| Record count is greater than expected | Use a fresh `proof-a-review.db`. The script deliberately reuses matching EXP-001 records, but a manually altered database can contain other records. |
| Docker/Vina workflow fails | This does not invalidate the record replay. Document the platform, tool version, command, and failure before treating it as a reproducibility result. |

## Frequently asked questions

**Does this replay rerun AutoDock Vina?** No. It replays the frozen record
content into a new local Witness database and checks the public API and graph
relationship. Re-executing docking requires a sealed execution environment and independently sourced inputs; the historical byte package is now committed.

**Does `r = 0.885` validate CDK2 binding or a drug candidate?** No. It describes
agreement between the two specified docking score vectors. It makes no claim
about wet-lab affinity, enrichment, efficacy, safety, or therapeutic value.

**Are the two runs independent scientific replications?** They are two specified
computational runs with different seeds. Hardware/operator/environment
independence is not yet established by the public proof package.

**Can I expose Witness to collaborators on a network?** No. The current
prototype has unauthenticated write routes and is intended for loopback-only
review use.

**What is the next scientifically meaningful contribution?** Help specify and
review the sealed Proof B package before execution: inputs, software digests,
environment capture, preregistered success criteria, an independent question
owner, and an external reproduction path.

## Questions reviewers can answer now

- Does the generated/observed/inferred separation make sense for this workflow?
- Does a two-run agreement statistic justify the stated limited inference?
- Are the frozen parameters and failure provenance sufficiently represented?
- What inputs, software digests, environment metadata, and review gates must a
  portable Proof B package include?
- What would falsify or narrow the local reproducibility claim?

## Score reanalysis and regression checks

These commands reanalyse the committed scores, without executing docking. This locked analysis environment is tested on Python 3.12; record replay itself needs only standard-library Python 3.9+. Use Python 3.12 for the pinned NumPy environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-review.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python src/compute-broker/scripts/validate_consensus.py --job-id EXP-001 --results-dir proofs/EXP-001-v1/outputs/vina --output /tmp/humanity-grid-consensus.json
```

Use one replay process at a time against a disposable database. Writes are sequential, not an atomic batch: if a later write fails, earlier accepted records remain and can be checked on retry. Matching labels alone never authorize reuse; payloads and provenance must also agree. Requests are bounded, have timeouts, and reject redirects and remote API destinations.
