from pathlib import Path
from qrprint.__main__ import parse_size, _normalize_number_string


def test_parse_size_cm():
    # width-cm should be converted to mm
    mm = parse_size(None, 7.439, None, 300)
    assert round(mm, 3) == 74.39


def test_parse_size_string():
    # supports 'mm' and 'cm' suffix in strings
    mm = parse_size(None, None, "7.439cm", 300)
    assert round(mm, 3) == 74.39


def test_parse_size_comma_decimal():
    # supports comma decimal in the width/height '74,39cm'
    mm = parse_size(None, None, "30,997cm", 300)
    assert round(mm, 2) == 309.97


def test_normalize_number_string():
    assert _normalize_number_string("30,997") == "30.997"
    assert _normalize_number_string("1.234,56") == "1234.56"


def test_padding_cm_to_mm():
    # 0,5 cm => 5 mm
    from qrprint.units import convert_units

    mm = convert_units(0.5, "cm", "mm", dpi=300)
    assert round(mm, 3) == 5.0
