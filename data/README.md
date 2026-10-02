# Data

Raw and interim data are **not** committed. To obtain them:

1. Verify current release versions on each provider's download page.
2. Fill in `manifest.yaml` (url, release; sha256 after first download).
3. Run `epirepurpose download` (or `make data`).

| Folder | Contents | Tracked in Git? |
|---|---|---|
| `raw/` | Files exactly as downloaded | No |
| `interim/` | Cleaned/harmonized intermediates (Parquet) | No |
| `processed/` | Small final tables used by the app | Yes (or Zenodo if large) |
