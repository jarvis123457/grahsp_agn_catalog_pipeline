#!/usr/bin/env bash

# Test-run template for Vega.
# Edit paths if your installation changes.

set -e

source /vdata1/shared/lavisha/grahsp_venv/bin/activate
cd ~/RainbowLasso

export HDF5_USE_FILE_LOCKING=FALSE
export OMP_NUM_THREADS=1

# Copy the demo config to the name expected by GRAHSP
cp /path/to/grahsp_agn_catalog_pipeline/configs/pcigale_demo.ini pcigale.ini

# Run only after confirming the catalog and config checks pass
python ~/GRAHSP-run/dualsampler.py analyse --cores=1 --plot 2>&1 | tee test_grahsp.log
