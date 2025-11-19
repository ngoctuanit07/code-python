from __future__ import annotations

import httpx

from wallet_tool.models import TokenBalance, WalletReport, TxRecord
from wallet_tool.providers.base import ProviderError


class BlockstreamBTCProvider:
    """BTC via Blockstream public API (no API key)."""

    def __init__(self, base_url: str = "https://blockstream.info/api"):
        self.base_url = base_url.rstrip("/")

    async def fetch(self, address: str, chain: str, history: int | None = None) -> WalletReport:
        if chain.lower() not in ("btc", "bitcoin"):
            raise ProviderError("BlockstreamBTCProvider only supports 'btc' chain.")
        async with httpx.AsyncClient(timeout=25.0) as client:
            # balance
            r = await client.get(f"{self.base_url}/address/{address}")
            if r.status_code != 200:
                raise ProviderError(f"Blockstream error {r.status_code}: {r.text}")
            data = r.json()

            funded = data.get("chain_stats", {}).get("funded_txo_sum", 0) + data.get("mempool_stats", {}).get(
                "funded_txo_sum", 0
            )
            spent = data.get("chain_stats", {}).get("spent_txo_sum", 0) + data.get("mempool_stats", {}).get(
                "spent_txo_sum", 0
            )
            sats = funded - spent
            amount_btc = sats / 1e8

            tb = TokenBalance(
                chain="btc", symbol="BTC", name="Bitcoin",
                contract_address=None, decimals=8, amount=amount_btc,
                quote_rate=None, quote=None, logo_url=None,
            )

            txs = []
            if history and history > 0:
                rt = await client.get(f"{self.base_url}/address/{address}/txs")
                if rt.status_code == 200:
                    for t in (rt.json() or [])[:history]:
                        txid = t.get("txid")
                        # Tính net change cho địa chỉ trong tx này
                        inputs_from_addr = 0
                        for vin in t.get("vin", []):
                            prev = vin.get("prevout") or {}
                            if prev.get("scriptpubkey_address") == address:
                                inputs_from_addr += prev.get("value", 0)
                        outputs_to_addr = 0
                        for vout in t.get("vout", []):
                            if vout.get("scriptpubkey_address") == address:
                                outputs_to_addr += vout.get("value", 0)
                        net_sats = outputs_to_addr - inputs_from_addr
                        direction = "in" if net_sats > 0 else ("out" if net_sats < 0 else None)
                        amt_btc = abs(net_sats) / 1e8 if net_sats != 0 else None

                        txs.append(
                            TxRecord(
                                chain="btc",
                                tx_hash=txid,
                                timestamp=t.get("status", {}).get("block_time"),
                                from_address=None,
                                to_address=None,
                                amount=amt_btc,
                                token_symbol="BTC" if amt_btc is not None else None,
                                contract_address=None,
                                direction=direction,
                            )
                        )

        return WalletReport(address=address, chain="btc", items=[tb], txs=txs)
