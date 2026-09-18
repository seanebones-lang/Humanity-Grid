# EXP-001 Proof A package, version 1

This is a frozen, local computational-infrastructure demonstration. It contains
the exact files available from the two specified AutoDock Vina CPU runs, their
consensus report, and the Witness graph created by a fresh replay through the
current public REST API.

It does **not** establish a drug candidate, biological activity, docking
enrichment, scientific discovery, independent computation, or external review.

## Verify without network access

```bash
python3 proofs/EXP-001-v1/tools/verify.py
```

The verifier checks every manifested file's SHA-256 digest and byte length,
checks the frozen consensus values, checks the 12 Observed / 2 Inferred / 1
Generated Witness graph, checks that consensus links twelve premises, and checks
that the JSON record export matches the SQLite snapshot.

It deliberately does not recompute docking, parse Parquet result values, verify
the content identifiers from the Rust implementation, or infer scientific
validity. Those are distinct tasks for a future independently reviewed Proof B.

## Contents

| Path | Role |
| --- | --- |
| `inputs/1KE7.pdb` | PDB source structure used locally |
| `inputs/1KE7_rigid.pdbqt` | Prepared rigid receptor used by the Vina runs |
| `outputs/vina/rep1/` | Run-one ligand, pose, SMILES, and Parquet output files |
| `outputs/vina/rep2/` | Run-two ligand, pose, SMILES, and Parquet output files |
| `outputs/consensus.json` | Frozen agreement report |
| `outputs/witness/records.json` | Exact exported EXP-001 Witness records from a fresh replay |
| `outputs/witness/proof-a-review.db` | SQLite snapshot corresponding to the record export |
| `manifest.json` | SHA-256 and byte counts for all packaged artifacts |

## Interpretation boundary

The visible agreement statistic is Pearson `r = 0.8849788400337059` for two
specified score vectors and a local rule of `r >= 0.80`. It says those score
vectors agree under that metric. It does not validate affinity predictions,
biological activity, or the experimental method.

The initial raw result files were generated locally and are now preserved in
this repository. Their inclusion establishes a reproducible byte package, not
independent custody or external provenance. The PDB source is identified by
its embedded PDB record; reviewers should consult RCSB PDB for source terms and
metadata before downstream redistribution.
