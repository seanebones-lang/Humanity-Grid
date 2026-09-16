# Humanity Grid API Reference

## Base URL
```
https://api.humanity-grid.org/v1
```

## Authentication
All endpoints are public for read operations. Write operations require a signed Research Manifest (future).

## Endpoints

### Projects

#### List Projects
```
GET /projects
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | all | Filter: `active`, `completed`, `archived` |
| `cause` | string | all | Filter: `cancer`, `alzheimer`, `antibiotics`, `climate`, `energy`, `rare` |
| `limit` | integer | 20 | Max results (max 100) |
| `offset` | integer | 0 | Pagination offset |

**Response:**
```json
{
  "projects": [
    {
      "project_id": "H-9182",
      "title": "KRAS G12C Covalent Inhibitor Discovery",
      "description": "Virtual screening of 42M approved drug compounds...",
      "cause": "cancer",
      "status": "completed",
      "target": {
        "protein": "KRAS",
        "uniprot_id": "P01116",
        "mutation": "G12C",
        "pdb_ids": ["6O0M", "6O0N"]
      },
      "stats": {
        "volunteer_computers": 14822,
        "gpu_hours": 2810000,
        "work_units_completed": 42839201,
        "validated_results": 42100000
      },
      "results_summary": {
        "candidates_tested": 42839201,
        "potential_hits": 184,
        "high_confidence": 7
      },
      "created_at": "2026-09-16T14:30:00Z",
      "completed_at": "2026-09-20T10:15:00Z",
      "links": {
        "data": "/projects/H-9182/results",
        "notebooks": "/projects/H-9182/notebooks",
        "api": "/api/v1/projects/H-9182"
      }
    }
  ],
  "pagination": {
    "total": 42,
    "limit": 20,
    "offset": 0
  }
}
```

#### Get Project
```
GET /projects/{project_id}
```

**Response:** Full project metadata including hypothesis, experiments, results summary, data access links.

#### Get Project Results
```
GET /projects/{project_id}/results
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `experiment_type` | string | all | `virtual_screening`, `molecular_dynamics`, `consensus` |
| `format` | string | json | `json`, `parquet`, `csv` |
| `limit` | integer | 1000 | Max records |
| `offset` | integer | 0 | Pagination |

**Response:**
```json
{
  "results": [
    {
      "experiment_id": "EXP-H9182-VS-001",
      "work_unit_id": "EXP-H9182-VS-001-WU-0421",
      "compound_id": "CHEMBL123456",
      "affinity_kcal_mol": -10.2,
      "rmsd_lb": 1.2,
      "rmsd_ub": 2.1,
      "consensus_score": 0.94,
      "validated": true,
      "replicate_count": 2
    }
  ],
  "schema": {
    "compound_id": "string",
    "affinity_kcal_mol": "float",
    "rmsd_lb": "float",
    "rmsd_ub": "float",
    "consensus_score": "float",
    "validated": "boolean",
    "replicate_count": "integer"
  }
}
```

#### Get Project Notebooks
```
GET /projects/{project_id}/notebooks
```

**Response:** List of available analysis notebooks with download links.

### Datasets

#### List Datasets
```
GET /datasets
```

**Response:**
```json
{
  "datasets": [
    {
      "dataset_id": "chembl_approved_v32",
      "name": "ChEMBL Approved Drugs v32",
      "description": "2M compounds with approved drug status",
      "format": "sdf",
      "size_bytes": 128000000,
      "sha256": "abc123...",
      "source": "https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/",
      "version": "32",
      "updated_at": "2026-01-15T00:00:00Z"
    }
  ]
}
```

#### Get Dataset
```
GET /datasets/{dataset_id}
```

**Response:** Full dataset metadata including download URLs (direct, torrent, IPFS).

### Statistics

#### Global Stats
```
GET /stats
```

**Response:**
```json
{
  "global": {
    "total_volunteers": 14822,
    "active_volunteers_24h": 3241,
    "total_gpu_hours": 28100000,
    "total_cpu_hours": 156000000,
    "projects_completed": 12,
    "papers_published": 4,
    "work_units_validated": 124000000
  },
  "by_cause": {
    "cancer": { "gpu_hours": 12400000, "projects": 5 },
    "alzheimer": { "gpu_hours": 5600000, "projects": 2 },
    "antibiotics": { "gpu_hours": 4200000, "projects": 2 },
    "climate": { "gpu_hours": 2100000, "projects": 1 },
    "energy": { "gpu_hours": 1800000, "projects": 1 },
    "rare": { "gpu_hours": 2000000, "projects": 1 }
  },
  "top_contributors": [
    { "rank": 1, "name": "compute_maxi", "credits": 342156, "team": "NextEleven Research" },
    { "rank": 2, "name": "folding_legend", "credits: 298734, "team": "Stanford Folding" }
  ]
}
```

### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-09-16T15:30:00Z",
  "dependencies": {
    "database": "ok",
    "storage": "ok",
    "boinc_central": "ok"
  }
}
```

## Error Responses

All errors follow RFC 7807 Problem Details:

```json
{
  "type": "https://api.humanity-grid.org/errors/not-found",
  "title": "Project Not Found",
  "status": 404,
  "detail": "Project H-9999 does not exist",
  "instance": "/api/v1/projects/H-9999"
}
```

Common status codes:
- `200` - Success
- `400` - Bad Request (validation error)
- `404` - Not Found
- `429` - Rate Limited (60 req/min default)
- `500` - Internal Server Error
- `503` - Service Unavailable (dependency down)

## Rate Limiting
- Default: 60 requests/minute per IP
- Authenticated researchers: 300 requests/minute
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Data Formats

### Parquet Schema (Virtual Screening Results)
```python
{
  'compound_id': 'string',
  'affinity_kcal_mol': 'float32',
  'rmsd_lb': 'float32',
  'rmsd_ub': 'float32',
  'pose_coords': 'binary',  # optional, compressed
  'consensus_score': 'float32',
  'validated': 'bool',
  'replicate_count': 'int16',
  'work_unit_id': 'string',
  'job_id': 'string'
}
```

### JobSpec (Experiment Definition)
See `src/experiment-engine/src/experiment_engine/jobs/spec.py` for the canonical Pydantic model.

## Webhooks (Future)
Researchers can register webhooks for:
- `project.completed`
- `experiment.validated`
- `result.published`

## SDKs
- **Python**: `pip install humanity-grid-client` (planned)
- **R**: `devtools::install_github("humanity-grid/r-client")` (planned)
- **CLI**: `hg` command-line tool (planned)