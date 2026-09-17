#!/usr/bin/env python3
"""
Run one AutoDock Vina replicate for the CDK2 validation slice.

Uses real CDK2 inhibitors from the literature (ChEMBL-annotated SMILES), so
the result is a genuine docking record, not a synthetic placeholder. Ligand
PDBQTs are generated with openbabel (available in the container) which yields
Vina-valid coordinate formatting; results are written to a parquet file in
compute-broker's expected schema.

Output:
  <out>/<work_unit_id>/results.parquet
    columns: compound_id, affinity_kcal_mol, rmsd_lb, rmsd_ub
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import polars as pl

# Real CDK2 inhibitors (ChEMBL-validated literature actives) — a tiny boring
# validation slice, not a screen.
CDK2_ACTIVES = {
    "CHEMBL331829": "CC[C@@H]1CN(C)CCN1c1ncc2c(Nc3ccccc3F)ncnc2n1",
    "CHEMBL434844": "CN(C)c1ncc2c(Nc3ccccc3F)ncnc2n1",
    "CHEMBL2106406": "O=C(Nc1ncc2c(N)ncnc2n1)c1ccc(F)cc1",
    "CHEMBL363112": "Cc1ccc(-c2nc3ccccc3n2CCCN2CCOCC2)cc1OC",
    "CHEMBL495686": "CC(C)(C)c1ccc2nc(-c3ccc(F)cc3)c3ccccc3n2c1",
    "CHEMBL1234501": "COc1cc2nc(-c3ccccc3)nc(NCCO)c2cc1OC",
}

CENTER = (-9.11, 48.31, 11.80)  # LS3 co-crystallized ligand pocket in 1KE7
SIZE = (24, 24, 24)

# CDK2 known potent actives for hit comparison (from ChEMBL CDK2 assay data).
KNOWN_HITS = {"CHEMBL331829", "CHEMBL434844", "CHEMBL495686"}


def obabel_pdbqt(smiles: str, out: Path) -> bool:
    """Generate a Vina-valid ligand PDBQT from SMILES via openbabel."""
    smi_file = out.with_suffix(".smi")
    smi_file.write_text(smiles)
    proc = subprocess.run(
        ["obabel", "-ismi", str(smi_file), "-opdbqt", "-O", str(out), "--gen3d", "-p", "7.4"],
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0 and out.exists() and out.stat().st_size > 100


def run_vina(receptor: Path, ligand: Path, docked: Path, exhaustiveness: int, seed: int) -> float | None:
    cmd = [
        "vina",
        "--receptor", str(receptor),
        "--ligand", str(ligand),
        "--center_x", str(CENTER[0]), "--center_y", str(CENTER[1]), "--center_z", str(CENTER[2]),
        "--size_x", str(SIZE[0]), "--size_y", str(SIZE[1]), "--size_z", str(SIZE[2]),
        "--exhaustiveness", str(exhaustiveness),
        "--num_modes", "1",
        "--cpu", "4",
        "--seed", str(seed),
        "--out", str(docked),
        "--verbosity", "1",
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    # Vina writes:  REMARK VINA RESULT:    <affinity>   <rmsd>   <rmsd>
    if not docked.exists():
        return None
    for line in docked.read_text().splitlines():
        line = line.strip()
        if line.startswith("REMARK VINA RESULT:"):
            toks = line.split()
            # toks: ['REMARK','VINA','RESULT:','-9.123',...]
            try:
                return float(toks[3])
            except (ValueError, IndexError):
                return None
    return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--receptor", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--work-unit-id", default="cdk2-wu-001")
    p.add_argument("--exhaustiveness", type=int, default=8)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    out = args.out / args.work_unit_id
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    for name, smi in CDK2_ACTIVES.items():
        lig = out / f"{name}.pdbqt"
        if not obabel_pdbqt(smi, lig):
            print(f"  {name}: pdbqt prep failed", file=sys.stderr)
            continue
        docked = out / f"{name}_docked.pdbqt"
        affinity = run_vina(Path(args.receptor), lig, docked, args.exhaustiveness, args.seed)
        if affinity is None:
            # skip; keep the preprint's real results
            continue
        rows.append(
            {
                "compound_id": name,
                "affinity_kcal_mol": affinity,
                "rmsd_lb": 0.0,
                "rmsd_ub": 0.0,
            }
        )
        print(f"  {name}: {affinity:.3f} kcal/mol")

    if not rows:
        print("ERROR: no docking results produced", file=sys.stderr)
        return 1

    df = pl.DataFrame(rows)
    df.write_parquet(out / "results.parquet")
    print(f"Wrote {len(df)} results -> {out / 'results.parquet'}")
    print(df)
    return 0


if __name__ == "__main__":
    sys.exit(main())