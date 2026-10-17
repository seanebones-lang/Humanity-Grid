# Proof A review correction, version 2

This addresses the bounded findings in [Witness issue 9](https://github.com/seanebones-lang/witness/issues/9).
The original `proof-a-v1` tag and `proofs/EXP-001-v1` evidence are preserved.
Version 2 is a corrected review package and score reanalysis, not a new docking
experiment or an independent scientific reproduction.

## Package completeness

The original tag contains 19 of the 43 manifested artifacts. The missing 24
are twelve SMILES files and twelve docked poses, excluded by broad ignore rules.
Current main restored all 43 exact manifested files before this correction.
The separate `proofs/EXP-001-v2` package retains their original bytes, keeps the
old consensus as `outputs/consensus-historical-v1.json`, and adds a current
consensus and an explicit outlier-analysis record. Its manifest covers all 45
artifacts. Artifact-specific reuse terms remain in `LICENSES.md`.

## Two different outlier questions

The historical validator applied a two-sided IQR rule to replicate one's
affinity scores. That flags `CHEMBL2106406`. The accompanying prose described
between-run disagreement and named `CHEMBL495686` instead. Both produce one
outlier; equal counts concealed different meanings.

Current analysis applies the rule to each compound's absolute score difference
between the matched replicate pair. It flags `CHEMBL495686`, with a difference
of approximately `0.570 kcal/mol`. Both analyses, their variables, linear
quartiles, factor, fences and compound identifiers are recorded in v2.
Pearson correlation still uses all six compounds: approximately
`0.8849788400337059`, meeting the historical local threshold of `0.80`.
An outlier flag does not remove a compound or establish biological validity.

The historical Witness export remains historical. It is not rewritten to
pretend that the newer analysis was recorded at the original execution time.

## Preserve each execution

The old recipe ran seeds 101 and 202 into one directory, then copied its final
contents to both replicate directories. Followed literally, this can compare
the second result with itself. The already archived Parquet files differ;
this recipe defect does not prove how they were originally generated.

The corrected recipe writes directly to `rep1` and `rep2`. The runner refuses
an existing work-unit directory or docking pose, rejects failed processes and
nonfinite scores, and does not publish a partial compound set. Fixture tests
exercise separate seed outputs, repeat-run refusal, partial failure, stale
pose preservation and failed subprocess results. They use fictional values
and do not invoke Vina or Open Babel.

## Validation boundary

Verify the v2 package from a clean checkout:

```sh
python3 proofs/EXP-001-v2/tools/verify.py
```

Reanalyse the original Parquet scores with the pinned Python 3.12 environment:

```sh
.venv/bin/python src/compute-broker/scripts/validate_consensus.py \
  --job-id EXP-001 --results-dir proofs/EXP-001-v2/outputs/vina \
  --output /tmp/exp001-reanalysis.json
.venv/bin/python -m unittest discover -s tests -v
```

The dependency-free byte verifier checks digests, recorded analysis fields and
the stored Witness graph. It does not parse Parquet or independently recompute
the scientific analysis; the separate pinned analysis command does that.
No fresh molecular docking, biological validation, independent execution,
source-custody verification or new Witness API replay is claimed by this fix.
An immutable container digest, independent input sourcing and an externally
executed Proof B remain separate gates.
