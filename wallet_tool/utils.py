from __future__ import annotations

import re


_EVM_ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
_BTC_ADDRESS_RE = re.compile(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[0-9a-zA-Z]{11,71}$")
_TRON_ADDRESS_RE = re.compile(r"^T[1-9A-HJ-NP-Za-km-z]{33}$")  # Base58Check, độ dài 34, bắt đầu T


def is_evm_address(addr: str) -> bool:
    return bool(_EVM_ADDRESS_RE.match(addr))


def is_btc_address(addr: str) -> bool:
    return bool(_BTC_ADDRESS_RE.match(addr))


def is_tron_address(addr: str) -> bool:
    return bool(_TRON_ADDRESS_RE.match(addr))


def detect_chain(addr: str) -> str | None:
    """
    Trả về 'evm' | 'btc' | 'tron' hoặc None nếu không chắc chắn.
    """
    if is_evm_address(addr):
        return "evm"
    if is_btc_address(addr):
        return "btc"
    if is_tron_address(addr):
        return "tron"
    return None
