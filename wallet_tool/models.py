from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class TokenBalance:
    chain: str
    symbol: str
    name: str
    contract_address: Optional[str]
    decimals: int
    amount: float
    quote_rate: Optional[float]
    quote: Optional[float]
    logo_url: Optional[str] = None


@dataclass(frozen=True)
class TxRecord:
    chain: str
    tx_hash: str
    timestamp: Optional[int]  # unix epoch (s/ms) hoặc ISO tuỳ provider
    from_address: Optional[str]
    to_address: Optional[str]
    amount: Optional[float]           # số tiền giao dịch (đơn vị human)
    token_symbol: Optional[str]       # ETH/BNB/MATIC/BTC/TRX...
    contract_address: Optional[str]
    direction: Optional[str] = None   # 'out' | 'in' | None


@dataclass(frozen=True)
class WalletReport:
    address: str
    chain: str
    items: List[TokenBalance] = field(default_factory=list)
    txs: List[TxRecord] = field(default_factory=list)

    def total_usd(self) -> Optional[float]:
        vals = [i.quote for i in self.items if i.quote is not None]
        return sum(vals) if vals else None
