# qrprint/__main__.py
from __future__ import annotations

import argparse
from pathlib import Path

from .qr import QRLabelConfig, build_qr_label
from .units import convert_units


def _normalize_number_string(s: str) -> str:
    """Normalize a numeric string to a dot-decimal format suitable for float().

    Handles localized formats like "1.234,56" or "30,997".
    """
    s = str(s).strip().replace(" ", "")
    if "." in s and "," in s:
        # assume '.' is thousands separator and ',' is decimal separator
        s = s.replace(".", "")
        s = s.replace(",", ".")
        return s
    if "," in s:
        return s.replace(",", ".")
    return s


def parse_localized_float(s: str) -> float:
    """Argparse type that accepts comma decimals and thousands separators.

    Examples: "30,997" -> 30.997 ; "1.234,56" -> 1234.56 ; "74.39" -> 74.39
    """
    try:
        return float(_normalize_number_string(s))
    except Exception as e:
        raise argparse.ArgumentTypeError(f"Invalid numerical value: {s}") from e


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="qrprint: Generate precisely-sized QR labels (mm → px).")
    p.add_argument("--data", required=True, help="QR content (URL/text).")
    grp_w = p.add_mutually_exclusive_group(required=True)
    grp_w.add_argument("--width-mm", type=float, help="Target label width in millimeters.")
    grp_w.add_argument("--width-cm", type=parse_localized_float, help="Target label width in centimeters.")
    grp_w.add_argument("--width", type=str, help="Target width with unit, e.g. 74.39mm or 7.439cm")

    grp_h = p.add_mutually_exclusive_group(required=True)
    grp_h.add_argument("--height-mm", type=float, help="Target label height in millimeters.")
    grp_h.add_argument("--height-cm", type=parse_localized_float, help="Target label height in centimeters.")
    grp_h.add_argument("--height", type=str, help="Target height with unit, e.g. 5.02mm or 0.502cm")
    p.add_argument("--padding-mm", type=parse_localized_float, default=None, help="White padding around label (mm).")
    p.add_argument("--padding-cm", type=parse_localized_float, help="White padding around label (cm). Accepts comma decimals e.g. 0,5")
    p.add_argument("--dpi", type=int, default=300, help="Output DPI (e.g., 300, 600).")
    p.add_argument("--min-quiet-modules", type=int, default=4, help="Minimum quiet-zone in modules (per side).")
    p.add_argument("--background", default="white", help='Background color, e.g., "white" or "#FFFFFF".')
    p.add_argument("--output", default="qrcode_label.png", help="Output file path (.png or .jpg).")
    p.add_argument("--allow-stretch", action="store_true", help="Stretch QR to fill inner rectangle (NOT recommended).")
    return p.parse_args()


def parse_size(mm_value: float | None, cm_value: float | None, text: str | None, dpi: int) -> float:
    """Parse a size specified as mm, cm or as a unit-suffixed string; return mm value.

    Rules: prefer mm if provided, then cm, then unit-suffixed string (e.g., '7.2cm' or '74.39mm').
    """
    if mm_value is not None:
        return float(mm_value)
    if cm_value is not None:
        return float(convert_units(float(cm_value), "cm", "mm", dpi=dpi))
    if text:
        import re

        m = re.match(r"^\s*([-+]?\d*[\.,]?\d+)\s*([A-Za-z]+)\s*$", text)
        if not m:
            raise SystemExit("Size parse error: value+unit not recognised")
        val, unit = m.group(1), m.group(2)
        val = _normalize_number_string(val)
        return float(convert_units(float(val), unit, "mm", dpi=dpi))
    raise SystemExit("Missing size value for width/height")


def main() -> None:
    args = parse_args()
    # width_mm / height_mm are parsed by parse_size helper above

    width_mm = parse_size(args.width_mm, args.width_cm, args.width, args.dpi)

    height_mm = parse_size(args.height_mm, args.height_cm, args.height, args.dpi)

    # padding: prefer explicit mm, then cm
    if args.padding_mm is not None:
        padding_mm = args.padding_mm
    elif args.padding_cm is not None:
        padding_mm = float(convert_units(float(args.padding_cm), "cm", "mm", dpi=args.dpi))
    else:
        padding_mm = 0.5

    cfg = QRLabelConfig(
        data=args.data,
        width_mm=width_mm,
        height_mm=height_mm,
        padding_mm=padding_mm,
        dpi=args.dpi,
        background=args.background,
        min_quiet_modules=args.min_quiet_modules,
        allow_stretch=args.allow_stretch,
    )

    img, info = build_qr_label(cfg)

    out_path = Path(args.output)
    ext = out_path.suffix.lower()
    fmt = "PNG" if ext in (".png", "") else ("JPEG" if ext in (".jpg", ".jpeg") else "PNG")

    save_params = {"dpi": (cfg.dpi, cfg.dpi)}
    if fmt == "JPEG":
        save_params.update({"quality": 95, "subsampling": 0})

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path), fmt, **save_params)

    print("✅ QR label generated:", out_path)
    print(f"   - Target: {cfg.width_mm} x {cfg.height_mm} mm @ {cfg.dpi} DPI")
    print(f"   - Target px: {info.target_px[0]} x {info.target_px[1]} px")
    print(f"   - Padding: {cfg.padding_mm} mm -> {info.padding_px} px each side")
    print(f"   - Inner rect px: {info.inner_rect_px[0]} x {info.inner_rect_px[1]} px")
    print(f"   - QR square (incl. quiet zone): {info.qr_square_px} px")
    print(f"   - Module size: {info.module_px} px/module")
    print(f"   - Quiet zone: ≥ {info.quiet_modules} modules/side")
    if info.stretched:
        print("   - ⚠️ Stretched to fill inner rectangle (may reduce scannability).")


if __name__ == "__main__":
    main()
