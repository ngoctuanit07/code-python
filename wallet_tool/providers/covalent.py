from __future__ import annotations

import os
from decimal import Decimal
from typing import List, Optional

import httpx

from wallet_tool.models import TokenBalance, WalletReport, TxRecord
from wallet_tool.providers.base import ProviderError

COVALENT_CHAIN_IDS = {
    "eth": 1, "ethereum": 1,
    "bsc": 56, "binance": 56,
    "polygon": 137, "matic": 137,
    "arbitrum": 42161,
    "optimism": 10,
    "avax": 43114, "avalanche": 43114,
    "fantom": 250,
    "base": 8453,
}
SYMBOL_BY_CHAIN = {
    "eth": "ETH", "bsc": "BNB", "polygon": "MATIC",
    "arbitrum": "ETH", "optimism": "ETH",
    "avax": "AVAX", "avalanche": "AVAX", "fantom": "FTM", "base": "ETH",
}


class CovalentProvider:
    """Balances & (optional) recent tx via Covalent (needs COVALENT_API_KEY)."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.covalenthq.com"):
        self.api_key = api_key or os.getenv("COVALENT_API_KEY")
        if not self.api_key:
            raise ProviderError("Missing COVALENT_API_KEY in environment.")
        self.base_url = base_url.rstrip("/")

    async def fetch(self, address: str, chain: str, history: int | None = None) -> WalletReport:
        chain_id = COVALENT_CHAIN_IDS.get(chain.lower())
        if not chain_id:
            raise ProviderError(f"Unsupported EVM chain '{chain}'. Try: {sorted(set(COVALENT_CHAIN_IDS.keys()))}")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
            # balances
            url_bal = f"{self.base_url}/v1/{chain_id}/address/{address}/balances_v2/"
            rb = await client.get(url_bal, params={"quote-currency": "USD", "nft": False, "no-nft-fetch": True})
            if rb.status_code != 200:
                raise ProviderError(f"Covalent error {rb.status_code}: {rb.text}")
            items_raw = rb.json().get("data", {}).get("items", [])

            balances: List[TokenBalance] = []
            for it in items_raw:
                try:
                    decimals = int(it.get("contract_decimals") or 0)
                    raw = Decimal(it.get("balance") or "0")
                    amount = float(raw / (Decimal(10) ** decimals) if decimals > 0 else raw)
                    symbol = (it.get("contract_ticker_symbol") or "").strip() or (it.get("contract_name") or "?")
                    name = it.get("contract_name") or symbol
                    contract = it.get("contract_address")
                    quote_rate = it.get("quote_rate")
                    quote = it.get("quote")
                    if amount == 0.0 and (quote is None or quote == 0):
                        continue
                    balances.append(
                        TokenBalance(
                            chain=chain.lower(),
                            symbol=symbol,
                            name=name,
                            contract_address=contract if contract and contract != "0x0000000000000000000000000000000000000000" else None,
                            decimals=decimals,
                            amount=amount,
                            quote_rate=float(quote_rate) if quote_rate is not None else None,
                            quote=float(quote) if quote is not None else None,
                            logo_url=it.get("logo_url"),
                        )
                    )
                except Exception:
                    continue

            # txs (native value & direction)
            txs: List[TxRecord] = []
            if history and history > 0:
                url_tx = f"{self.base_url}/v1/{chain_id}/address/{address}/transactions_v3/"
                rt = await client.get(url_tx, params={"no-logs": True, "page-size": min(history, 100)})
                if rt.status_code == 200:
                    td = rt.json().get("data", {}).get("items", [])
                    sym = SYMBOL_BY_CHAIN.get(chain.lower(), "NATIVE")
                    for t in td[:history]:
                        # value (wei) có thể nằm trong t["value"]
                        val_wei = t.get("value")
                        amt = None
                        if val_wei is not None:
                            try:
                                amt = float(Decimal(str(val_wei)) / (Decimal(10) ** 18))
                            except Exception:
                                amt = None
                        f = (t.get("from_address") or "").lower() or None
                        to = (t.get("to_address") or "").lower() or None
                        direction = None
                        addr_l = address.lower()
                        if f and f == addr_l:
                            direction = "out"
                        elif to and to == addr_l:
                            direction = "in"
                        txs.append(
                            TxRecord(
                                chain=chain.lower(),
                                tx_hash=t.get("tx_hash") or t.get("hash") or "",
                                timestamp=t.get("block_signed_at_ts") or t.get("block_signed_at"),
                                from_address=f,
                                to_address=to,
                                amount=amt,
                                token_symbol=sym if amt is not None else None,
                                contract_address=None,
                                direction=direction,
                            )
                        )

        return WalletReport(address=address, chain=chain.lower(), items=balances, txs=txs)
