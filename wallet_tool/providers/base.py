from __future__ import annotations

from typing import Protocol, Optional

from wallet_tool.models import WalletReport


class ProviderError(RuntimeError):
    pass


class WalletProvider(Protocol):
    async def fetch(self, address: str, chain: str, history: int | None = None) -> WalletReport:
        """
        Lấy số dư (và nếu history > 0, cố gắng lấy lịch sử giao dịch gần nhất).
        """
        ...
