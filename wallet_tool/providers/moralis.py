from __future__ import annotations

import os
from decimal import Decimal
from typing import List, Optional

import httpx

from wallet_tool.models import TokenBalance, WalletReport, TxRecord
from wallet_tool.providers.base import ProviderError

MORALIS_CHAINS = {
    "eth": "eth", "ethereum": "eth",
    "bsc": "bsc", "binance": "bsc",
    "polygon": "polygon", "matic": "polygon",
    "arbitrum": "arbitrum",
    "optimism": "optimism",
    "avalanche": "avalanche", "avax": "avalanche",
    "fantom": "fantom",
    "base": "base",
}

NATIVE_SYMBOL = {
    "eth": "ETH", "bsc": "BNB", "polygon": "MATIC",
    "arbitrum": "ETH", "optimism": "ETH",
    "avalanche": "AVAX", "fantom": "FTM", "base": "ETH",
}


class MoralisProvider:
    """EVM balances & (basic) tx list via Moralis Web3 API (no USD quotes here)."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://deep-index.moralis.io/api/v2.2"):
        self.api_key = api_key or os.getenv("MORALIS_API_KEY")
        if not self.api_key:
            raise ProviderError("Missing MORALIS_API_KEY in environment.")
        self.base_url = base_url.rstrip("/")

    async def fetch(self, address: str, chain: str, history: int | None = None) -> WalletReport:
        chain_param = MORALIS_CHAINS.get(chain.lower())
        if not chain_param:
            raise ProviderError(f"Unsupported chain '{chain}' for Moralis. Try one of: {sorted(MORALIS_CHAINS)}")

        headers = {"X-API-Key": self.api_key}
        address_l = address.lower()

        async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
            # Native balance
            r_native = await client.get(f"{self.base_url}/{address}/balance", params={"chain": chain_param})
            if r_native.status_code != 200:
                raise ProviderError(f"Moralis native balance error {r_native.status_code}: {r_native.text}")
            native = r_native.json()

            # ERC20 list
            r_erc20 = await client.get(f"{self.base_url}/{address}/erc20", params={"chain": chain_param})
            if r_erc20.status_code != 200:
                raise ProviderError(f"Moralis erc20 error {r_erc20.status_code}: {r_erc20.text}")
            erc20 = r_erc20.json()

            # txs (native value & direction)
            txs: List[TxRecord] = []
            if history and history > 0:
                r_txs = await client.get(f"{self.base_url}/{address}", params={"chain": chain_param, "limit": min(100, history)})
                if r_txs.status_code == 200:
                    td = r_txs.json().get("result", [])
                    sym = NATIVE_SYMBOL.get(chain_param, "NATIVE")
                    for t in td[:history]:
                        # 'value' là chuỗi wei
                        wei = t.get("value") or "0"
                        try:
                            amt = float(Decimal(wei) / (Decimal(10) ** 18))
                        except Exception:
                            amt = None
                        f = (t.get("from_address") or "").lower() or None
                        to = (t.get("to_address") or "").lower() or None
                        direction = None
                        if f and f == address_l:
                            direction = "out"
                        elif to and to == address_l:
                            direction = "in"
                        txs.append(
                            TxRecord(
                                chain=chain.lower(),
                                tx_hash=t.get("hash"),
                                timestamp=t.get("block_timestamp"),
                                from_address=f,
                                to_address=to,
                                amount=amt,
                                token_symbol=sym if amt is not None else None,
                                contract_address=None,
                                direction=direction,
                            )
                        )

        # Build balances
        items: List[TokenBalance] = []
        native_symbol = NATIVE_SYMBOL.get(chain_param, "NATIVE")
        native_amount = float(Decimal(native.get("balance") or "0") / (Decimal(10) ** 18))
        if native_amount != 0.0:
            items.append(
                TokenBalance(chain=chain.lower(), symbol=native_symbol, name=native_symbol,
                             contract_address=None, decimals=18, amount=native_amount,
                             quote_rate=None, quote=None, logo_url=None)
            )

        for t in erc20:
            try:
                decimals = int(t.get("decimals") or 0)
                raw = Decimal(t.get("balance") or "0")
                amount = float(raw / (Decimal(10) ** decimals) if decimals > 0 else raw)
                if amount == 0.0:
                    continue
                items.append(
                    TokenBalance(
                        chain=chain.lower(),
                        symbol=(t.get("symbol") or "").strip() or "?",
                        name=(t.get("name") or "").strip() or (t.get("symbol") or "?"),
                        contract_address=t.get("token_address"),
                        decimals=decimals,
                        amount=amount,
                        quote_rate=None,
                        quote=None,
                        logo_url=None,
                    )
                )
            except Exception:
                continue

        return WalletReport(address=address, chain=chain.lower(), items=items, txs=txs)
