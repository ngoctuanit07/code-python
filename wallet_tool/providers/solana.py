from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx

from wallet_tool.models import TokenBalance, WalletReport, TxRecord
from wallet_tool.providers.base import ProviderError


LAMPORTS_PER_SOL = 1_000_000_000
DEFAULT_RPC = "https://api.mainnet-beta.solana.com"

# SPL Token program id (legacy)
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"


class SolanaProvider:
    """
    Solana balances (SOL + SPL tokens) & recent tx via JSON-RPC.
    - RPC có thể đặt qua env SOLANA_RPC_URL (default mainnet-beta public).
    - Lịch sử: getSignaturesForAddress + getTransaction và suy ra amount SOL (in/out) bằng pre/post balance delta.
      (Best-effort, không phân tích SPL transfers trong lịch sử để giữ đơn giản/nhanh.)
    """

    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = (rpc_url or os.getenv("SOLANA_RPC_URL") or DEFAULT_RPC).strip()

    async def _rpc(self, method: str, params: list[Any]) -> Any:
        payload: Dict[str, Any] = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(self.rpc_url, json=payload)
            if r.status_code != 200:
                raise ProviderError(f"Solana RPC HTTP {r.status_code}: {r.text}")
            data = r.json()
        if "error" in data:
            raise ProviderError(f"Solana RPC error: {data['error']}")
        return data.get("result")

    async def fetch(self, address: str, chain: str, history: int | None = None) -> WalletReport:
        # 1) Native SOL balance
        res_bal = await self._rpc("getBalance", [address, {"commitment": "confirmed"}])
        lamports = int(res_bal.get("value", 0))
        sol = lamports / LAMPORTS_PER_SOL

        items: List[TokenBalance] = []
        if sol != 0:
            items.append(
                TokenBalance(
                    chain="solana",
                    symbol="SOL",
                    name="Solana",
                    contract_address=None,
                    decimals=9,
                    amount=float(sol),
                    quote_rate=None,
                    quote=None,
                    logo_url=None,
                )
            )

        # 2) SPL tokens
        res_tokens = await self._rpc(
            "getTokenAccountsByOwner",
            [
                address,
                {"programId": TOKEN_PROGRAM_ID},
                {"encoding": "jsonParsed", "commitment": "confirmed"},
            ],
        )
        for acc in (res_tokens.get("value") or []):
            try:
                info = (acc.get("account") or {}).get("data", {}).get("parsed", {}).get("info", {})
                token_amt = info.get("tokenAmount", {})
                ui_amount = token_amt.get("uiAmount")
                decimals = int(token_amt.get("decimals") or 0)
                mint = info.get("mint")
                if ui_amount is None or float(ui_amount) == 0.0:
                    continue
                # Tên/symbol không có sẵn từ RPC, để ngắn gọn dùng mint rút gọn làm symbol.
                short = mint[:6] if isinstance(mint, str) else "SPL"
                items.append(
                    TokenBalance(
                        chain="solana",
                        symbol=short,
                        name=mint,
                        contract_address=mint,
                        decimals=decimals,
                        amount=float(ui_amount),
                        quote_rate=None,
                        quote=None,
                        logo_url=None,
                    )
                )
            except Exception:
                continue

        # 3) Transactions (native SOL in/out best-effort)
        txs: List[TxRecord] = []
        if history and history > 0:
            sigs = await self._rpc("getSignaturesForAddress", [address, {"limit": min(100, history)}])
            for sig in sigs[: history]:
                try:
                    tx = await self._rpc(
                        "getTransaction",
                        [sig.get("signature"), {"encoding": "json", "commitment": "confirmed"}],
                    )
                    if not tx:
                        continue
                    msg = (tx.get("transaction") or {}).get("message", {})
                    keys: List[str] = [k.get("pubkey") if isinstance(k, dict) else k for k in msg.get("accountKeys", [])]
                    meta = tx.get("meta") or {}
                    pre = meta.get("preBalances") or []
                    post = meta.get("postBalances") or []

                    # tìm index của address trong accountKeys
                    idx = None
                    for i, k in enumerate(keys):
                        if isinstance(k, str) and k == address:
                            idx = i
                            break
                    # nếu không tìm thấy, bỏ qua amount
                    amount = None
                    direction = None
                    if idx is not None and idx < len(pre) and idx < len(post):
                        delta = (post[idx] - pre[idx]) / LAMPORTS_PER_SOL
                        if delta != 0:
                            amount = abs(delta)
                            direction = "in" if delta > 0 else "out"

                    txs.append(
                        TxRecord(
                            chain="solana",
                            tx_hash=tx.get("transaction", {}).get("signatures", [""])[0],
                            timestamp=tx.get("blockTime"),
                            from_address=None,
                            to_address=None,
                            amount=amount,
                            token_symbol="SOL" if amount is not None else None,
                            contract_address=None,
                            direction=direction,
                        )
                    )
                except Exception:
                    continue

        return WalletReport(address=address, chain="solana", items=items, txs=txs)
