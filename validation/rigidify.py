#!/usr/bin/env python3
"""Convert an openbabel-generated receptor PDBQT into a Vina rigid receptor
by stripping ROOT/BRANCH folding tags while keeping every ATOM/HETATM line
(with AutoDock atom type column). Vina's rigid receptor parser rejects
ROOT/ENDROOT/BRANCH/ENDBRANCH/TORSDOF."""
from __future__ import annotations

import sys
from pathlib import Path


def rigidify(src: Path, out: Path) -> int:
    keep: list[str] = []
    counts = {"ATOM": 0, "HETATM": 0}
    for line in src.read_text().splitlines():
        s = line.strip()
        if s.startswith(("ROOT", "ENDROOT", "BRANCH", "ENDBRANCH", "TORSDOF")):
            continue
        if s.startswith(("ATOM", "HETATM")):
            key = s[:6]
            counts[key] = counts.get(key, 0) + 1
        keep.append(line.rstrip())
    out.write_text("\n".join(keep) + "\n")
    return counts["ATOM"] + counts["HETATM"]


if __name__ == "__main__":
    n = rigidify(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"rigid receptor atoms kept: {n}")