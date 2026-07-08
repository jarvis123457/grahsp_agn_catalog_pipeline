#!/usr/bin/env python3

"""
Verify a GRAHSP-ready FITS catalog before running GRAHSP.
"""

import sys
import numpy as np
from astropy.table import Table


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/verify_catalog.py path/to/catalog.fits")
        sys.exit(1)

    catalog_path = sys.argv[1]
    table = Table.read(catalog_path)

    print(f"Catalog: {catalog_path}")
    print(f"Sources: {len(table)}")
    print(f"Columns: {table.colnames}")
    print()

    flux_cols = [
        c for c in table.colnames
        if c not in ("id", "redshift") and not c.endswith("_err")
    ]

    failed = False

    for row in table:
        n_valid = sum(np.isfinite(row[c]) for c in flux_cols)
        if n_valid < 4:
            print(f"FAIL: {row['id']} has only {n_valid} valid bands")
            failed = True

    bad_z = table[table["redshift"] <= 0]
    if len(bad_z) > 0:
        print(f"FAIL: {len(bad_z)} sources have redshift <= 0")
        failed = True

    for col in flux_cols:
        values = np.array(table[col])
        values = values[np.isfinite(values)]

        if len(values) == 0:
            print(f"WARN: {col} has no detections")
            continue

        median_flux = np.nanmedian(values)

        if median_flux > 10:
            print(f"WARN: {col} median flux = {median_flux:.2e} Jy; check units")
        elif median_flux < 1e-15:
            print(f"WARN: {col} median flux = {median_flux:.2e} Jy; check units")
        else:
            ab_mag = -2.5 * np.log10(median_flux) + 8.9
            print(f"OK: {col:25s} median = {median_flux:.2e} Jy, AB = {ab_mag:.2f}")

    err_cols = [c for c in table.colnames if c.endswith("_err")]

    for err_col in err_cols:
        flux_col = err_col.replace("_err", "")

        if flux_col not in table.colnames:
            print(f"FAIL: error column {err_col} has no matching flux column")
            failed = True
            continue

        both = np.isfinite(table[flux_col]) & np.isfinite(table[err_col])
        if both.sum() == 0:
            continue

        snr = table[flux_col][both] / table[err_col][both]

        if (snr <= 0).any():
            print(f"FAIL: {err_col} has non-positive S/N")
            failed = True

    print()
    if failed:
        print("Catalog verification FAILED.")
        sys.exit(1)

    print("Catalog verification passed.")


if __name__ == "__main__":
    main()
