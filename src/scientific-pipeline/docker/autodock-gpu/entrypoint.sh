#!/bin/bash
set -euo pipefail

# Entrypoint for AutoDock-GPU container
# Expects:
#   /input/work_unit.json - work unit configuration
#   /input/ - input files (read-only)
#   /output/ - output directory (writable)

echo "=== AutoDock-GPU Container Starting ==="
echo "Work unit: $(cat /input/work_unit.json | jq -r '.work_unit_id')"
echo "Job: $(cat /input/work_unit.json | jq -r '.job_id')"

# Run the Python orchestrator
python3 /app/run.py \
  --input-dir /input \
  --output-dir /output \
  --work-unit-config /input/work_unit.json

EXIT_CODE=$?

echo "=== AutoDock-GPU Container Exiting (code: $EXIT_CODE) ==="
exit $EXIT_CODE