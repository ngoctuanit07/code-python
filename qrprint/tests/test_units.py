import math
from qrprint import convert_units, mm_to_px


def test_mm_cm_m():
    assert convert_units(1000, "mm", "m") == 1.0
    assert convert_units(10, "cm", "mm") == 100.0


def test_inch_mm():
    assert math.isclose(convert_units(1, "in", "mm"), 25.4)


def test_px_mm_rounding():
    # 25.4 mm -> 300 px at 300 DPI
    assert convert_units(25.4, "mm", "px", dpi=300) == 300.0


def test_px_to_mm():
    # 300 px @ 300 DPI -> 25.4 mm
    assert math.isclose(convert_units(300, "px", "mm", dpi=300), 25.4)


def test_no_round_px():
    # 0.5 in @ 300 DPI -> 150 px (no rounding; exact)
    assert math.isclose(convert_units(0.5, "in", "px", dpi=300, round_px=False), 150.0)
