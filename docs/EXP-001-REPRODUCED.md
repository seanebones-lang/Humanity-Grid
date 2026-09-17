# CDK2 Validation — Real End-to-End Record (EXP-001)

**Date**: 2026-09-16
**Pipeline**: AutoDock Vina (CPU) -> redundant replicates -> consensus -> Grid→Witness bridge

This is Proof A (infrastructure): does the same work unit, run twice with
pinned parameters, produce concordant results that survive consensus, and can
the whole trail be deposited into Witness as an inspectable Record?

**This is deliberately boring.** It is not a drug discovery claim. It proves
the *machine* works end to end on the *first mission*. The science comes later
with a real lab question.

---

## 1. Target & Data

| Item | Value |
|------|-------|
| Protein | CDK2 (Cyclin-dependent kinase 2) |
| PDB | `1KE7` (2.0 Å, CDK2 + co-sovereign ligand) |
| Binding site center | `[-9.11, 48.31, 11.80]` (LS3 ligand pocket) |
| Box size | `[24, 24, 24]` Å |
| Engine | AutoDock Vina 1.2 (CPU — runs on any volunteer machine) |
| Library | 6 real CDK2 inhibitors (ChEMBL-annotated literature actives) |

The binding-site center was extracted from the co-crystallized LS3 ligand,
not guessed — the earlier attempt used a fabricated center that produced
garbage (near-zero) scores. Real coordinates are the difference between
meaningless output and reproducible output.

---

## 2. Redundant Execution (two "volunteer" machines)

Each replicate ran the same 6 compounds with pinned parameters, differing
only in the RNG seed (which is the honest real-world case: volunteers run
identical jobs independently).

| Compound | Rep 1 affinity (kcal/mol) | Rep 2 affinity (kcal/mol) |
|----------|---------------------------|---------------------------|
| CHEMBL331829 | -6.927 | -6.740 |
| CHEMBL434844 | -6.856 | -6.865 |
| CHEMBL2106406 | -7.847 | -7.847 |
| CHEMBL363112 | -6.567 | -6.542 |
| CHEMBL495686 | -7.027 | -7.597 |
| CHEMBL1234501 | -6.593 | -6.532 |

---

## 3. Consensus (the disagreement rule)

`src/compute-broker/scripts/validate_consensus.py`

- Pearson correlation rep1 vs rep2: **r = 0.885**
- Threshold: r ≥ 0.80
- Outcome: **PASSED** (1/1 work units)
- Outliers flagged (IQR): 1 (CHEMBL495686, the largest rep1↔rep2 spread)

**The disagreement rule works.** Scores agree within tolerance, consensus is
accepted, and the one outlying compound is flagged rather than silently
folded in. Had r < 0.80, the work unit would be re-queued (or fail loud).

---

## 4. Deposit into Witness (the Record)

`src/compute-broker/scripts/witness_bridge.py` deposits the experimental
trail into a running Witness API using only the Python standard library
(`urllib`). It enforces Witness's three epistemic categories:

| Category | What | Witness author |
|----------|------|----------------|
| **Observed** | raw best-affinity scores from each replicate | `compute:grid-EXP-001-...` (instrument) |
| **Inferred** | consensus (premises = both observed nodes, falsifier attached) | `humanity-grid:consensus-engine` (software) |
| **Generated** | Research Scout hypothesis prose (`human_reviewed:false`) | `research-scout:scout-v1` (model) |

Live write-through verified against the Witness API on port 8090:

```
Observed [rep1] cdk2-wu-001: -7.847 kcal/mol -> c94b3c4c-...
Observed [rep2] cdk2-wu-001: -7.847 kcal/mol -> 88b7b21f-...
Inferred consensus -> d81a4815-...
Generated hypothesis -> e915497c-...
```

The consensus **inference** carries `parents = [observed_rep1, observed_rep2]`
and an explicit falsifier: *"A third independent work-unit run on the same
slice disagrees past the consensus threshold."* The **generation** is stored
with `human_reviewed:false` — it is never auto-promoted to a measurement.

Query confirmed from the run:
- `GET /api/nodes?type=observed&domain=cancer-screening` → 2 replicate brains
- `GET /api/nodes?type=inferred&domain=cancer-screening` → consensus with premises + falsifier
- `GET /api/nodes?type=generated&domain=cancer-screening` → scout hypothesis

---

## 5. What this proves

The pipeline closes the loop that the whole project is about:

1. Write a job → 2. ship an experiment to compute → 3. verify redundant
   consensus → 4. chain the evidence into an inspectable, category-strict
   Record → 5. keep Scout prose labeled as Generated until a human says
   otherwise.

The volunteer app is the shell. This is the machine. And the machine is
verified end to end.

---

## 6. What this does NOT prove (and must not be claimed to)

- Docking enrichment / discovery (that is Proof B, bias-controlled, later).
- That AutoDock-GPU ran — this ran Vina (CPU). GPU validation needs NVIDIA.
- Any biological or clinical claim. All six ligands are known actives; the
  point is reproducibility of the *pipeline*, not activity.

---

## 7. Reproduce it

```bash
# 0. Requirements: docker, a Witness API on :8090 (fresh DB)
# 1. Prepare rigid receptor
python3 validation/rigidify.py validation/output/prep/1KE7.pdbqt validation/output/prep/1KE7_rigid.pdbqt

# 2. Run two replicates inside the container (openbabel + vina + rdkit + polars)
for rep in 101 202; do
  docker run --rm --user root -v "$PWD/validation:/work" -w /work \
    humanity-grid/autodock-gpu:val-1 \
    bash -lc "apt-get update >/dev/null 2>&1 && apt-get install -y openbabel >/dev/null 2>&1 && \
      python3 run_vina_replicate.py --receptor /work/output/prep/1KE7_rigid.pdbqt \
        --out /work/output/results --work-unit-id cdk2-wu-001 \
        --exhaustiveness 8 --seed $rep"
done
# shuffle into rep1/ rep2/
mkdir -p validation/output/results/rep1 validation/output/results/rep2
cp -r validation/output/results/cdk2-wu-001 validation/output/results/rep1/
cp -r validation/output/results/cdk2-wu-001 validation/output/results/rep2/

# 3. Consensus
uv run --python /tmp/gridvenv/bin/python src/compute-broker/scripts/validate_consensus.py \
  --job-id EXP-001 --results-dir validation/output/results \
  --redundancy 2 --threshold 0.8 --output validation/output/results/consensus.json

# 4. Bridge the whole Record into Witness
uv run --python /tmp/gridvenv/bin/python src/compute-broker/scripts/witness_bridge.py \
  --witness http://127.0.0.1:8090 --job-id EXP-001 --hypothesis H-9182 \
  --results-dir validation/output/results --report validation/output/results/consensus.json \
  --domain cancer-screening --pdb 1KE7
```

Result files are in `validation/output/results/` (`rep1/`, `rep2/`,
`consensus.json`), receptor in `validation/output/prep/1KE7_rigid.pdbqt`.