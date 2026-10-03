# Design decisions log

Record each decision with date, options considered, choice, and reason.

## #1 Scope tiers (date: YYYY-MM-DD)
- Core: Aims 0-2 (data layer, association, benchmarking/replication).
- Extensions: Aims 3-4 (tumor mapping, signature reversal, integration, app).
- Reason: a rigorous core is publishable on its own; extensions are added only after the Phase 2 checkpoint.

## #2 Checkpoint 1: methylation data and BRCA1 (2026-10-02)
- Data: DepMap "Methylation (RRBS)" file `CCLE_RRBS_TSS_1kb_20180614.txt`. 20,192 TSS regions x 843 cell lines, 47 breast lines. Coordinates match hg19.
- Finding: BRCA1 promoter methylation is low in breast cell lines (maximum 0.46 in MDAMB134VI, most below 0.1).
- Decision: BRCA1 cannot define methylated vs unmethylated groups among breast lines. It is kept as a case study only. The main analysis uses genome-wide methylation-silenced gene modules and global methylation patterns. BRCA1 will be revisited in tumor data (TCGA) in Aim 3.
- Note: when a single BRCA1 value is needed, use the TSS row with the highest coverage (`BRCA1_17_41276132_41277132`, avg coverage about 120).

## #3 Checkpoint 2: joining methylation to model annotations (2026-10-02)
- 839 of 843 methylation cell lines match Model.csv via CCLEName. All 47 breast lines matched (script: scripts/check_join.py).
- Subtype: use ModelSubtypeFeatures (44 of 47 breast lines labeled in the top-10 printout; 3 to inspect). Approximate grouping: TNBC 20, ER+/HER2- 7, ER+/HER2+ 9, HER2+/ER- 8. Final mapping to be written in code.
- OncotreeSubtype is not used for subtype: its categories overlap and are inconsistent.
- Implication: methylation differs by subtype, so subtype is a required covariate in all association models.

## #4 Checkpoint 3: drug data (2026-10-02)
- Source: DepMap Repurposing 24Q2 Extended Primary Data Matrix and compound list. 6,790 treatments x 919 cell lines (DepMap IDs). Mostly a single 2.5 uM dose, 5-day assay. Value = log2 fold-change in viability vs DMSO (more negative = more killing). This is NOT AUC; AUC applies only to multi-dose screens (secondary PRISM, GDSC, CTRP).
- Quality: 32.5% missing, extreme values (min -26.4, max 8.1), 6,790 rows but 6,575 unique drug names (duplicates across screens/IDs).
- Decision: rank-based statistics (or winsorizing), report per-drug n, handle duplicates explicitly using the `screen` column.
- Sample size: 47 breast lines have methylation, 33 have drug data, 27 have both (my grouping of ModelSubtypeFeatures: TNBC 13, ER+ 9, HER2+/ER- 5).
- Decision: breast-only per-drug testing across ~6,700 treatments is underpowered. Main analysis is pan-cancer with lineage covariates and a breast-specific term. Breast-only results are exploratory, reported with effect sizes and confidence intervals.
- Positive-control drugs present: PARP inhibitors (olaparib, talazoparib, niraparib, rucaparib), HDAC inhibitors (vorinostat, belinostat, panobinostat, romidepsin), DNMT inhibitors (azacitidine, decitabine, guadecitabine).