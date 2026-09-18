# EXP-001 artifact rights and source boundary

This file separates the project-authored review materials from inputs and
outputs that may carry source-specific rights or terms. It is not a substitute
for reviewing those source terms for a proposed use.

| Material | Boundary |
| --- | --- |
| `README.md`, this file, `manifest.json`, and `tools/verify.py` | Original project review materials, offered under the repository MIT License. |
| `inputs/1KE7.pdb` | A source structure identified by a Protein Data Bank record. Humanity Grid does not claim to relicense the source record. Consult the record and RCSB PDB terms, citation guidance, and metadata before reuse. |
| `inputs/1KE7_rigid.pdbqt` | A local preparation derived from the source structure. It may remain subject to rights or terms applicable to its source and to the tools used to create it. |
| `outputs/vina/` | Locally generated calculation inputs and outputs, including data derived from named source materials. Their inclusion makes the byte package reviewable; it does not grant rights in any upstream dataset, identifier, structure, tool, or source data. |
| `outputs/witness/` | A local Witness record export and SQLite snapshot. The repository grants no independent right to source data represented in those records. |

The package makes no representation that any artifact is independently
authenticated, suitable for clinical, biological, regulatory, or commercial
use, or free of third-party restrictions. Cite the exact package version and
commit when discussing a review result.
