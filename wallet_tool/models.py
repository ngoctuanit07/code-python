from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class TokenBalance:
    chain: str
    symbol: str
    name: str
    contract_address: Optional[str]  # None for native coin (e.g., ETH/BTC/TRX)
    decimals: int
    amount: float                    # human-readable units
    quote_rate: Optional[float]      # price per unit in USD if available
    quote: Optional[float]           # total value in USD if available
    logo_url: Optional[str] = None


@dataclass(frozen=True)
class TxRecord:
    chain: str
    tx_hash: str
    timestamp: Optional[int]  # unix epoch ms or s depending on provider
    from_address: Optional[str]
    to_address: Optional[str]
    amount: Optional[float]           # human-readable if known
    token_symbol: Optional[str]       # e.g. ETH, USDC, TRX, ...
    contract_address: Optional[str]   # token address if applicable


@dataclass(frozen=True)
class WalletReport:
    address: str
    chain: str
    items: List[TokenBalance] = field(default_factory=list)
    txs: List[TxRecord] = field(default_factory=list)

    def total_usd(self) -> Optional[float]:
        vals = [i.quote for i in self.items if i.quote is not None]
        return sum(vals) if vals else None
