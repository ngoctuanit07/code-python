# qrprint/qr.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from PIL import Image
import qrcode

from .units import mm_to_px, SizePx
from .exceptions import SizeTooSmallError


@dataclass(frozen=True)
class QRLabelConfig:
    data: str
    width_mm: float
    height_mm: float
    padding_mm: float = 0.5
    dpi: int = 300
    background: str = "white"
    error_correction: int = qrcode.constants.ERROR_CORRECT_H
    min_quiet_modules: int = 4
    allow_stretch: bool = False


@dataclass(frozen=True)
class QRBuildInfo:
    target_px: Tuple[int, int]
    padding_px: int
    inner_rect_px: Tuple[int, int]
    qr_square_px: int
    module_px: int
    quiet_modules: int
    dpi: int
    stretched: bool


def _compute_matrix_size(qr: qrcode.QRCode) -> int:
    """Modules per side, excluding quiet zone."""
    return len(qr.get_matrix())


def _build_qr_object(data: str, error_correction: int) -> qrcode.QRCode:
    # Let library auto-select version, keep border=0 (we add quiet zone manually)
    qr = qrcode.QRCode(
        version=None,
        error_correction=error_correction,
        box_size=1,
        border=0,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr


def _render_qr_square(
    qr: qrcode.QRCode,
    inner_max_px: int,
    min_quiet_modules: int,
) -> tuple[Image.Image, int, int]:
    """
    Choose an integer module pixel size so that:
    total = (modules + 2*quiet) * module_px <= inner_max_px
    Returns (img_rgb, total_qr_px, module_px)

    Raises SizeTooSmallError if not enough room for 1 px/module.
    """
    modules = _compute_matrix_size(qr)
    denom = modules + 2 * min_quiet_modules
    module_px = inner_max_px // denom
    if module_px < 1:
        raise SizeTooSmallError(
            f"Inner size {inner_max_px}px too small; need at least {denom}px."
        )

    # Make base image at 1 px/module, then scale with NEAREST to keep edges crisp
    base = qr.make_image(fill_color="black", back_color="white").convert("L")
    qr_px = modules * module_px
    qr_img = base.resize((qr_px, qr_px), Image.NEAREST)

    quiet_px = min_quiet_modules * module_px
    total_qr_px = qr_px + 2 * quiet_px

    canvas = Image.new("L", (total_qr_px, total_qr_px), 255)
    canvas.paste(qr_img, (quiet_px, quiet_px))

    return canvas.convert("RGB"), total_qr_px, module_px


def _compose_center(
    qr_img: Image.Image,
    target: SizePx,
) -> Image.Image:
    bg = Image.new("RGB", (target.width, target.height), "white")
    x = (target.width - qr_img.width) // 2
    y = (target.height - qr_img.height) // 2
    bg.paste(qr_img, (x, y))
    return bg


def build_qr_label(cfg: QRLabelConfig) -> tuple[Image.Image, QRBuildInfo]:
    """
    Generate a label image with exact physical size (mm) at given DPI,
    containing a *square* QR code rendered for optimal scan reliability.

    Returns: (PIL.Image, QRBuildInfo)
    """
    target_w_px = mm_to_px(cfg.width_mm, cfg.dpi)
    target_h_px = mm_to_px(cfg.height_mm, cfg.dpi)
    padding_px = mm_to_px(cfg.padding_mm, cfg.dpi)

    if target_w_px <= 2 * padding_px or target_h_px <= 2 * padding_px:
        raise SizeTooSmallError("Padding too large for the target size.")

    inner_w = target_w_px - 2 * padding_px
    inner_h = target_h_px - 2 * padding_px

    inner_sq = min(inner_w, inner_h)

    qr = _build_qr_object(cfg.data, cfg.error_correction)

    if cfg.allow_stretch:
        # Render as square with safe quiet zone (based on min dimension),
        # then stretch to fill inner rectangle (NOT recommended).
        qr_sq_img, sq_size, module_px = _render_qr_square(
            qr, inner_max_px=min(inner_w, inner_h), min_quiet_modules=cfg.min_quiet_modules
        )
        stretched = qr_sq_img.resize((inner_w, inner_h), Image.NEAREST)

        bg = Image.new("RGB", (target_w_px, target_h_px), cfg.background)
        bg.paste(stretched, (padding_px, padding_px))

        info = QRBuildInfo(
            target_px=(target_w_px, target_h_px),
            padding_px=padding_px,
            inner_rect_px=(inner_w, inner_h),
            qr_square_px=sq_size,
            module_px=module_px,
            quiet_modules=cfg.min_quiet_modules,
            dpi=cfg.dpi,
            stretched=True,
        )
        return bg, info

    # Recommended path: keep QR square; center within inner rectangle
    qr_sq_img, sq_size, module_px = _render_qr_square(
        qr, inner_max_px=inner_sq, min_quiet_modules=cfg.min_quiet_modules
    )

    # Place the square inside exact-size background
    bg = Image.new("RGB", (target_w_px, target_h_px), cfg.background)
    x = (target_w_px - qr_sq_img.width) // 2
    y = (target_h_px - qr_sq_img.height) // 2
    bg.paste(qr_sq_img, (x, y))

    info = QRBuildInfo(
        target_px=(target_w_px, target_h_px),
        padding_px=padding_px,
        inner_rect_px=(inner_w, inner_h),
        qr_square_px=sq_size,
        module_px=module_px,
        quiet_modules=cfg.min_quiet_modules,
        dpi=cfg.dpi,
        stretched=False,
    )
    return bg, info
