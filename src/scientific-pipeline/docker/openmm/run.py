#!/usr/bin/env python3
"""
OpenMM runner for BOINC work units - Molecular Dynamics simulations.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

import openmm as mm
import openmm.app as app
import openmm.unit as unit
from openmm.app import PDBFile, ForceField, Modeller, Simulation
from openmm import LangevinMiddleIntegrator, MonteCarloBarostat, Platform

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def setup_system(
    pdb_file: Path,
    ligand_sdf: Optional[Path],
    forcefield: str = "amber14-all.xml",
    water_model: str = "tip3p.xml",
    box_padding: float = 1.0 * unit.nanometer,
    ion_concentration: float = 0.15 * unit.molar,
) -> tuple[app.Topology, list[unit.Quantity], app.System]:
    """Set up the simulation system: protein + ligand + solvent + ions."""
    logger.info(f"Loading structure from {pdb_file}")
    pdb = PDBFile(str(pdb_file))

    # Load force field
    logger.info(f"Loading force field: {forcefield}, water: {water_model}")
    ff = ForceField(forcefield, water_model)

    # Create modeller for adding solvent
    modeller = Modeller(pdb.topology, pdb.positions)

    # Add ligand if provided
    if ligand_sdf and ligand_sdf.exists():
        logger.info(f"Adding ligand from {ligand_sdf}")
        from rdkit import Chem
        from rdkit.Chem import AllChem
        from openmm.app import PDBFile as OPDBFile

        # Convert SDF to PDB for OpenMM
        suppl = Chem.SDMolSupplier(str(ligand_sdf), removeHs=False)
        for mol in suppl:
            if mol:
                mol = Chem.AddHs(mol)
                AllChem.EmbedMolecule(mol, randomSeed=42)
                # Write temp PDB
                ligand_pdb = pdb_file.parent / "ligand_temp.pdb"
                with open(ligand_pdb, "w") as f:
                    f.write(Chem.MolToPDBBlock(mol))
                ligand_pdb_file = PDBFile(str(ligand_pdb))
                modeller.add(ligand_pdb_file.topology, ligand_pdb_file.positions)
                break

    # Add solvent
    logger.info(f"Adding solvent with padding {box_padding}")
    modeller.addSolvent(ff, model=water_model, padding=box_padding, ionicStrength=ion_concentration)

    # Create system
    logger.info("Creating OpenMM System")
    system = ff.createSystem(
        modeller.topology,
        nonbondedMethod=app.PME,
        nonbondedCutoff=1.0 * unit.nanometer,
        constraints=app.HBonds,
        rigidWater=True,
    )

    return modeller.topology, modeller.positions, system


def run_simulation(
    topology: app.Topology,
    positions: list[unit.Quantity],
    system: app.System,
    output_dir: Path,
    temperature: float = 300.0 * unit.kelvin,
    pressure: float = 1.0 * unit.atmosphere,
    timestep: float = 2.0 * unit.femtosecond,
    n_steps: int = 500000,  # 1 ns at 2 fs
    report_interval: int = 1000,
    platform_name: str = "CUDA",
    device_index: int = 0,
) -> dict:
    """Run MD simulation and write outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Integrator
    integrator = LangevinMiddleIntegrator(temperature, 1.0 / unit.picosecond, timestep)

    # Barostat for NPT
    system.addForce(MonteCarloBarostat(pressure, temperature, 25))

    # Platform
    platform = Platform.getPlatformByName(platform_name)
    properties = {"DeviceIndex": str(device_index), "Precision": "mixed"}

    # Simulation
    simulation = Simulation(topology, system, integrator, platform, properties)
    simulation.context.setPositions(positions)
    simulation.context.setVelocitiesToTemperature(temperature)

    # Minimize
    logger.info("Minimizing energy...")
    simulation.minimizeEnergy(maxIterations=500)

    # Reporters
    traj_file = output_dir / "trajectory.dcd"
    log_file = output_dir / "simulation.log"

    simulation.reporters.append(app.DCDReporter(str(traj_file), report_interval))
    simulation.reporters.append(app.StateDataReporter(
        str(log_file), report_interval,
        step=True, time=True, potentialEnergy=True, kineticEnergy=True,
        totalEnergy=True, temperature=True, volume=True, density=True,
        speed=True
    ))

    # Run
    logger.info(f"Running {n_steps} steps ({n_steps * timestep.value_in_unit(unit.picosecond)} ps)...")
    simulation.step(n_steps)

    # Save final structure
    final_pdb = output_dir / "final_structure.pdb"
    state = simulation.context.getState(getPositions=True)
    with open(final_pdb, "w") as f:
        PDBFile.writeFile(topology, state.getPositions(), f)

    logger.info("Simulation completed")

    return {
        "trajectory": str(traj_file),
        "log": str(log_file),
        "final_structure": str(final_pdb),
        "steps_completed": n_steps,
    }


def analyze_trajectory(traj_file: Path, top_file: Path, output_dir: Path) -> dict:
    """Basic trajectory analysis."""
    try:
        import mdtraj as md
        traj = md.load(str(traj_file), top=str(top_file))

        # RMSD relative to first frame
        rmsd = md.rmsd(traj, traj, 0)

        # Radius of gyration
        rg = md.compute_rg(traj)

        # Save analysis
        import numpy as np
        np.savez(output_dir / "analysis.npz", rmsd=rmsd, rg=rg)

        return {
            "rmsd_mean": float(rmsd.mean()),
            "rmsd_std": float(rmsd.std()),
            "rg_mean": float(rg.mean()),
            "rg_std": float(rg.std()),
        }
    except Exception as e:
        logger.warning(f"Analysis failed: {e}")
        return {}


def main():
    parser = argparse.ArgumentParser(description="OpenMM MD work unit runner")
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--work-unit-config", type=Path, required=True)
    args = parser.parse_args()

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
    ligand_file = input_dir / config["input_files"].get("ligand", "")
    ligand_file = ligand_file if ligand_file.exists() else None

    # Simulation parameters
    temperature = params.get("temperature", 300.0) * unit.kelvin
    pressure = params.get("pressure", 1.0) * unit.atmosphere
    timestep = params.get("timestep", 2.0) * unit.femtosecond
    n_steps = params.get("n_steps", 500000)
    platform_name = params.get("platform", "CUDA")

    # Setup and run
    topology, positions, system = setup_system(protein_file, ligand_file)
    results = run_simulation(
        topology, positions, system, output_dir,
        temperature, pressure, timestep, n_steps,
        platform_name=platform_name,
    )

    # Analyze
    analysis = analyze_trajectory(
        Path(results["trajectory"]),
        Path(results["final_structure"]),
        output_dir,
    )

    # Write metadata
    metadata = {
        "work_unit_id": work_unit_id,
        "job_id": job_id,
        "completed_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "results": results,
        "analysis": analysis,
    }
    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    logger.info(f"Work unit {work_unit_id} completed successfully")


if __name__ == "__main__":
    main()