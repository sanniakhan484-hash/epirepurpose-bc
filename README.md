# EpiRepurpose-BC

Multi-evidence, epigenetics-informed drug repurposing for breast cancer.

> **Status:** early development (Phase 0). Outputs are research hypotheses, not clinical advice.

## What it will do
1. Associate epigenetic state with drug sensitivity in breast cancer cell lines (DepMap/PRISM, GDSC, CTRP).
2. Map patient tumor profiles (TCGA-BRCA, METABRIC) to the most similar cell-line models.
3. Check signature reversal against LINCS L1000 and integrate everything into transparent, tiered evidence cards.

Full plan: [docs/PROJECT_PROPOSAL.md](docs/PROJECT_PROPOSAL.md)

## Quickstart
```bash
git clone <your-repo-url> && cd epirepurpose-bc
python -m venv .venv && source .venv/bin/activate
make install
make test
epirepurpose --help
```

## Data
Raw data are not stored in this repo. See [data/README.md](data/README.md).

## Results
_Add your key figure and a 3-line summary of findings here once Phase 2 is complete._

## Limitations
Associations in cell lines and public cohorts; not proof of clinical efficacy.

## License
MIT. See [LICENSE](LICENSE).
