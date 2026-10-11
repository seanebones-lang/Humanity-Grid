# Compute Broker: local reviewer tools and planned architecture

**Current status:** no provisioned BOINC control plane, volunteer dispatch, automatic arbitration, or credit system is implemented as a supported platform. The supported tools are `scripts/validate_consensus.py` (local score-file reanalysis) and `scripts/witness_bridge.py` (local deposit of validated score aggregates and a bounded inference). Dependencies are pinned in the repository's `requirements-review.txt`.

The validator requires matching complete work-unit and compound sets, unique IDs, finite scores, and at least two nonconstant score vectors. It rejects empty experiments. IQR outliers use absolute differences between replicate pairs with linear quartiles. Agreement is a numerical property of supplied vectors, not biological validity or independent execution.

The bridge recomputes report correlations and checks all source files before its first write. Each replica's minimum score comes from its own file. Its inference explicitly states that those minimum-score premises do not contain the complete raw vectors. It makes no model call and emits no invented Research Scout generation. Writes are sequential and not idempotent: use a disposable local database; partial writes can remain if a later HTTP request fails. Use root `ingest_exp001.py` for the bounded historical example's verified reuse behavior.

Example, from the repository root:

```bash
.venv/bin/python src/compute-broker/scripts/validate_consensus.py --job-id EXP-001 --results-dir proofs/EXP-001-v1/outputs/vina --output /tmp/humanity-grid-consensus.json
.venv/bin/python src/compute-broker/scripts/witness_bridge.py --witness http://127.0.0.1:18080 --job-id EXP-001 --hypothesis EXP-001 --results-dir proofs/EXP-001-v1/outputs/vina --report /tmp/humanity-grid-consensus.json
```

A separate fresh Witness database must already be running. Neither command runs docking or dispatches work. Historical source identity and scientific correctness remain unverified.

## Planned architecture (not an available volunteer service)

BOINC work distribution, authenticated node identity, bounded container execution, independent redundant execution, arbitration, credits, GPU scheduling, and safe platform installers need implementation and separate verification. Design sketches in other project documents describe that future system; they are not evidence of deployed services.
