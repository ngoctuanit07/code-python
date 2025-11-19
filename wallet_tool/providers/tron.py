from __future__ import annotations

import os
from typing import List, Optional

import httpx

from wallet_tool.models import TokenBalance, WalletReport, TxRecord
from wallet_tool.providers.base import ProviderError


class TronProvider:
    """
    Tron (TRX/TRC-20) via TronGrid.
    - Balance: GET /v1/accounts/{address}
    - TRC20 (best-effort): from 'trc20' arrays if present
    - Tx history: GET /v1/accounts/{address}/transactions (basic)
    Requires TRON_API_KEY (header 'TRON-PRO-API-KEY'). Có thể hoạt động hạn chế nếu không có key.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.trongrid.io"):
        self.api_key = api_key or os.getenv("TRON_API_KEY")
        self.base_url = base_url.rstrip("/")

    async def fetch(self, address: str, chain: str, history: int | None = None) -> WalletReport:
        headers = {}
        if self.api_key:
            headers["TRON-PRO-API-KEY"] = self.api_key

        async with httpx.AsyncClient(timeout=25.0, headers=headers) as client:
            # account info
            r = await client.get(f"{self.base_url}/v1/accounts/{address}")
            if r.status_code != 200:
                raise ProviderError(f"TronGrid error {r.status_code}: {r.text}")
            data = r.json()
            d0 = (data.get("data") or [{}])[0] if isinstance(data.get("data"), list) and data.get("data") else {}

            # Native TRX (Sun -> TRX)
            trx_amount = (d0.get("balance") or 0) / 1_000_000
            items: List[TokenBalance] = []
            if trx_amount != 0:
                items.append(
                    TokenBalance(
                        chain="tron",
                        symbol="TRX",
                        name="TRON",
                        contract_address=None,
                        decimals=6,
                        amount=float(trx_amount),
                        quote_rate=None,
                        quote=None,
                        logo_url=None,
                    )
                )

            # TRC20 tokens (best effort)
            for tmap in d0.get("trc20", []) or []:
                # tmap là dict {contract: balance_str, "name": "...", "symbol": "...", "decimals": "..."} hoặc biến thể
                try:
                    symbol = tmap.get("symbol") or "TRC20"
                    name = tmap.get("name") or symbol
                    decimals = int(tmap.get("decimals") or 0)
                    balance_raw = tmap.get("balance") or "0"
                    amount = float(int(balance_raw) / (10 ** decimals)) if decimals > 0 else float(balance_raw)
                    contract = tmap.get("contract_address") or tmap.get("contract") or None
                    if amount == 0.0:
                        continue
                    items.append(
                        TokenBalance(
                            chain="tron",
                            symbol=symbol,
                            name=name,
                            contract_address=contract,
                            decimals=decimals,
                            amount=amount,
                            quote_rate=None,
                            quote=None,
                            logo_url=None,
                        )
                    )
                except Exception:
                    continue

            # history (basic)
            txs: List[TxRecord] = []
            if history and history > 0:
                rt = await client.get(
                    f"{self.base_url}/v1/accounts/{address}/transactions",
                    params={"limit": min(50, history), "only_confirmed": True},
                )
                if rt.status_code == 200:
                    td = rt.json().get("data", [])
                    for t in td[:history]:
                        txs.append(
                            TxRecord(
                                chain="tron",
                                tx_hash=t.get("txID"),
                                timestamp=t.get("block_timestamp"),
                                from_address=(t.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("owner_address")),
                                to_address=(t.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("to_address")),
                                amount=None,
                                token_symbol=None,
                                contract_address=None,
                            )
                        )

        return WalletReport(address=address, chain="tron", items=items, txs=txs)
