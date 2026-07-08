#!/usr/bin/env python3

"""
Check that every flux band in a GRAHSP column_list has a matching _err column.

This catches a dangerous class of bugs:
the run may appear to converge, but the results can be physically meaningless
if uncertainty columns are missing.
"""

import re
import sys
from pathlib import Path

try:
    from astropy.table import Table
except ImportError:
    Table = None


def parse_column_list(config_path):
    text = Path(config_path).read_text()

    match = re.search(r"column_list\s*=\s*(.+)", text)

    if not match:
        raise ValueError("No column_list found in config file")

    return [col.strip() for col in match.group(1).split(",") if col.strip()]


def find_missing_error_columns(columns):
    flux_cols = [c for c in columns if not c.endswith("_err")]
    err_cols = set(c for c in columns if c.endswith("_err"))

    missing = []

    for flux_col in flux_cols:
        if flux_col + "_err" not in err_cols:
            missing.append(flux_col)

    return missing


def check_against_fits(columns, fits_path):
    if Table is None:
        print("WARN: astropy not installed; skipping FITS check")
        return False

    table = Table.read(fits_path)
    missing = [col for col in columns if col not in table.colnames]

    if missing:
        print("FAIL: These columns are in column_list but missing from FITS:")
        for col in missing:
            print(f"  {col}")
        return False

    print(f"OK: all {len(columns)} column_list entries exist in FITS")
    return True


def main():
    if len(sys.argv) not in (2, 3):
        print("Usage:")
        print("  python scripts/check_column_list.py configs/pcigale_demo.ini")
        print("  python scripts/check_column_list.py configs/pcigale_demo.ini data/processed/catalog_demo.fits")
        sys.exit(1)

    config_path = sys.argv[1]
    fits_path = sys.argv[2] if len(sys.argv) == 3 else None

    columns = parse_column_list(config_path)
    missing_error_cols = find_missing_error_columns(columns)

    if missing_error_cols:
        print("CRITICAL BUG DETECTED")
        print("These flux columns have no matching _err column:")

        for col in missing_error_cols:
            print(f"  {col} -> missing {col}_err")

        print()
        print("Stop here and fix the config before running GRAHSP.")
        sys.exit(1)

    flux_cols = [c for c in columns if not c.endswith("_err")]
    print(f"OK: all {len(flux_cols)} flux bands have matching _err columns")

    if fits_path:
        ok = check_against_fits(columns, fits_path)
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()
