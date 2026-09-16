"""
Experiment Engine - Core models and job specification.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import yaml
from yaml import safe_load as parse_yaml_raw


class ExperimentType(str, Enum):
    VIRTUAL_SCREENING = "virtual_screening"
    MOLECULAR_DYNAMICS = "molecular_dynamics"
    CONSENSUS_DOCKING = "consensus_docking"
    FREE_ENERGY = "free_energy"
    ADMET_PREDICTION = "admet_prediction"
    CUSTOM = "custom"


class SplitStrategy(str, Enum):
    SEQUENTIAL = "sequential"
    RANDOM = "random"
    STRATIFIED = "stratified"


class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    FAILED = "failed"
    OUTLIER = "outlier"
    RETRY = "retry"


class ComputeRequirements(BaseModel):
    """Compute resource requirements for a work unit."""
    engine: str
    gpu_required: bool = False
    gpu_memory_gb: int = 0
    cpus: int = 1
    memory_gb: int = 4
    estimated_runtime_hours: float = 1.0
    max_runtime_hours: float = 4.0


class WorkUnitSpec(BaseModel):
    """Work unit splitting specification."""
    total: int = Field(ge=1)
    compounds_per_unit: int = Field(ge=1)
    compound_library: str
    split_strategy: SplitStrategy = SplitStrategy.SEQUENTIAL


class InputSpec(BaseModel):
    """Input data specification with content addressing."""
    source: str
    sha256: str
    # Optional structured metadata
    binding_site: Optional[dict] = None
    format: Optional[str] = None


class ContainerSpec(BaseModel):
    """Container specification for reproducible execution."""
    image: str
    sha256: str
    entrypoint: str
    environment: list[str] = Field(default_factory=list)


class OutputSchemaField(BaseModel):
    name: str
    type: str  # string, float, int, binary, boolean


class OutputValidation(BaseModel):
    required_fields: list[str] = Field(default_factory=list)
    affinity_range: Optional[list[float]] = None


class OutputSpec(BaseModel):
    """Output specification."""
    name: str
    format: str  # parquet, csv, json, sdf, pdb
    schema_fields: list[OutputSchemaField] = Field(default_factory=list)
    validation: OutputValidation = Field(default_factory=OutputValidation)


class ValidationSpec(BaseModel):
    """Validation and quality control specification."""
    redundancy: int = Field(default=2, ge=1)
    consensus_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    outlier_detection: str = "iqr"  # iqr, zscore, isolation_forest
    failed_unit_retry: int = Field(default=3, ge=0)


class ProvenanceSpec(BaseModel):
    """Provenance and approval tracking."""
    hypothesis_id: str
    researcher_approval: str
    approval_timestamp: datetime
    git_commit: str
    spec_hash: Optional[str] = None


class JobSpec(BaseModel):
    """Complete job specification for a distributed experiment."""
    job_id: str
    hypothesis_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    experiment_type: ExperimentType
    name: str
    description: str = ""

    compute: ComputeRequirements
    work_units: WorkUnitSpec
    inputs: dict[str, InputSpec]
    container: ContainerSpec
    outputs: list[OutputSpec]
    validation: ValidationSpec = Field(default_factory=ValidationSpec)
    provenance: ProvenanceSpec

    @model_validator(mode="after")
    def compute_spec_hash(self) -> JobSpec:
        """Compute and store the spec hash for reproducibility."""
        # Create a deterministic representation excluding the spec_hash itself
        data = self.model_dump(exclude={"provenance": {"spec_hash"}})
        # Convert to canonical JSON
        canonical = json.dumps(data, sort_keys=True, default=str)
        self.provenance.spec_hash = hashlib.sha256(canonical.encode()).hexdigest()
        return self

    @field_validator("job_id")
    @classmethod
    def validate_job_id(cls, v: str) -> str:
        if not v or len(v) < 3:
            raise ValueError("job_id must be at least 3 characters")
        return v

    def to_yaml(self, path: Optional[Path] = None) -> str:
        """Serialize to YAML."""
        yaml_str = yaml.dump(self.model_dump(mode="json"), sort_keys=False, default_flow_style=False)
        if path:
            path.write_text(yaml_str)
        return yaml_str

    @classmethod
    def from_yaml(cls, path: Path) -> JobSpec:
        """Load from YAML file."""
        data = parse_yaml_raw(path.read_text())
        return cls.model_validate(data)

    def to_json(self, path: Optional[Path] = None) -> str:
        """Serialize to JSON."""
        json_str = self.model_dump_json(indent=2)
        if path:
            path.write_text(json_str)
        return json_str

    @classmethod
    def from_json(cls, path: Path) -> JobSpec:
        """Load from JSON file."""
        return cls.model_validate_json(path.read_text())


class WorkUnit(BaseModel):
    """A single unit of work within a job."""
    work_unit_id: str
    job_id: str
    index: int
    compound_range: tuple[int, int]  # start, end (inclusive)
    input_hashes: dict[str, str]
    status: ValidationStatus = ValidationStatus.PENDING
    assigned_node: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class JobResult(BaseModel):
    """Result from a completed work unit."""
    work_unit_id: str
    job_id: str
    node_id: str
    container_hash: str
    input_hashes: dict[str, str]
    output_hash: str
    output_path: str
    metrics: dict[str, float] = Field(default_factory=dict)
    validation_status: ValidationStatus = ValidationStatus.PENDING
    consensus_score: Optional[float] = None
    replicate_id: Optional[str] = None
    started_at: datetime
    completed_at: datetime
    cpu_time_sec: float
    gpu_time_sec: Optional[float] = None
    error: Optional[str] = None


# Template definitions for common experiment types
VIRTUAL_SCREENING_TEMPLATE = {
    "experiment_type": "virtual_screening",
    "compute": {
        "engine": "autodock-gpu",
        "gpu_required": True,
        "gpu_memory_gb": 8,
        "cpus": 4,
        "memory_gb": 16,
        "estimated_runtime_hours": 0.5,
        "max_runtime_hours": 2.0,
    },
    "work_units": {
        "total": 1000,
        "compounds_per_unit": 1000,
        "compound_library": "chembl_approved",
        "split_strategy": "sequential",
    },
    "inputs": {
        "protein_structure": {
            "source": "pdb:XXXX",
            "sha256": "TODO",
            "binding_site": {"center": [0, 0, 0], "radius": 15.0},
        },
        "compound_library": {
            "source": "chembl:v32:approved",
            "sha256": "TODO",
            "format": "sdf",
        },
        "docking_parameters": {
            "source": "inline",
            "sha256": "TODO",
            "exhaustiveness": 16,
            "num_modes": 10,
            "energy_range": 3.0,
        },
    },
    "container": {
        "image": "ghcr.io/humanity-grid/autodock-gpu:1.2.0",
        "sha256": "TODO",
        "entrypoint": "/app/run_docking.sh",
        "environment": ["OMP_NUM_THREADS=4", "CUDA_VISIBLE_DEVICES=0"],
    },
    "outputs": [
        {
            "name": "docking_results",
            "format": "parquet",
            "schema_fields": [
                {"name": "compound_id", "type": "string"},
                {"name": "affinity_kcal_mol", "type": "float"},
                {"name": "rmsd_lb", "type": "float"},
                {"name": "rmsd_ub", "type": "float"},
                {"name": "pose_coords", "type": "binary"},
            ],
            "validation": {
                "required_fields": ["compound_id", "affinity_kcal_mol"],
                "affinity_range": [-20, 10],
            },
        }
    ],
    "validation": {
        "redundancy": 2,
        "consensus_threshold": 0.8,
        "outlier_detection": "iqr",
        "failed_unit_retry": 3,
    },
}


def create_job_from_template(
    template_name: str,
    job_id: str,
    hypothesis_id: str,
    name: str,
    overrides: dict[str, Any],
) -> JobSpec:
    """Create a JobSpec from a template with overrides."""
    templates = {
        "virtual_screening": VIRTUAL_SCREENING_TEMPLATE,
    }

    if template_name not in templates:
        raise ValueError(f"Unknown template: {template_name}")

    import copy
    template = copy.deepcopy(templates[template_name])

    # Apply overrides
    def deep_update(base: dict, updates: dict) -> dict:
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                deep_update(base[key], value)
            else:
                base[key] = value
        return base

    template = deep_update(template, overrides)

    # Add required fields
    template["job_id"] = job_id
    template["hypothesis_id"] = hypothesis_id
    template["name"] = name

    # Provenance needs to be provided
    if "provenance" not in template:
        raise ValueError("provenance must be provided in overrides")

    return JobSpec.model_validate(template)