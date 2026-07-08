#!/usr/bin/env python3

"""
Build a small GRAHSP-ready FITS catalog from toy photometry.

This script demonstrates:
- reading photometric data,
- mapping input columns to GRAHSP filter names,
- requiring spectroscopic redshift,
- requiring at least 4 valid bands,
- writing a FITS catalog,
- writing a matching pcigale config file.
"""

import os
import numpy as np
import pandas as pd
from astropy.table import Table

INPUT_FILE = "data/examples/toy_photometry.csv"
OUT_FITS = "data/processed/catalog_demo.fits"
OUT_INI = "configs/pcigale_demo.ini"
MIN_BANDS = 4
FLUX_UNIT_FACTOR = 1.0  # toy data are already in Jy

ID_COL = "sed_id"
Z_COL = "zsp"

BAND_MAP = {
    "NIRCam_F150W": ("jwst.nircam.F150W", "NIRCam_F150W_unc"),
    "NIRCam_F277W": ("jwst.nircam.F277W", "NIRCam_F277W_unc"),
    "NIRCam_F444W": ("jwst.nircam.F444W", "NIRCam_F444W_unc"),
    "MIRI_F770W": ("jwst.miri.F770W", "MIRI_F770W_unc"),
    "HSC_i_flux": ("HSC_i", "HSC_i_err"),
}


def to_float(value):
    """Convert spreadsheet values to float; return NaN for missing data."""
    if value is None:
        return np.nan

    text = str(value).strip()

    if text in ("", "-", "nan", "NaN", "None", "nd", "ND"):
        return np.nan

    if text.startswith("<"):
        return np.nan

    try:
        number = float(text)
        return number if np.isfinite(number) else np.nan
    except (ValueError, TypeError):
        return np.nan


def main():
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("configs", exist_ok=True)

    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {INPUT_FILE}: {len(df)} rows")

    grahsp_bands = list(dict.fromkeys(gname for gname, _ in BAND_MAP.values()))

    ids = []
    redshifts = []
    band_data = {band: [] for band in grahsp_bands}
    band_errs = {band + "_err": [] for band in grahsp_bands}

    skipped = []

    for _, row in df.iterrows():
        source_id = str(row[ID_COL]).strip()
        redshift = to_float(row[Z_COL])

        if not np.isfinite(redshift) or redshift <= 0:
            skipped.append((source_id, "invalid spectroscopic redshift"))
            continue

        fluxes = {}

        for input_col, (grahsp_name, err_col) in BAND_MAP.items():
            flux = to_float(row.get(input_col, np.nan)) * FLUX_UNIT_FACTOR
            err = to_float(row.get(err_col, np.nan)) * FLUX_UNIT_FACTOR

            if np.isfinite(flux) and flux > 0 and np.isfinite(err) and err > 0:
                fluxes[grahsp_name] = (flux, err)

        if len(fluxes) < MIN_BANDS:
            skipped.append((source_id, f"only {len(fluxes)} valid bands"))
            continue

        ids.append(f"XID_{source_id}")
        redshifts.append(redshift)

        for band in grahsp_bands:
            if band in fluxes:
                band_data[band].append(fluxes[band][0])
                band_errs[band + "_err"].append(fluxes[band][1])
            else:
                band_data[band].append(np.nan)
                band_errs[band + "_err"].append(np.nan)

    table = Table()
    table["id"] = ids
    table["redshift"] = redshifts

    active_bands = []

    for band in grahsp_bands:
        values = np.array(band_data[band])
        if np.isfinite(values).any():
            active_bands.append(band)
            table[band] = band_data[band]
            table[band + "_err"] = band_errs[band + "_err"]

    table.write(OUT_FITS, format="fits", overwrite=True)

    column_list = []
    for band in active_bands:
        column_list.append(band)
        column_list.append(band + "_err")

    with open(OUT_INI, "w") as f:
        f.write("# Demo GRAHSP configuration\n")
        f.write(f"data_file = {OUT_FITS}\n")
        f.write("column_list = " + ", ".join(column_list) + "\n")

    print(f"Accepted sources: {len(ids)}")
    print(f"Skipped sources: {len(skipped)}")
    print(f"Saved FITS catalog: {OUT_FITS}")
    print(f"Saved config file: {OUT_INI}")
    print(f"Active bands: {active_bands}")


if __name__ == "__main__":
    main()
