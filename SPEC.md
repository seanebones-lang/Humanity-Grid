# Humanity Grid — Open Discovery Loop

**Codename:** OpenCure (internal) → Humanity Grid (public)

---

## Vision

A global, open-source scientific computing network that continuously turns unused computers into experiments aimed at important human problems.

Not: "Download this program and maybe it folds proteins."

Instead: **A continuously operating scientific discovery machine.**

---

## Mission Areas (Cause Selection)

Volunteers choose what their computer works on:

- 🧬 Cancer
- 🧠 Alzheimer's / neurological disease
- 🦠 Antibiotic resistance
- 🧫 Emerging infectious disease
- 🧬 Rare diseases
- 🌎 Climate modeling
- 🔋 Clean-energy / materials research

---

## The Open Discovery Loop

```
        SCIENTIFIC LITERATURE
                 ↓
        ┌───────────────────┐
        │   RESEARCH SCOUT  │
        │ AI + databases    │
        └─────────┬─────────┘
                  ↓
          Potential hypothesis
                  ↓
        ┌───────────────────┐
        │  HUMAN SCIENTIST  │
        │ reviews/approves  │
        └─────────┬─────────┘
                  ↓
          Computational study
                  ↓
       ┌─────────────────────┐
       │  HUMANITY GRID      │
       │                     │
       │  💻 💻 🖥️ 💻 🖥️   │
       │  thousands of PCs  │
       └─────────┬───────────┘
                 ↓
       promising candidates
                 ↓
       higher fidelity simulation
                 ↓
           ranked results
                 ↓
        OPEN RESEARCH REPORT
                 ↓
        experimental laboratory
                 ↓
               results
                 ↓
       feeds the system again
```

---

## First Mission: Cancer — Virtual Screening Pipeline

Cancer = hundreds of biologically different diseases. We attack smaller, answerable questions:

> **Find molecules likely to interfere with a particular cancer-driving protein.**

Pipeline:

```
10,000,000 compounds
        ↓
virtual screening (AutoDock)
        ↓
100,000 candidates
        ↓
better docking / consensus scoring
        ↓
5,000 candidates
        ↓
molecular dynamics (OpenMM)
        ↓
100 candidates
        ↓
literature / toxicity / known-drug analysis
        ↓
10-20 serious hypotheses
        ↓
REAL LABORATORY TESTING
```

**Key principle:** The computer doesn't discover "a cure." It discovers **candidates worthy of scarce laboratory time**.

---

## AI Research Orchestration (The Novelty)

Old volunteer computing: **Scientist → generates jobs → computers run jobs → scientist analyzes results.**

Humanity Grid: **AI + scientist → hypothesis → distributed experiment → AI analysis → next hypothesis → scientist approval → next experiment.**

### Research Scout Capabilities

- Constantly watch scientific literature (PubMed, bioRxiv, arXiv, patents)
- Monitor structured databases (ChEMBL, PubChem, PDB, UniProt, BindingDB)
- Detect signals:
  - New binding pocket discovered in protein X
  - Pathway Y critical in cancer subtype (multiple independent groups)
  - Compound Z failed original indication but has characteristics for new target
- Propose computational experiments with:
  - Hypothesis ID (e.g., H-9182)
  - Evidence: cited papers
  - Target protein
  - Proposed computation: screen library A against binding site B
  - Estimated compute: GPU-hours
  - Scientific reviewer: approved/pending
  - Launch experiment?

---

## Open Results — Radical Transparency

Every project gets a public page:

```
PROJECT H-9182
━━━━━━━━━━━━━━━━━━━━━━━━━━

Target: KRAS ...
Question: Can known compounds bind ...
Scientific rationale: [references]
Status: ████████████████░░ 82%
Volunteer computers: 14,822
Compute contributed: 2.81M GPU hours
Candidates tested: 42,839,201
Potential hits: 184
High-confidence candidates: 7
Data: Download
Code: GitHub
Results: Public
Paper: Pending
```

Volunteer dashboard:
> **Sean's MacBook Pro**
> 6,382 validated experiments
> 182 hours donated
> Contributed to 11 studies
> 4 studies published

**No cryptocurrency. No NFT. No bullshit token. Just: You helped science.**

---

## Trust & Security Architecture

### Job Execution Model

```
Signed Research Manifest
    ↓
approved research organization
    ↓
approved software image (Docker)
    ↓
sandbox
    ↓
NO arbitrary network access
NO user filesystem access
CPU/GPU/RAM limits
temperature limits
power limits
    ↓
signed result
```

### Result Validation (Byzantine Fault Tolerance)

- Duplicate important work units
- Computer A calculates X, Computer B independently calculates X
- If they disagree → send X to Computer C
- BOINC has used redundant computation/result validation for this class of problem

---

## Volunteer Application — Beautiful & Honest

```
What do you want your computer working on tonight?

Cancer Research        ● Selected
Alzheimer's Research   ○
Antibiotic Discovery   ○
Climate Modeling       ○
Clean Energy           ○

Use my computer:       While idle  ▼
Maximum CPU:           30%         ████████░░
Maximum GPU:           40%         ██████████░░
Run on battery:        No
Pause above:           75°C
Electricity preference: Only during my chosen hours  ▼
```

Then:
> **Tonight your computer screened 18,421 candidate molecules for a pediatric cancer study.**

---

## Architecture

```
Humanity Grid
├── Research Scout
│   ├── literature ingestion (PubMed, bioRxiv, arXiv, patents)
│   ├── citation graph
│   ├── hypothesis generator (LLM + structured reasoning)
│   └── human-review queue
│
├── Experiment Engine
│   ├── job definitions (YAML/JSON)
│   ├── datasets (compound libraries, protein structures)
│   ├── reproducibility (container hashes, env pins)
│   └── provenance (full lineage tracking)
│
├── Compute Broker
│   ├── BOINC adapter (primary)
│   ├── CPU workloads
│   ├── GPU workloads (CUDA, HIP, OpenCL, Metal)
│   └── result validation (redundancy, consensus)
│
├── Scientific Pipeline
│   ├── AutoDock (virtual screening)
│   ├── OpenMM (molecular dynamics — CPU, CUDA, HIP, OpenCL)
│   ├── future modules (AlphaFold, Rosetta, custom)
│
├── Open Results
│   ├── raw data (downloadable)
│   ├── analyses (notebooks, reports)
│   ├── citations (linked to literature)
│   └── reproducible notebooks (Jupyter/Quarto)
│
└── Volunteer App (cross-platform)
    ├── CPU/GPU controls (percentage, cores)
    ├── thermal limits (pause temp, resume temp)
    ├── cause selection (multi-cause allocation)
    ├── contributions dashboard
    └── project stories (human-readable impact)
```

---

## First Experiment: Boring but Rigorous

**Not:** "Cure pancreatic cancer."

**Instead:** Take a known protein-ligand system with experimentally established results and see whether our distributed pipeline can rediscover the expected candidates.

Proves: **scheduler → machines → calculation → verification → aggregation → scientific reproducibility.**

Then take it to a computational biology lab: **"The network exists. Give us a scientifically useful question."**

---

## Technology Choices

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Distributed compute | **BOINC** (via BOINC Central) | Mature, open source, handles heterogeneous CPUs/GPUs, scheduling, credits, retries, Docker workloads, AutoDock support |
| Virtual screening | **AutoDock Vina / AutoDock-GPU** | BOINC Central already supports it; proven in drug discovery |
| Molecular dynamics | **OpenMM** | Open source, CPU/CUDA/HIP/OpenCL/Metal, Python API, used in production science |
| AI/Research Scout | **Local LLMs + structured extraction** | Privacy, cost control, reproducible; can use Hermes Agent skills |
| Container runtime | **Docker / Podman** | BOINC Central supports Docker workloads |
| Volunteer app | **Tauri (Rust + Web UI)** | Small binary, native performance, web tech for beautiful UI, cross-platform |
| Data/results | **Parquet + SQLite + Git** | Analytical queries, reproducibility, version control |
| Web portal | **Next.js + React** | Existing NextEleven stack, Cloudflare Pages deployment |

---

## Non-Goals (v1)

- ❌ Generative "AI discovers cure" claims
- ❌ Cryptocurrency / tokens / NFTs
- ❌ Building our own distributed compute engine (use BOINC)
- ❌ Operating wet labs
- ❌ Clinical trials
- ❌ Medical advice

---

## Success Criteria (v1)

1. **Infrastructure works:** Research Scout ingests papers → proposes hypothesis → Human reviewer approves → Experiment Engine creates jobs → Compute Broker distributes via BOINC → Results return → Open Results publishes
2. **Reproducibility proven:** First experiment (known protein-ligand) rediscovers expected candidates with statistical significance
3. **Volunteer app runs:** Cross-platform, respects thermal/power limits, shows real contribution metrics
4. **Zero trust violations:** No sandbox escapes, no unauthorized network/filesystem access
5. **Public results:** All data, code, analyses downloadable and verifiable

---

## Milestones

| Milestone | Description | Target |
|-----------|-------------|--------|
| M0 | Repo initialized, SPEC.md, architecture docs | Week 1 |
| M1 | Research Scout: literature ingestion + citation graph | Week 2-3 |
| M2 | Research Scout: hypothesis generator + human review queue | Week 3-4 |
| M3 | Experiment Engine: job definitions, datasets, provenance | Week 4-5 |
| M4 | Compute Broker: BOINC adapter + result validation | Week 5-7 |
| M5 | Scientific Pipeline: AutoDock + OpenMM containers | Week 6-8 |
| M6 | Open Results: data portal + reproducible notebooks | Week 7-8 |
| M7 | Volunteer App: Tauri cross-platform MVP | Week 8-10 |
| M8 | Integration test: boring experiment end-to-end | Week 10-12 |
| M9 | Lab partnership: first real scientific question | Week 12+ |

---

## Team & Governance

- **Core maintainers:** Engineers building the infrastructure
- **Scientific Advisory Board:** Computational biologists, chemists, clinicians who review hypotheses
- **Open source:** MIT/Apache-2.0 license, community contributions welcome
- **No single point of failure:** Federation-ready architecture

---

## Funding Model

- Grants (NIH, NSF, Chan Zuckerberg, Gates Foundation, etc.)
- Institutional partnerships (universities, research institutes)
- Corporate sponsorship (compute credits, matching donations)
- Individual donations (volunteer-supported, Wikipedia-style)
- **Never:** Volunteer compute sold, data sold, tokens, premium features

---

## References

- [BOINC](https://boinc.berkeley.edu/) — Berkeley Open Infrastructure for Network Computing
- [BOINC Central](https://boinc.berkeley.edu/central/about.php) — Managed volunteer computing for scientists
- [AutoDock](http://autodock.scripps.edu/) — Molecular docking suite
- [OpenMM](http://openmm.org/) — Molecular dynamics simulation
- [World Community Grid](https://www.worldcommunitygrid.org/) — IBM's volunteer computing (Mapping Cancer Markers)
- [Folding@home](https://foldingathome.org/) — Protein folding simulation
- [ChEMBL](https://www.ebi.ac.uk/chembl/) — Bioactive molecule database
- [PubChem](https://pubchem.ncbi.nlm.nih.gov/) — Chemical information
- [PDB](https://www.rcsb.org/) — Protein Data Bank
- [BindingDB](https://www.bindingdb.org/) — Protein-ligand binding affinities