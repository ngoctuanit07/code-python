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


class CovalentProvider:
    """
    Balances & (optional) recent tx via Covalent.
    Requires COVALENT_API_KEY.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.covalenthq.com"):
        self.api_key = api_key or os.getenv("COVALENT_API_KEY")
        if not self.api_key:
            raise ProviderError("Missing COVALENT_API_KEY in environment.")
        self.base_url = base_url.rstrip("/")

    async def fetch(self, address: str, chain: str, history: int | None = None) -> WalletReport:
        chain_id = COVALENT_CHAIN_IDS.get(chain.lower())
        if not chain_id:
            raise ProviderError(f"Unsupported EVM chain '{chain}'. Try one of: {sorted(set(COVALENT_CHAIN_IDS.keys()))}")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
            # balances
            url_bal = f"{self.base_url}/v1/{chain_id}/address/{address}/balances_v2/"
            params_bal = {"quote-currency": "USD", "nft": False, "no-nft-fetch": True}
            rb = await client.get(url_bal, params=params_bal)
            if rb.status_code != 200:
                raise ProviderError(f"Covalent error {rb.status_code}: {rb.text}")
            data = rb.json()

            items_raw = data.get("data", {}).get("items", [])
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
                    logo = it.get("logo_url")
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
                            logo_url=logo,
                        )
                    )
                except Exception:
                    continue

            txs: List[TxRecord] = []
            if history and history > 0:
                # dùng transactions_v3 (đơn giản: chỉ lấy trang đầu)
                url_tx = f"{self.base_url}/v1/{chain_id}/address/{address}/transactions_v3/"
                rt = await client.get(url_tx, params={"no-logs": True, "page-size": min(history, 100)})
                if rt.status_code == 200:
                    td = rt.json().get("data", {}).get("items", [])
                    for t in td[:history]:
                        txs.append(
                            TxRecord(
                                chain=chain.lower(),
                                tx_hash=t.get("tx_hash") or t.get("hash") or "",
                                timestamp=t.get("block_signed_at_ts") or t.get("block_signed_at"),
                                from_address=t.get("from_address"),
                                to_address=t.get("to_address"),
                                amount=None,  # Có thể tính từ transfers nhưng giữ đơn giản
                                token_symbol=None,
                                contract_address=None,
                            )
                        )

        return WalletReport(address=address, chain=chain.lower(), items=balances, txs=txs)
