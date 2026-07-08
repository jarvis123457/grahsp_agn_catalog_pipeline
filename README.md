# GRAHSP AGN Catalog Pipeline

A repository to document my progress for preparing photometric data, use GRAHSP on that and then validate configs, write tests, and extract AGN host-galaxy observable parameters.

#Workflow

1. Check input photometry units.
2. Require spectroscopic redshifts.
3. Match photometric bands to GRAHSP filter names.
4. Build a GRAHSP-ready FITS catalog.
5. Generate a matching `pcigale.ini`.
6. Verify catalog and configuration.
7. Run the critical `_err` column check.
8. Run a small 2-source test before the full catalog.
9. Extract results and apply quality-control flags.

## Demo Commands

```bash
python scripts/build_catalog.py
python scripts/verify_catalog.py data/processed/catalog_demo.fits
python scripts/check_column_list.py configs/pcigale_demo.ini data/processed/catalog_demo.fits
pytest -q
