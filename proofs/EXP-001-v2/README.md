# EXP-001 Proof A review package, version 2

This corrected package addresses [Witness issue 9](https://github.com/seanebones-lang/witness/issues/9).
It preserves the original raw score, ligand, pose, receptor and Witness-export
bytes. The original `proof-a-v1` tag and `proofs/EXP-001-v1` directory are not
rewritten. See the [correction record](../../docs/PROOF_A_CORRECTIONS.md).

## Offline byte and record verification

```sh
python3 proofs/EXP-001-v2/tools/verify.py
```

All 45 manifested artifacts must be present and match their byte lengths and
SHA-256 digests. The verifier also checks the recorded consensus fields and
historical Witness graph/export. It does not parse the Parquet files, rerun
Vina, independently recompute the statistics or validate biology.

`outputs/consensus-historical-v1.json` is the unchanged historical report.
`outputs/consensus.json` is a current reanalysis of the same two archived score
vectors. `outputs/outlier-analysis.json` records both the old single-run score
IQR rule (CHEMBL2106406) and the between-run difference rule (CHEMBL495686),
including variables, linear quartiles, fences and flagged values. The
historical Witness export has not been changed to impersonate a later analysis.

## Reanalyse the Parquet scores

Use the pinned Python 3.12 reviewer environment described in the
[review guide](../../docs/PROOF_A_REVIEW.md):

```sh
.venv/bin/python src/compute-broker/scripts/validate_consensus.py \
  --job-id EXP-001 --results-dir proofs/EXP-001-v2/outputs/vina \
  --threshold 0.8 --output /tmp/exp001-reanalysis.json
```

Pearson correlation includes all six compounds, approximately 0.8849788400337059.
The one IQR difference outlier does not change that calculation. Agreement is
under a local threshold of 0.80, not a scientific validity threshold.

Read [artifact rights and sources](LICENSES.md) before reuse. This package does
not establish input authenticity, independent custody/execution, docking
correctness, biological activity, efficacy or a drug candidate. There was no
new molecular-docking run or Witness API replay for this correction.
