# Open Results

**Public data portal, reproducible analyses, and open science publishing for Humanity Grid.**

## Responsibilities

- Host all experimental data, results, and analyses publicly
- Provide reproducible computational notebooks (Jupyter/Quarto)
- Link results to scientific literature and hypotheses
- Enable download of raw data, processed results, and metadata
- Support citation and attribution

## Data Portal Structure

```
open-results/
├── projects/
│   ├── H-9182/
│   │   ├── metadata.json          # Project metadata
│   │   ├── hypothesis.json        # Original hypothesis
│   │   ├── job-spec.yaml          # Experiment specification
│   │   ├── results/
│   │   │   ├── virtual_screening/
│   │   │   │   ├── EXP-H9182-VS-001_results.parquet
│   │   │   │   ├── EXP-H9182-VS-001_analysis.ipynb
│   │   │   │   └── EXP-H9182-VS-001_report.html
│   │   │   ├── molecular_dynamics/
│   │   │   │   ├── EXP-H9182-MD-001_trajectory.dcd
│   │   │   │   ├── EXP-H9182-MD-001_analysis.ipynb
│   │   │   │   └── EXP-H9182-MD-001_report.html
│   │   │   └── consensus/
│   │   │       ├── top_candidates.parquet
│   │   │       └── consensus_report.html
│   │   ├── papers/
│   │   │   └── manuscript.pdf
│   │   └── citations.bib
│   └── ...
├── datasets/
│   ├── chembl_approved_v32/
│   │   ├── metadata.json
│   │   ├── compounds.parquet
│   │   └── sha256.txt
│   └── ...
├── api/
│   ├── projects.yaml              # OpenAPI spec
│   └── datasets.yaml
└── web/
    └── (Next.js frontend)
```

## Project Metadata Schema

```json
{
  "project_id": "H-9182",
  "title": "KRAS G12C Covalent Inhibitor Discovery",
  "description": "Virtual screening of approved drugs against KRAS G12C pocket",
  "target": {
    "protein": "KRAS",
    "uniprot_id": "P01116",
    "mutation": "G12C",
    "pdb_ids": ["6O0M", "6O0N"]
  },
  "hypothesis": {
    "hypothesis_id": "H-9182",
    "question": "Can known covalent inhibitors bind the G12C pocket with improved selectivity?",
    "rationale": ["PMID:36543210", "PMID:37123456", "PMID:35987654"]
  },
  "status": "completed",
  "created_at": "2026-09-16T14:30:00Z",
  "completed_at": "2026-09-20T10:15:00Z",
  "compute_stats": {
    "volunteer_computers": 14822,
    "gpu_hours": 2810000,
    "work_units_completed": 42839201,
    "validated_results": 42100000
  },
  "results_summary": {
    "candidates_tested": 42839201,
    "potential_hits": 184,
    "high_confidence": 7,
    "top_candidates": [
      {"compound_id": "CHEMBL123", "affinity": -10.2, "known_drug": "Drug X"},
      {"compound_id": "CHEMBL456", "affinity": -9.8, "known_drug": "Drug Y"}
    ]
  },
  "experiments": [
    {"job_id": "EXP-H9182-VS-001", "type": "virtual_screening", "status": "completed"},
    {"job_id": "EXP-H9182-MD-001", "type": "molecular_dynamics", "status": "completed"}
  ],
  "data_access": {
    "raw_results": "https://data.humanity-grid.org/projects/H-9182/results/",
    "processed": "https://data.humanity-grid.org/projects/H-9182/processed/",
    "notebooks": "https://notebooks.humanity-grid.org/H-9182/"
  },
  "license": "CC0-1.0",
  "citation": "Humanity Grid Consortium. (2026). KRAS G12C Covalent Inhibitor Discovery. Humanity Grid Project H-9182. https://doi.org/10.xxxx/hg.H-9182"
}
```

## Reproducible Notebooks

Each experiment gets a Quarto/Jupyter notebook that:
- Loads raw results from the data portal
- Performs analysis (ranking, clustering, visualization)
- Generates publication-ready figures
- Is version-controlled and executable

Example notebook structure:
```markdown
# Analysis: EXP-H9182-VS-001

## 1. Load Data
```python
results = pd.read_parquet("s3://humanity-grid/projects/H-9182/results/EXP-H9182-VS-001_results.parquet")
```

## 2. Quality Control
- Check replicate consensus
- Remove outliers
- Validate schema

## 3. Ranking & Filtering
- Rank by binding affinity
- Filter by drug-likeness (Lipinski)
- Cross-reference with known drugs

## 4. Visualization
- Affinity distribution
- Chemical space (t-SNE/UMAP)
- Binding pose inspection

## 5. Top Candidates Table
| Rank | Compound | Affinity | Drug | MOA |
|------|----------|----------|------|-----|
| 1 | CHEMBL123 | -10.2 | Drug X | EGFR inhibitor |
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/projects` | List all projects |
| `GET /api/v1/projects/{id}` | Project metadata |
| `GET /api/v1/projects/{id}/results` | List result files |
| `GET /api/v1/projects/{id}/results/{file}` | Download result file |
| `GET /api/v1/projects/{id}/notebooks` | List notebooks |
| `GET /api/v1/datasets` | List datasets |
| `GET /api/v1/datasets/{id}` | Dataset metadata |
| `GET /api/v1/stats` | Global compute statistics |

## Architecture

```
open-results/
├── pyproject.toml
├── src/
│   └── open_results/
│       ├── __init__.py
│       ├── portal/
│       │   ├── models.py          # Data models
│       │   ├── storage.py         # S3/MinIO/GCS abstraction
│       │   ├── api.py             # FastAPI endpoints
│       │   └── web.py             # Next.js frontend (separate repo)
│       ├── notebooks/
│       │   ├── generator.py       # Auto-generate analysis notebooks
│       │   ├── templates/         # Quarto templates
│       │   └── runner.py          # Execute notebooks headless
│       ├── publishing/
│       │   ├── doi.py             # DataCite DOI minting
│       │   ├── citation.py        # Citation generation
│       │   └── export.py          # Export packages (ZIP, BagIt)
│       └── config.py
├── tests/
├── scripts/
│   ├── publish_project.py
│   ├── generate_notebook.py
│   └── sync_to_portal.py
└── quarto/
    └── templates/
        ├── virtual_screening.qmd
        ├── molecular_dynamics.qmd
        └── consensus_report.qmd
```

## Quick Start

```bash
cd src/open-results
uv pip install -e .

# Publish a completed project
python -m open_results.publishing.publish_project \
  --project-id H-9182 \
  --results-dir /path/to/results \
  --output s3://humanity-grid/projects/H-9182/

# Generate analysis notebook
python -m open_results.notebooks.generator \
  --job-id EXP-H9182-VS-001 \
  --template virtual_screening \
  --output notebooks/H-9182/

# Run notebook headless
python -m open_results.notebooks.runner \
  notebooks/H-9182/EXP-H9182-VS-001_analysis.qmd

# Start API server
python -m open_results.portal.api
```