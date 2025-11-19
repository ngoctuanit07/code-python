# qrprint/exceptions.py
from __future__ import annotations


class QRPrintError(Exception):
    """Base error for qrprint."""


class SizeTooSmallError(QRPrintError):
    """Raised when target size is too small for requested QR constraints."""
