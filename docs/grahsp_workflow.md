# GRAHSP Workflow Notes

## Before Running

- Confirm flux units are Jy.
- Require spectroscopic redshifts.
- Match each photometric band to a GRAHSP filter name.
- Require at least 4 valid bands per source.
- Make sure every flux column has a matching `_err` column.

## Build Stage

- Read input photometry.
- Convert units if needed.
- Remove invalid fluxes and errors.
- Write a GRAHSP-ready FITS catalog.
- Write a matching `pcigale.ini`.

## Verification Stage

Run:

```bash
python scripts/verify_catalog.py data/processed/catalog_demo.fits
python scripts/check_column_list.py configs/pcigale_demo.ini data/processed/catalog_demo.fits
