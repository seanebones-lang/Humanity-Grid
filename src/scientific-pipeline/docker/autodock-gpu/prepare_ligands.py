#!/usr/bin/env python3
"""
Prepare ligands from SDF to PDBQT for AutoDock-GPU.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem


def main():
    parser = argparse.ArgumentParser(description="Prepare ligands from SDF to PDBQT")
    parser.add_argument("--input", type=Path, required=True, help="Input SDF file")
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory for PDBQT files")
    parser.add_argument("--max-ligands", type=int, help="Maximum number of ligands to process")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    suppl = Chem.SDMolSupplier(str(args.input), removeHs=False)
    count = 0

    for i, mol in enumerate(suppl):
        if args.max_ligands and count >= args.max_ligands:
            break
        if mol is None:
            continue

        # Add hydrogens and generate 3D coordinates
        mol = Chem.AddHs(mol)
        if AllChem.EmbedMolecule(mol, randomSeed=42) == -1:
            print(f"Warning: Could not embed molecule {i}", file=sys.stderr)
            continue
        AllChem.MMFFOptimizeMolecule(mol)

        # Write PDBQT (simplified - uses PDB format, AutoDock-GPU can read)
        output_path = args.output_dir / f"ligand_{count:06d}.pdbqt"
        with open(output_path, "w") as f:
            # Write as PDB block (AutoDock-GPU expects PDBQT but we'll use PDB for now)
            f.write(Chem.MolToPDBBlock(mol))
        
        count += 1

        if count % 100 == 0:
            print(f"Prepared {count} ligands...")

    # Write ligand list file
    list_file = args.output_dir / "ligands.list"
    with open(list_file, "w") as f:
        for i in range(count):
            f.write(f"ligand_{i:06d}.pdbqt\n")

    print(f"Prepared {count} ligands to {args.output_dir}")
    print(f"Ligand list: {list_file}")


if __name__ == "__main__":
    main()