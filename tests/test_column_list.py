from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_column_list import parse_column_list, find_missing_error_columns


def test_column_list_has_no_missing_errors(tmp_path):
    config = tmp_path / "pcigale.ini"
    config.write_text(
        "column_list = HSC_i, HSC_i_err, jwst.nircam.F150W, jwst.nircam.F150W_err\n"
    )

    columns = parse_column_list(config)
    missing = find_missing_error_columns(columns)

    assert missing == []


def test_column_list_detects_missing_errors(tmp_path):
    config = tmp_path / "pcigale.ini"
    config.write_text(
        "column_list = HSC_i, HSC_i_err, jwst.nircam.F150W\n"
    )

    columns = parse_column_list(config)
    missing = find_missing_error_columns(columns)

    assert missing == ["jwst.nircam.F150W"]
