#!/usr/bin/env python3
"""
CLI to split JobSpec into work unit configs.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from experiment_engine.jobs.spec import JobSpec, WorkUnit


def main():
    parser = argparse.ArgumentParser(description="Split JobSpec into work unit configs")
    parser.add_argument("job_spec", type=Path, help="JobSpec YAML file")
    parser.add_argument("--output", type=Path, default=Path("work_units"), help="Output directory")
    parser.add_argument("--library-path", type=Path, help="Path to compound library file")
    args = parser.parse_args()

    # Load job spec
    job = JobSpec.from_yaml(args.job_spec)

    # Calculate work unit splits
    total_compounds = job.work_units.total * job.work_units.compounds_per_unit
    # Last unit may have fewer compounds
    n_units = job.work_units.total

    args.output.mkdir(parents=True, exist_ok=True)

    # Get input file names from job spec
    protein_input = job.inputs.get("protein_structure")
    library_input = job.inputs.get("compound_library")
    config_input = job.inputs.get("docking_parameters")

    protein_file = protein_input.source if protein_input else "protein.pdbqt"
    library_file = library_input.source if library_input else "library.sdf"
    config_file = config_input.source if config_input else "config.txt"

    # Default docking parameters
    default_params = {"exhaustiveness": 16, "num_modes": 10, "energy_range": 3.0}
    docking_params = default_params.copy()
    if config_input and config_input.format == "json":
        # If params are embedded in the input, they'd be parsed separately
        pass

    for i in range(n_units):
        start = i * job.work_units.compounds_per_unit
        end = min(start + job.work_units.compounds_per_unit, total_compounds)

        # Create work unit config
        wu_config = {
            "work_unit_id": f"{job.job_id}-WU-{i:04d}",
            "job_id": job.job_id,
            "index": i,
            "compound_range": [start, end - 1],
            "parameters": docking_params,
            "input_files": {
                "protein": protein_file,
                "compounds": library_file,
                "config": config_file,
            },
            "output_files": {
                "results": f"results_{i:04d}.parquet",
                "poses": f"poses_{i:04d}.pdbqt",
                "metadata": f"metadata_{i:04d}.json",
            },
            "binding_site": protein_input.binding_site if protein_input and protein_input.binding_site else {},
        }

        output_file = args.output / f"wu_{i:04d}.json"
        with open(output_file, "w") as f:
            json.dump(wu_config, f, indent=2)

    print(f"Created {n_units} work unit configs in {args.output}")


if __name__ == "__main__":
    main()