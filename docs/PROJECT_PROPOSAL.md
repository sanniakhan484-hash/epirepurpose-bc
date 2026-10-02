# EpiRepurpose-BC (working title)
## A multi-evidence framework for epigenetics-informed drug repurposing in breast cancer

**Status:** Proposal v1.0 | **Author:** [Your name] | **Last updated:** [date]

> This document is a living proposal. Items marked **[VERIFY]** depend on data release versions, URLs, or citations that must be checked against the source before they are relied upon.

---

## 1. Summary

Breast cancer is a molecularly heterogeneous disease in which epigenetic dysregulation, particularly promoter DNA hypermethylation that silences tumor suppressor and DNA-repair genes, contributes to tumor behavior and treatment response. Drug repurposing (finding new uses for existing approved or clinical-stage drugs) is an attractive route to new options, but most computational repurposing studies rely on a single evidence type, which makes their candidate lists fragile.

This project builds **an open, reproducible tool that prioritizes existing drugs for breast cancer by integrating three independent lines of evidence anchored in epigenetic state**:

1. **Pharmacogenomic association** in cell lines (does epigenetic state predict drug sensitivity?)
2. **Tumor-to-model transfer** (can patient tumor methylation profiles be mapped to the cell-line models that resemble them, carrying drug response across?)
3. **Signature reversal** (does a drug shift gene expression in the opposite direction from a methylation-associated tumor signature?)

Each candidate is annotated with target dependency data and its clinical status, and its evidence is summarized in a transparent, uncertainty-aware score. The final product is a Python package, a command-line interface, a hosted web app, and a written report.

**Scope principle:** the project is staged into a *minimum viable core* (Aims 1 and 2, which alone form a complete study) and *extensions* (Aims 3 and 4). The core must stand on its own if time runs short.

---

## 2. Background and motivation

- **Epigenetic silencing in breast cancer.** Promoter hypermethylation can silence genes without altering their sequence. *BRCA1* is a well-known example: promoter methylation is reported in a subset of breast tumors, enriched in triple-negative disease **[VERIFY frequencies and citations]**. Silencing of DNA-repair genes can create therapeutic vulnerabilities (for example sensitivity to PARP inhibitors or platinum agents), while epigenetic drugs (DNMT and HDAC inhibitors, among others) act on the machinery itself.
- **Why repurposing.** Existing drugs have known safety profiles, which shortens the path from hypothesis to testing. Large public screens now measure the response of hundreds to thousands of drugs across hundreds of cancer cell lines.
- **The gap.** Epigenetic state is rarely used as the *organizing variable* for repurposing, and tumor-derived epigenetic signals are rarely linked rigorously to the cell-line models in which drug response is actually measured. Single-evidence pipelines are also typically not benchmarked against simple baselines or controls.

### 2.1 Lessons from the prototype

A 2024 course prototype explored this idea using BRCA1 CpG sites from TCGA and six hand-picked epigenetic drugs. A retrospective review identified problems that this project is explicitly designed to avoid:

| Prototype problem | Design response in this project |
|---|---|
| Tumor methylation (TCGA) and drug response (cell lines) never linked | Methylation and drug response taken from the **same cell lines**; separate, validated tumor-to-model mapping |
| Samples selected by the predictor (high methylation) before correlating | No selection on predictors; defined inclusion criteria stated in advance |
| Arbitrary thresholds, forced to 10 CpGs | Annotation-driven probe selection (promoter-region probes) and pre-specified, justified parameters |
| Pearson on beta values, no p-values or multiple testing | M-values or rank-based statistics, effect sizes, FDR control, permutation checks |
| Six hand-picked drugs (cannot discover anything) | Full drug-library screen |
| Mean AUC per drug with unequal cell-line sets | Per-drug n reported, models with covariates, lineage-aware design |
| CpG choice had no effect on drug ranking | Drug ranking depends explicitly on epigenetic state by construction |
| Manual Excel intermediates, Colab paths | Scripted, versioned, cached data pipeline |

---

## 3. Research questions and hypotheses

**RQ1.** Is epigenetic state in breast cancer cell lines associated with differential drug sensitivity, after accounting for subtype and lineage?
**H1.** Specific drug classes show methylation-state-dependent sensitivity that survives adjustment for subtype and multiple testing.

**RQ2.** Do methylation features carry predictive information about drug response beyond expression and subtype?
**H2.** A model with methylation features outperforms expression-only and subtype-only baselines in grouped cross-validation. *A null result is an acceptable, reportable outcome.*

**RQ3.** Can tumor methylation profiles be mapped to cell-line models well enough to transfer drug-response evidence?
**H3.** Mapped cell lines recover tumor subtype and methylation state above chance, using held-out labels not used in the mapping.

**RQ4.** Does combining independent evidence types produce more reliable candidates than any single type?
**H4.** Candidates supported by two or more independent evidence types and replicated across two or more screens are enriched for drugs with prior breast-cancer-relevant evidence, compared with random drug sets of equal size.

---

## 4. Aims and deliverables

| Aim | Description | Tier |
|---|---|---|
| **Aim 0** | Reproducible data layer: scripted download, harmonization, caching | Core |
| **Aim 1** | Define epigenetic states in breast cancer cell lines and test association with drug response across the library | Core |
| **Aim 2** | Benchmark whether methylation adds predictive value over baselines; replicate across independent screens | Core |
| **Aim 3** | Tumor-to-cell-line mapping using TCGA-BRCA and METABRIC | Extension |
| **Aim 4** | Signature reversal using LINCS L1000; evidence integration; annotation; web app | Extension (integration/app are required for the "tool" claim) |

---

## 5. Data sources (public only)

| Resource | Used for | Notes |
|---|---|---|
| **DepMap / CCLE** | Cell-line promoter methylation (RRBS), expression, annotations, CRISPR dependency | Pin a specific release **[VERIFY current release and file names]** |
| **PRISM Repurposing** (primary and secondary screens) | Drug response across many lines | Primary screen: many compounds, single dose. Secondary: multi-dose, fewer lines per compound |
| **GDSC** | Independent drug-response replication | Pin version **[VERIFY]** |
| **CTRP** | Independent drug-response replication | **[VERIFY]** |
| **TCGA-BRCA** (via GDC / UCSC Xena) | Tumor methylation (450K) and expression, subtype labels | Large methylation matrix; filter to annotated promoter probes early |
| **METABRIC** (via cBioPortal) | Independent tumor cohort | Check availability of methylation vs expression for the needed samples **[VERIFY]** |
| **LINCS L1000** | Drug-induced expression signatures | Cell-line coverage for breast is limited; check which lines are available **[VERIFY]** |
| **Broad Repurposing Hub / DGIdb / ChEMBL** | Drug-to-target and mechanism annotation | |
| **ClinicalTrials.gov API** | Existing clinical activity in breast cancer | |
| **Illumina 450K manifest** | Probe-to-gene and region annotation | Needed for promoter probe selection |

**Data-access note.** Everything above is publicly accessible. Large raw files are not committed to Git. A manifest records each source, version, and checksum; a script downloads and verifies them; processed intermediates are cached as Parquet and (optionally) archived on Zenodo with a DOI.

---

## 6. Methods

### 6.1 Module 0: Data layer (Aim 0)
- Manifest-driven download with version pinning and checksums.
- Harmonize identifiers (cell line IDs such as DepMap IDs, gene symbols vs Ensembl IDs, drug names to a canonical compound ID).
- Store everything as typed Parquet; one function per transformation; no manual spreadsheet steps.
- Document every exclusion with counts (a "sample flow" table).

### 6.2 Module 1: Epigenetic state definition (Aim 1)
Because very few breast cell lines may carry *BRCA1* promoter hypermethylation, *BRCA1* is treated as a **case study and positive-control anchor, not as the sole engine**. States are defined at several levels:

1. **Gene-level promoter methylation** for selected genes (starting with *BRCA1*).
2. **Methylation-silenced gene modules:** genes whose promoter methylation is negatively associated with their own expression across lines (genome-wide, FDR-controlled), summarized into module scores.
3. **Global epigenetic axes:** low-dimensional structure of promoter methylation (for example PCA or NMF components, CIMP-like clustering), checked for confounding by subtype.

### 6.3 Module 2: Pharmacogenomic association (Aim 1)
For each drug *d* and epigenetic state variable *s*:

`response(d, line) ~ s(line) + subtype(line) + covariates`

- Response is area under the dose-response curve (or equivalent) from each screen; lower means more sensitive.
- Analyses in two tiers: (i) breast-only; (ii) pan-cancer with lineage as a covariate and a state-by-breast interaction, to gain power.
- Report per-drug n, effect size with confidence interval, BH-adjusted FDR, and a permutation-based check.
- Consider the biology of each assay (for example, short assays may under-represent drugs that need several cell divisions, such as hypomethylating agents) and report this as a caveat, not a conclusion.

### 6.4 Module 3: Predictive benchmarking and replication (Aim 2)
- Compare models: subtype-only, expression-only, methylation-only, methylation + expression (regularized linear models and tree ensembles).
- **Grouped cross-validation:** leave-one-cell-line-out and leave-one-lineage-out so that information does not leak across related lines.
- Metrics: rank correlation between predicted and observed response, with bootstrap intervals.
- **Replication:** the same associations estimated in each independent screen; report concordance of effect direction and rank.

### 6.5 Module 4: Tumor-to-cell-line mapping (Aim 3)
- Build a shared feature space between tumors and cell lines (shared informative promoter methylation features and/or expression), and address the known systematic differences between tumors and cultured models (for example purity, microenvironment, culture adaptation). Existing approaches such as Celligner are useful reference points **[VERIFY citation]**.
- Map each tumor to its nearest cell-line models; compute transferred drug-response evidence with an uncertainty estimate (distance-weighted, with bootstrap).
- **Validation without circularity:** hold out subtype and state labels; report recovery rate versus random-neighbor baselines; evaluate separately in TCGA-BRCA and METABRIC.

### 6.6 Module 5: Signature reversal (Aim 4)
- From tumor data, derive a differential-expression signature between methylation-defined states (stratified by subtype).
- Score LINCS L1000 drug signatures by connectivity (anti-correlation with the tumor signature) using an established metric, with null distributions from random gene sets.
- Report coverage honestly: not every drug or breast line is represented in L1000.

### 6.7 Module 6: Annotation and evidence integration (Aim 4)
- **Dependency context:** DepMap CRISPR data shows whether breast lines in a given state depend on the drug's target.
- **Clinical context:** approval status, mechanism, and existing breast-cancer trials.
- **Integration:** each module yields a standardized evidence score per drug; combine via a transparent weighted scheme and a rank-aggregation alternative; run a **sensitivity analysis** over weights; output confidence tiers (for example, "multi-evidence, replicated" versus "single-evidence").
- Every candidate gets an **evidence card** that shows each contributing result, n, effect size, and caveats.

---

## 7. Validation and controls

| Check | Purpose |
|---|---|
| **Positive controls** (relationships expected from the literature, such as PARP-inhibitor sensitivity in BRCA1/2-deficient contexts, HDAC-inhibitor activity in triple-negative models) **[VERIFY each expectation]** | Confirm the pipeline can recover known biology before trusting novel hits |
| **Negative controls** (permuted labels, random gene sets, random drug sets) | Estimate false-discovery behavior |
| **Subtype-adjusted analysis** | Ensure signals are not simply subtype proxies |
| **Cross-screen replication** (PRISM, GDSC, CTRP) | Reduce dependence on a single assay |
| **Grouped CV** | Avoid leakage between related lines |
| **Retrospective enrichment** of multi-evidence candidates for prior breast-cancer evidence, against random drug sets | Test H4. *Caveat:* popular drugs have more literature and trials, so enrichment must be compared to size- and popularity-matched random sets |

---

## 8. The tool

**User stories**
1. *Explore:* choose a gene or epigenetic module and see its methylation-expression relationship and cell-line distribution.
2. *Rank:* choose an epigenetic state and subtype context and get a ranked, filterable drug list with evidence tiers.
3. *Map:* upload a methylation or expression profile and see nearest cell-line models and transferred drug evidence with uncertainty.
4. *Inspect:* open an evidence card for any drug.
5. *Understand limits:* a methods and limitations page that states what the tool does not claim.

**Technical stack:** Python 3.11+, pandas/pyarrow, SciPy, statsmodels, scikit-learn, Streamlit and Plotly for the app, pytest, ruff, GitHub Actions for CI, Docker for reproducibility.

**Deployment:** Streamlit Community Cloud or Hugging Face Spaces (free tiers). The app serves precomputed, cached results, so it does not need heavy computation at runtime.

**Responsible-use statement (shown in the app).** Outputs are *research hypotheses for experimental follow-up*, derived from associations in cell lines and public cohorts. They are not clinical recommendations.

---

## 9. Compute plan

Colab, Kaggle, and a local VS Code environment are sufficient:
- Cell-line matrices are small.
- The large object is the TCGA 450K methylation matrix (roughly 485,000 probes). Filter early to annotated promoter probes, process in chunks, and cache as Parquet.
- Heavy steps run once; the app and notebooks read cached results.
- Use fixed random seeds and log package versions for every run.

---

## 10. Repository plan

```
epirepurpose-bc/
├── README.md                  # what it is, quickstart, results summary, citation
├── LICENSE
├── CITATION.cff
├── pyproject.toml             # package metadata and dependencies
├── Makefile                   # make data | make analysis | make test | make app
├── Dockerfile
├── .gitignore                 # data/raw, data/interim, large files, secrets
├── .github/workflows/ci.yml   # lint + tests on every push
├── configs/
│   └── config.yaml            # parameters, release versions, seeds (no magic numbers in code)
├── data/
│   ├── README.md              # how to obtain data; what is tracked vs ignored
│   ├── manifest.yaml          # source, version, URL, checksum for every raw file
│   ├── raw/                   # (ignored) downloaded files
│   ├── interim/               # (ignored) cleaned intermediates
│   └── processed/             # small, final tables (tracked or on Zenodo)
├── src/epirepurpose/
│   ├── data/                  # download, load, harmonize, ID mapping
│   ├── epigenetics/           # probe annotation, state definitions
│   ├── association/           # per-drug models, FDR, permutations
│   ├── benchmark/             # baselines, grouped CV, replication
│   ├── mapping/               # tumor-to-cell-line mapping
│   ├── signature/             # LINCS reversal scoring
│   ├── integrate/             # evidence scores, annotation, tiers
│   └── cli.py
├── app/streamlit_app.py       # web interface over cached results
├── notebooks/                 # numbered, narrative notebooks (exploration and figures)
├── tests/                     # unit tests incl. small synthetic fixtures
├── results/
│   ├── figures/
│   └── tables/
├── docs/
│   ├── PROJECT_PROPOSAL.md    # this document
│   ├── methods.md
│   ├── decisions.md           # log of design decisions and why
│   └── report/                # final write-up
└── environment/               # lockfile / requirements for exact reproduction
```

**Git practices that read well on a CV**
- Small, descriptive commits; a branch per module; pull requests even if you are the only author.
- Tag a release for each milestone (`v0.1-data-layer`, `v0.2-association`, ...).
- Keep a `docs/decisions.md` log: it shows scientific judgment.
- Never commit raw data or credentials; commit the manifest and the scripts that fetch it.
- Put a results figure and a "What this project found" section near the top of the README.

---

## 11. Timeline (part-time, approximately 18 to 20 weeks)

| Phase | Weeks | Deliverable |
|---|---|---|
| **0. Setup and data layer** | 1-3 | Repo, manifest, scripted download, harmonized cell-line tables, sample-flow table |
| **1. Epigenetic states** | 4-6 | Promoter probe annotation, gene/module/global state definitions, positive-control checks |
| **2. Association and benchmarking** (core complete) | 7-10 | Per-drug results, baselines, grouped CV, cross-screen replication, **core report draft** |
| **3. Tumor-to-model mapping** | 11-13 | Mapping method, validation in TCGA-BRCA and METABRIC |
| **4. Signature reversal and integration** | 14-16 | L1000 scoring, annotation, evidence tiers, sensitivity analysis |
| **5. Tool and write-up** | 17-20 | Streamlit app, tests/CI, Docker, final report, optional preprint |

**Decision points:** at the end of Phase 2, decide whether to proceed to Aims 3 and 4 or deepen the core. A well-executed core with honest benchmarks is stronger than a rushed full pipeline.

---

## 12. Risks and mitigations

| Risk | Mitigation |
|---|---|
| **Few breast lines per drug in PRISM secondary** (the prototype saw only about 2 to 6 per drug) | Use the primary screen for breadth, GDSC and CTRP for more breast lines, and a pan-cancer model with lineage terms |
| **Very few lines with BRCA1 hypermethylation** | Treat BRCA1 as a case study; rely on module-level and global epigenetic states |
| **Methylation confounded with subtype** | Subtype as covariate; stratified analyses; report the confounding explicitly |
| **Tumor-to-line gap** | Dedicated validation with held-out labels; report uncertainty; do not overclaim |
| **Data release drift / broken links** | Pin versions, record checksums, archive processed outputs |
| **Assay limitations** (for example, short exposure for epigenetic drugs) | State as caveat; use replication and mechanism annotation |
| **Association is not causation** | Language discipline; dependency and signature evidence as orthogonal support; no clinical claims |
| **Scope creep** | Core/extension split with a formal decision point |
| **Popular-drug bias in retrospective validation** | Matched random sets |

---

## 13. Expected outputs and how to describe them

- Public GitHub repository with tests, CI, Docker, and documentation
- Hosted web app
- Written report in paper format (introduction, methods, results, limitations); optional bioRxiv preprint
- Processed results archived with a DOI (Zenodo)

**CV framing guidance.** Describe only what you actually complete, with numbers you can defend (datasets, sample sizes, benchmark outcomes). Prefer wording like "Built and benchmarked an open-source pipeline integrating ... across N cell lines and M drugs" over claims such as "discovered new treatments." Be ready to explain every design choice and limitation in an interview.

---

## 14. Ethics and responsible use

- Only public, de-identified data are used; follow each resource's terms of use and cite them.
- Candidate drugs are hypotheses for laboratory follow-up, not treatment advice. The app and README must say so plainly.

---

## 15. Key references (starting list)

**[VERIFY every citation before use; these are listed from memory as search starting points.]**

- Barretina et al., 2012, *Nature*: Cancer Cell Line Encyclopedia.
- Ghandi et al., 2019, *Nature*: Next-generation characterization of the CCLE.
- Corsello et al., 2020, *Nature Cancer*: PRISM drug repurposing screen.
- Iorio et al., 2016, *Cell*: GDSC pharmacogenomic landscape.
- Seashore-Ludlow et al., 2015, *Cancer Discovery*: CTRP.
- Subramanian et al., 2017, *Cell*: LINCS L1000.
- Tsherniak et al., 2017, *Cell*: Cancer dependency map (DepMap).
- Warren et al., 2021, *Nature Communications*: Celligner (tumor-cell line alignment).
- Cancer Genome Atlas Network, 2012, *Nature*: comprehensive molecular portraits of breast tumours.
- Curtis et al., 2012, *Nature*: METABRIC.
- Pushpakom et al., 2019, *Nature Reviews Drug Discovery*: drug repurposing review.

---

## 16. Immediate next actions

1. Create the GitHub repository from the provided skeleton.
2. Choose the final project name.
3. Verify current DepMap, GDSC, CTRP, and LINCS release versions and file names; fill `data/manifest.yaml`.
4. Write `docs/decisions.md` entry #1: scope tiers and why.
5. Phase 0: download breast-relevant cell-line tables and produce the first sample-flow table.
