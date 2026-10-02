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