#!/usr/bin/env python3
"""
AutoDock-GPU runner for BOINC work units.
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

import polars as pl
from rdkit import Chem
from rdkit.Chem import AllChem

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def prepare_receptor(pdb_file: Path, output_pdbqt: Path, center: list[float], radius: float) -> None:
    """Prepare receptor PDB to PDBQT using MGLTools-style preparation."""
    # Simplified receptor preparation using AutoDock tools
    # In production, use prepare_receptor4.py from MGLTools
    cmd = [
        "autodock_gpu",
        "--receptor", str(pdb_file),
        "--receptor-out", str(output_pdbqt),
        "--center", f"{center[0]},{center[1]},{center[2]}",
        "--size", f"{radius*2},{radius*2},{radius*2}",
    ]
    logger.info(f"Preparing receptor: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Receptor preparation failed: {result.stderr}")
        raise RuntimeError(f"Receptor preparation failed: {result.stderr}")


def prepare_ligands(sdf_file: Path, output_dir: Path) -> list[Path]:
    """Convert SDF compounds to PDBQT files for AutoDock."""
    output_dir.mkdir(parents=True, exist_ok=True)
    pdbqt_files = []

    suppl = Chem.SDMolSupplier(str(sdf_file), removeHs=False)
    for i, mol in enumerate(suppl):
        if mol is None:
            continue
        # Add hydrogens and generate 3D coords
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)

        # Write PDBQT (simplified - in production use prepare_ligand4.py)
        pdbqt_path = output_dir / f"ligand_{i:06d}.pdbqt"
        # For now, write as SDF and let AutoDock handle it
        # Real implementation would use MGLTools prepare_ligand4.py
        with open(pdbqt_path, "w") as f:
            f.write(Chem.MolToMolBlock(mol))
        pdbqt_files.append(pdbqt_path)

    logger.info(f"Prepared {len(pdbqt_files)} ligands")
    return pdbqt_files


def run_autodock_gpu(
    receptor_pdbqt: Path,
    ligand_dir: Path,
    output_dir: Path,
    exhaustiveness: int = 16,
    num_modes: int = 10,
    energy_range: float = 3.0,
) -> Path:
    """Run AutoDock-GPU on a batch of ligands."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # AutoDock-GPU expects a file list
    ligand_list = output_dir / "ligands.list"
    with open(ligand_list, "w") as f:
        for lig in sorted(ligand_dir.glob("*.pdbqt")):
            f.write(f"{lig}\n")

    output_file = output_dir / "results.csv"

    cmd = [
        "autodock_gpu",
        "--receptor", str(receptor_pdbqt),
        "--ligand-list", str(ligand_list),
        "--output", str(output_file),
        "--exhaustiveness", str(exhaustiveness),
        "--num-modes", str(num_modes),
        "--energy-range", str(energy_range),
    ]

    logger.info(f"Running AutoDock-GPU: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        logger.error(f"AutoDock-GPU failed: {result.stderr}")
        raise RuntimeError(f"AutoDock-GPU failed: {result.stderr}")

    return output_file


def parse_results(csv_file: Path, output_parquet: Path) -> None:
    """Parse AutoDock-GPU CSV output to Parquet."""
    df = pl.read_csv(csv_file)
    # Expected columns: ligand, affinity, rmsd_lb, rmsd_ub, ...
    df.write_parquet(output_parquet)
    logger.info(f"Wrote {len(df)} results to {output_parquet}")


def main():
    parser = argparse.ArgumentParser(description="AutoDock-GPU work unit runner")
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--work-unit-config", type=Path, required=True)
    args = parser.parse_args()

    # Load work unit config
    with open(args.work_unit_config) as f:
        config = json.load(f)

    work_unit_id = config["work_unit_id"]
    job_id = config["job_id"]
    params = config.get("parameters", {})

    logger.info(f"Starting work unit {work_unit_id} for job {job_id}")

    input_dir = args.input_dir
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Input files
    protein_file = input_dir / config["input_files"]["protein"]
    compounds_file = input_dir / config["input_files"]["compounds"]
    # config_file = input_dir / config["input_files"]["config"]  # Optional

    # Binding site from config or defaults
    binding_site = config.get("binding_site", {"center": [0, 0, 0], "radius": 15.0})

    # Prepare receptor
    receptor_pdbqt = output_dir / "receptor.pdbqt"
    prepare_receptor(protein_file, receptor_pdbqt, binding_site["center"], binding_site["radius"])

    # Prepare ligands
    ligand_dir = output_dir / "ligands"
    prepare_ligands(compounds_file, ligand_dir)

    # Run docking
    exhaustiveness = params.get("exhaustiveness", 16)
    num_modes = params.get("num_modes", 10)
    energy_range = params.get("energy_range", 3.0)

    results_csv = run_autodock_gpu(
        receptor_pdbqt,
        ligand_dir,
        output_dir,
        exhaustiveness,
        num_modes,
        energy_range,
    )

    # Convert to Parquet
    results_parquet = output_dir / config["output_files"]["results"]
    parse_results(results_csv, results_parquet)

    # Write metadata
    metadata = {
        "work_unit_id": work_unit_id,
        "job_id": job_id,
        "completed_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "num_compounds": len(list(ligand_dir.glob("*.pdbqt"))),
        "output_file": str(results_parquet),
    }
    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Work unit {work_unit_id} completed successfully")


if __name__ == "__main__":
    main()