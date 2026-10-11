> **Pre-alpha component:** this document includes planned behavior. This component is not part of an installed, verified volunteer platform. Start with the repository root and the supported local Proof A reviewer path; do not infer scientific validity, deployed services, or independent execution from these design descriptions.

# Research Scout: proposed hypothesis workflow

**AI-powered literature ingestion, citation graph construction, and hypothesis generation for scientific discovery.**

## Planned responsibilities

- Ingest scientific literature from PubMed, bioRxiv, arXiv, patents
- Build and maintain citation graph
- Extract structured claims (protein targets, pathways, compounds, results)
- Generate computational hypotheses with evidence
- Human-review queue for scientist approval

## Data Sources

| Source | Type | Access |
|--------|------|--------|
| PubMed | Biomedical literature | NCBI E-utilities API |
| bioRxiv | Preprints (biology) | Cold Spring Harbor API |
| arXiv | Preprints (physics, ML, etc.) | arXiv API |
| Google Patents | Patent documents | Public API / bulk download |
| ChEMBL | Bioactive molecules | EBI REST API |
| PubChem | Chemical information | NCBI REST API |
| PDB | Protein structures | RCSB REST API |
| UniProt | Protein sequences/annotations | UniProt REST API |
| BindingDB | Binding affinities | Download / REST |

## Hypothesis Format

```json
{
  "hypothesis_id": "H-9182",
  "created_at": "2026-09-16T14:30:00Z",
  "target": {
    "protein": "KRAS",
    "uniprot_id": "P01116",
    "binding_site": "G12C pocket",
    "pdb_ids": ["6O0M", "6O0N"]
  },
  "question": "Can known covalent inhibitors bind the G12C pocket with improved selectivity?",
  "rationale": [
    "PMID:36543210 - New allosteric pocket discovered in KRAS G12C",
    "PMID:37123456 - Three independent groups confirm pathway dependency",
    "PMID:35987654 - Failed EGFR inhibitor shows KRAS cross-reactivity"
  ],
  "proposed_computation": {
    "type": "virtual_screening",
    "library": "ChEMBL_approved_drugs",
    "docking_engine": "AutoDock-GPU",
    "compounds": 2_000_000,
    "estimated_gpu_hours": 280_000
  },
  "review_status": "pending",
  "reviewer": null,
  "review_notes": null
}
```

## Proposed architecture

```
research-scout/
├── pyproject.toml
├── src/
│   └── research_scout/
│       ├── __init__.py
│       ├── ingest/
│       │   ├── pubmed.py
│       │   ├── biorxiv.py
│       │   ├── arxiv.py
│       │   ├── patents.py
│       │   └── base.py
│       ├── graph/
│       │   ├── citation_graph.py
│       │   ├── entity_extraction.py
│       │   └── claim_extraction.py
│       ├── hypothesis/
│       │   ├── generator.py
│       │   ├── templates.py
│       │   └── evidence.py
│       ├── review/
│       │   ├── queue.py
│       │   └── notifications.py
│       └── config.py
├── tests/
└── scripts/
    ├── ingest_literature.py
    ├── build_citation_graph.py
    └── generate_hypotheses.py
```

## Supported review entry point

The former quick-start examples described future modules or unverified container
paths. They are not supported installation instructions and are intentionally
omitted here. No portal, model pipeline, or production container is released
through this component document.

Start with the [local Proof A reviewer workflow](../../docs/PROOF_A_REVIEW.md)
and the [frozen artifact package](../../proofs/EXP-001-v1/README.md). Those checks
do not run new experiments, invoke a model, publish data, or establish scientific
validity. The design above is a proposal for implementation and separate review.
