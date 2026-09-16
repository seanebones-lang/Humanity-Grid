#!/usr/bin/env python3
"""
Prepare receptor PDB to PDBQT for AutoDock-GPU.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Prepare receptor for AutoDock-GPU")
    parser.add_argument("--input", type=Path, required=True, help="Input PDB file")
    parser.add_argument("--output", type=Path, required=True, help="Output PDBQT file")
    parser.add_argument("--center", type=float, nargs=3, required=True, help="Binding site center x y z")
    parser.add_argument("--radius", type=float, required=True, help="Binding site radius")
    parser.add_argument("--size", type=float, nargs=3, help="Box size x y z (default: 2*radius)")
    args = parser.parse_args()

    size = args.size if args.size else [args.radius * 2, args.radius * 2, args.radius * 2]

    # Use AutoDock-GPU's built-in receptor preparation
    cmd = [
        "autodock_gpu",
        "--receptor", str(args.input),
        "--receptor-out", str(args.output),
        "--center", f"{args.center[0]},{args.center[1]},{args.center[2]}",
        "--size", f"{size[0]},{size[1]},{size[2]}",
    ]

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)
    
    print(f"Receptor prepared: {args.output}")


if __name__ == "__main__":
    main()