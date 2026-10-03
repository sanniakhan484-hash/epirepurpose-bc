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

## #5 Checkpoint 5: methylation matrix (2026-10-02)
- Built data/interim/methylation_matrix.parquet: 20,192 TSS regions x 623 cell lines (columns are DepMap IDs). Gene/region annotation saved separately in tss_annotation.csv. Script: scripts/02_build_methylation_matrix.py.
- Issue found: some missing values were stored as space-padded "NA" strings (about 527k entries), which made pandas read columns as text. Fixed by coercing all values to numeric; unparseable entries become missing.
- Quality: 4.2% missing overall, no region over 50% missing, values within 0-1, no duplicate region IDs, average coverage 16 to 4,587 (median about 330).
- Open decision: 2,778 genes have multiple TSS regions. Rule to be chosen when building gene-level features (candidate: highest-coverage region, as used for BRCA1).
- Caveat: avg_coverage is averaged across cell lines, not per cell line.

## #6 Checkpoint 6: drug matrix (2026-10-02)
- Built data/interim/drug_matrix.parquet (6,790 treatments x 623 cell lines, DepMap IDs) and drug_meta.csv (name, screen, dose, MOA, target, n_lines, n_breast). Script: scripts/03_build_drug_matrix.py.
- Quality: 20.4% missing; every treatment has >=392 cell lines and >=15 breast lines (24 for the positive-control drugs, 27 for guadecitabine).
- Distribution: median -0.06; 1% of values below -5.2, 0.1% below -9.8; upper tail small (99.9th percentile +1.7). Long negative tail is likely a measurement floor from strong killing, not necessarily error.
- Decision: rank-based statistics are primary; sensitivity analysis with clipped values (for example at the 1st percentile).
- 1 treatment has no metadata (compound list and matrix disagree on one row; possible duplicated ID). Exclude it and inspect later.
- 207 drug names appear more than once (screen/batch/form). Duplicate-handling rule to be chosen at analysis time and documented. The 11 positive-control drugs each appear once.
- Implication: breast-only testing has about 24 lines per drug. It remains exploratory; the pan-cancer model with lineage terms is the main analysis.

## #7 Checkpoint 7: methylation structure (2026-10-02)
- PCA on the 5,000 most variable regions (regions with <=10% missing; remaining gaps filled with the region mean). Script: scripts/04_methylation_pca.py. Scores saved to data/interim/methylation_pcs.csv.
- Subtype grouping rule written in code (breast lines): TNBC 13, ER+ 9, HER2+ without ER 5. The ER+ group mixes HER2- (4) and HER2+ (5) lines; kept together for now.
- Positive control passed: tissue lineage explains a large share of several PCs (eta-squared 0.39 for PC1, up to 0.70 for PC7), so the methylation data is biologically structured and not scrambled.
- Breast subtype: eta-squared is near chance (expected about 0.08 with n=27, 3 groups) for most PCs but 0.41 (PC5) and 0.44 (PC9) for two. Suggestive only; would need a permutation test.
- Implication: lineage is the dominant source of methylation variation and also affects drug response. Pan-cancer models must adjust for lineage, and results must be checked within-lineage (including breast-only) to avoid rediscovering tissue differences.

## #8 Checkpoint 8: drug response structure (2026-10-02)
- Script: scripts/05_drug_structure.py. Rank-based eta-squared per treatment for lineage (17 lineages with >=10 lines, 588 cell lines). Output: data/interim/drug_lineage_eta2.csv.
- Finding: lineage explains little of drug response on average (mean eta-squared 0.047, maximum 0.287; chance level is about 0.027). This corrects an earlier expectation that lineage would dominate drug response. Lineage stays as a covariate in all models because it dominates methylation structure (checkpoint 7).
- Positive controls behave as expected: HDAC inhibitors strongly cytotoxic in all lineages (breast medians -1.5 to -3.9), so they are unlikely to show epigenetic-state selectivity; DNMT inhibitors weak in the 5-day assay (azacitidine -0.27, decitabine -0.77 in breast); PARP inhibitors weak at a single dose, talazoparib clearest (-0.79). Lineage rankings for olaparib, niraparib and rucaparib are near zero and mostly noise.
- Guadecitabine comes from screen REP.1M, the other ten positive-control drugs from REP.PRIMARY. Not directly comparable.
- Lymphoid and myeloid lines have no data for the 10 REP.PRIMARY positive-control drugs (older screen used adherent lines only). Every analysis must use only the cell lines with data for that treatment.
- Display bug fixed: lineages with no data sorted as "least sensitive" because their median was NaN. Fixed with dropna() before sorting.

## #9 Checkpoint 9: expression data (2026-10-03)
- Source: DepMap 26Q1 OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv (305.0 MB; log2(TPM+1), protein-coding genes). Script: scripts/check_expression.py.
- Structure: 6 info columns (Unnamed: 0, SequencingID, ModelConditionID, ModelID, IsDefaultEntryForMC, IsDefaultEntryForModel) then 19,215 gene columns named "SYMBOL (EntrezID)". The portal pop-up described different column names; the real header was checked before coding against it.
- 1,775 profiles for 1,719 cell lines; 54 lines have more than one profile. IsDefaultEntryForModel = Yes for exactly one profile per line. Decision: keep only the default profile per cell line.
- Coverage: 618 of the 623 master cell lines have expression, including all 27 breast lines. Expression-dependent analyses use the 618 lines; methylation-vs-drug analyses keep all 623.
- Gene naming: strip the " (EntrezID)" suffix to match the plain symbols used in the methylation annotation.


## #11 Checkpoint 11: gene-level methylation vs expression (2026-10-03)
- Script: scripts/07_gene_methylation_expression.py. For each of 12,694 genes (methylation region with the highest avg_coverage per gene), Spearman rho across 618 cell lines (raw), and a lineage-adjusted version (ranks minus lineage means, then correlation; df = n - lineages - 1). BH FDR on adjusted p-values. Output: data/interim/gene_meth_expr.csv.
- Findings: median rho -0.024 raw and -0.011 adjusted. Genes with rho < -0.3: 2,115 raw, 1,425 adjusted (about a third of the raw signal was lineage). Genes with adjusted rho > +0.3: only 42. All 1,425 adjusted hits have FDR < 0.05, so with n about 600 the FDR filter adds nothing at that effect size; the effect-size cutoff is what matters. The -0.3 cutoff is provisional and not yet justified.
- Known genes (adjusted rho): MGMT -0.44, CDH1 -0.49, RASSF1 -0.23, ESR1 -0.20 (all FDR < 0.001, as expected from the literature); BRCA1 +0.09 (null, consistent with checkpoint 1). MLH1 +0.02 and CDKN2A -0.10 (FDR 0.12) do not show silencing. Untested explanations: CDKN2A homozygous deletion in cancer lines; for MLH1, silencing in a small subset of lines and/or the highest-coverage region not covering its promoter.
- Decision: use the lineage-adjusted rho as the primary measure. Keep the highest-coverage region rule as provisional until the MLH1 check (all MLH1 TSS regions) is done.