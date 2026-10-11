#!/usr/bin/env python3
"""
CLI to create JobSpec from template.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from experiment_engine.jobs.spec import (
    create_job_from_template,
)


def main():
    parser = argparse.ArgumentParser(description="Create JobSpec from template")
    parser.add_argument("--template", default="virtual_screening", help="Template name")
    parser.add_argument("--job-id", required=True, help="Job ID")
    parser.add_argument("--hypothesis-id", required=True, help="Hypothesis ID")
    parser.add_argument("--name", required=True, help="Experiment name")
    parser.add_argument("--overrides", type=json.loads, default="{}", help="JSON overrides")
    parser.add_argument("--output", type=Path, required=True, help="Output YAML file")
    args = parser.parse_args()

    # Extract provenance from overrides (required)
    provenance = args.overrides.get("provenance")
    if not provenance:
        print("ERROR: provenance required in overrides", file=sys.stderr)
        sys.exit(1)

    # Create job from template
    job = create_job_from_template(
        template_name=args.template,
        job_id=args.job_id,
        hypothesis_id=args.hypothesis_id,
        name=args.name,
        overrides=args.overrides,
    )

    # Write output
    job.to_yaml(args.output)
    print(f"Created {args.output}")
    print(f"JobSpec hash: {job.provenance.spec_hash}")


if __name__ == "__main__":
    main()
