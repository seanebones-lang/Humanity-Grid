#!/bin/bash
set -euo pipefail

# Entrypoint for OpenMM container
echo "=== OpenMM Container Starting ==="
echo "Work unit: $(cat /input/work_unit.json | jq -r '.work_unit_id')"
echo "Job: $(cat /input/work_unit.json | jq -r '.job_id')"

python3 /app/run.py \
  --input-dir /input \
  --output-dir /output \
  --work-unit-config /input/work_unit.json

EXIT_CODE=$?

echo "=== OpenMM Container Exiting (code: $EXIT_CODE) ==="
exit $EXIT_CODE