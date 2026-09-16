# Research Scout

**AI-powered literature ingestion, citation graph construction, and hypothesis generation for scientific discovery.**

## Responsibilities

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

## Architecture

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

## Quick Start

```bash
cd src/research-scout
uv pip install -e .
python -m research_scout.ingest.pubmed --query "KRAS G12C" --max-results 100
python -m research_scout.graph.build --input data/papers.jsonl
python -m research_scout.hypothesis.generate --graph data/citation_graph.parquet
```