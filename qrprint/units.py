# qrprint/units.py
from __future__ import annotations

from dataclasses import dataclass

_MM_PER_INCH = 25.4


_UNIT_ALIASES = {
    "mm": "mm",
    "millimeter": "mm",
    "millimeters": "mm",
    "cm": "cm",
    "centimeter": "cm",
    "centimeters": "cm",
    "m": "m",
    "meter": "m",
    "meters": "m",
    "in": "in",
    "inch": "in",
    "inches": "in",
    "px": "px",
    "pixel": "px",
    "pixels": "px",
    "pt": "pt",
    "point": "pt",
    "points": "pt",
    "pc": "pc",
    "pica": "pc",
}


def mm_to_px(mm: float, dpi: int) -> int:
    """
    Convert millimeters to pixels using the given DPI, rounding to the nearest int.
    This rounding matches print workflows where integer device pixels are required.
    """
    return int(round((mm / _MM_PER_INCH) * dpi))


def px_to_mm(px: int, dpi: int) -> float:
    """
    Convert pixels back to millimeters at the given DPI.
    Returns a floating value in mm.
    """
    return (px / dpi) * _MM_PER_INCH


def _to_mm(value: float, unit: str, dpi: int | None = 300) -> float:
    """
    Normalize any supported unit to millimeters. "px" conversions require a DPI.

    - value: numerical value to convert
    - unit: unit string (aliases supported)
    - dpi: required when converting from or to pixels
    """
    if unit is None:
        raise ValueError("unit must be specified")

    key = _UNIT_ALIASES.get(unit.lower())
    if key is None:
        raise ValueError(f"Unsupported unit: {unit}")

    if key == "mm":
        return float(value)
    if key == "cm":
        return float(value) * 10.0
    if key == "m":
        return float(value) * 1000.0
    if key == "in":
        return float(value) * _MM_PER_INCH
    if key == "pt":
        # 1 point = 1/72 inch
        return float(value) * (_MM_PER_INCH / 72.0)
    if key == "pc":
        # 1 pica = 12 points
        return float(value) * (_MM_PER_INCH / 6.0)
    if key == "px":
        if not dpi or dpi <= 0:
            raise ValueError("DPI must be a positive int for px conversions")
        return px_to_mm(float(value), int(dpi))


def _from_mm(mm: float, unit: str, dpi: int | None = 300) -> float:
    """Convert millimeters to the requested unit."""
    key = _UNIT_ALIASES.get(unit.lower())
    if key is None:
        raise ValueError(f"Unsupported unit: {unit}")

    if key == "mm":
        return mm
    if key == "cm":
        return mm / 10.0
    if key == "m":
        return mm / 1000.0
    if key == "in":
        return mm / _MM_PER_INCH
    if key == "pt":
        return mm * 72.0 / _MM_PER_INCH
    if key == "pc":
        return mm * 6.0 / _MM_PER_INCH
    if key == "px":
        if not dpi or dpi <= 0:
            raise ValueError("DPI must be a positive int for px conversions")
        # return floating px so caller can choose rounding
        return (mm / _MM_PER_INCH) * dpi


def convert_units(value: float, from_unit: str, to_unit: str, dpi: int | None = 300, round_px: bool = True) -> float:
    """
    Convert between supported units (mm, cm, m, in, px, pt, pc).

    - round_px: when converting to pixels, rounds to nearest int if True.
    - dpi: required for px conversions; default 300 if not provided.

    Returns a float; when converting to px and round_px is True, returns an int-compatible float
    (e.g., 300.0) but you may cast to int if needed.
    """
    mm_val = _to_mm(value, from_unit, dpi)
    result = _from_mm(mm_val, to_unit, dpi)
    if round_px and _UNIT_ALIASES.get(to_unit.lower()) == "px":
        # keep numeric type simple — return an int when rounding to px
        return float(int(round(result)))
    return float(result)


def pretty_units() -> list[str]:
    """Return a sorted list of canonical units supported (string values)."""
    return sorted(set(_UNIT_ALIASES.values()))


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Convert between length units (mm/cm/m/in/px/pt/pc)")
    p.add_argument("value", type=float, help="Value to convert")
    p.add_argument("from_unit", help="From unit (e.g., mm, cm, m, in, px)")
    p.add_argument("to_unit", help="To unit (e.g., mm, cm, m, in, px)")
    p.add_argument("--dpi", type=int, default=300, help="DPI for px conversions (default 300)")
    p.add_argument("--no-round", dest="round_px", action="store_false", help="Don't round when converting to px")
    args = p.parse_args()

    try:
        out = convert_units(args.value, args.from_unit, args.to_unit, dpi=args.dpi, round_px=args.round_px)
    except Exception as e:
        print("Error:" if isinstance(e, Exception) else "", e)
        raise SystemExit(2)

    print(out)


@dataclass(frozen=True)
class SizePx:
    width: int
    height: int
