from __future__ import annotations

import argparse
import asyncio
import csv
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from wallet_tool.models import WalletReport
from wallet_tool.providers.blockstream_btc import BlockstreamBTCProvider
from wallet_tool.providers.covalent import CovalentProvider
from wallet_tool.providers.moralis import MoralisProvider
from wallet_tool.providers.tron import TronProvider
from wallet_tool.providers.solana import SolanaProvider
from wallet_tool.providers.base import ProviderError
from wallet_tool.utils import detect_chain, is_btc_address, is_evm_address, is_tron_address

console = Console()


# ----------------------------- helpers ---------------------------------
def _pick_provider(chain: str, provider: Optional[str]):
    c = chain.lower()
    if c in {"btc", "bitcoin"}:
        return BlockstreamBTCProvider()
    if c == "tron":
        return TronProvider()
    if c in {"sol", "solana"}:
        return SolanaProvider()
    # EVM:
    if provider is None or provider.lower() == "covalent":
        return CovalentProvider()
    if provider and provider.lower() == "moralis":
        return MoralisProvider()
    raise ProviderError(f"Unknown provider '{provider}'. Available: covalent, moralis")


def _validate_addr(addr: str, chain: str):
    c = chain.lower()
    if c in {"btc", "bitcoin"}:
        if not is_btc_address(addr):
            raise ProviderError("Invalid BTC address format.")
    elif c == "tron":
        if not is_tron_address(addr):
            raise ProviderError("Invalid Tron address format (Base58, starts with 'T').")
    elif c in {"sol", "solana"}:
        # Solana validation đã nằm trong detect_chain; ở đây chỉ kiểm tra tối thiểu độ dài base58
        if not (32 <= len(addr) <= 44):
            raise ProviderError("Invalid Solana address length (expected 32–44 base58 chars).")
    else:
        if not is_evm_address(addr):
            raise ProviderError("Invalid EVM address format (0x + 40 hex).")


def _export_csv(rep: WalletReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["chain", "symbol", "name", "contract_address", "decimals", "amount", "quote_rate_usd", "quote_usd"]
        )
        for i in rep.items:
            w.writerow(
                [
                    i.chain,
                    i.symbol,
                    i.name,
                    i.contract_address or "",
                    i.decimals,
                    f"{i.amount:.18f}",
                    "" if i.quote_rate is None else i.quote_rate,
                    "" if i.quote is None else i.quote,
                ]
            )


# format số tránh scientific notation, cắt 0 dư
def human_amount(val: float | None, max_decimals: int = 18) -> str:
    if val is None:
        return "-"
    s = f"{val:.{max_decimals}f}".rstrip("0").rstrip(".")
    return s or "0"


def _print_report(rep: WalletReport, as_json: bool, show_count: bool, show_txs: bool):
    token_count = len(rep.items)
    if as_json:
        payload = {
            "address": rep.address,
            "chain": rep.chain,
            "token_count": token_count,
            "total_usd": rep.total_usd(),
            "items": [
                {
                    "symbol": i.symbol,
                    "name": i.name,
                    "contract_address": i.contract_address,
                    "decimals": i.decimals,
                    "amount": i.amount,
                    "quote_rate": i.quote_rate,
                    "quote": i.quote,
                }
                for i in rep.items
            ],
            "txs": [
                {
                    "tx_hash": t.tx_hash,
                    "timestamp": t.timestamp,
                    "from": t.from_address,
                    "to": t.to_address,
                    "amount": t.amount,  # numeric để client tuỳ format
                    "token_symbol": t.token_symbol,
                    "contract_address": t.contract_address,
                    "direction": t.direction,
                }
                for t in rep.txs
            ]
            if show_txs
            else [],
        }
        console.print_json(data=payload)
        return

    # Balances table
    table = Table(title=f"Wallet {rep.address} on {rep.chain}")
    table.add_column("Symbol")
    table.add_column("Name")
    table.add_column("Amount", justify="right")
    table.add_column("USD/Unit", justify="right")
    table.add_column("USD Total", justify="right")
    for i in sorted(rep.items, key=lambda x: (x.quote or 0), reverse=True):
        table.add_row(
            i.symbol,
            i.name,
            f"{i.amount:,.8f}".rstrip("0").rstrip("."),
            f"{i.quote_rate:,.4f}" if i.quote_rate is not None else "-",
            f"{i.quote:,.2f}" if i.quote is not None else "-",
        )
    caption = []
    if show_count:
        caption.append(f"Token count: {token_count}")
    total = rep.total_usd()
    if total is not None:
        caption.append(f"Estimated portfolio value: ${total:,.2f} USD")
    if caption:
        table.caption = " | ".join(caption)
    console.print(table)

    # Transactions table
    if show_txs and rep.txs:
        t2 = Table(title="Recent Transactions")
        t2.add_column("Time")
        t2.add_column("Hash")
        t2.add_column("Dir")
        t2.add_column("From → To")
        t2.add_column("Amount")
        for t in rep.txs:
            hshort = (t.tx_hash[:10] + "…") if t.tx_hash else ""
            pair = f"{t.from_address or '?'} → {t.to_address or '?'}"
            amt = f"{human_amount(t.amount)} {t.token_symbol}" if (t.amount is not None and t.token_symbol) else "-"
            t2.add_row(str(t.timestamp or "-"), hshort, t.direction or "-", pair, amt)
        console.print(t2)


# ------------------------------ main -----------------------------------
def main(argv: list[str] | None = None) -> int:
    # Cho phép người dùng gõ thêm từ 'check' mà không lỗi (compat)
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0].lower() == "check":
        argv = argv[1:]

    p = argparse.ArgumentParser(
        prog="wallet_tool",
        description="Check balances, tokens & recent transactions by address (auto chain-detect).",
    )
    p.add_argument("-a", "--address", required=True, help="Wallet address")
    p.add_argument(
        "-c",
        "--chain",
        default="auto",
        help="eth/bsc/polygon/... | btc | tron | sol/solana | auto (default)",
    )
    p.add_argument(
        "-p",
        "--provider",
        choices=["covalent", "moralis"],
        default=None,
        help="EVM provider (default: covalent)",
    )
    p.add_argument("--json", action="store_true", help="Output JSON instead of table")
    p.add_argument("--count", action="store_true", help="Print only token count")
    p.add_argument("--export-csv", type=Path, help="Export balances to CSV")
    # -h dành cho help của argparse, nên dùng -H cho history
    p.add_argument("--history", "-H", type=int, help="Fetch last N transactions if supported")

    args = p.parse_args(argv)

    try:
        # auto-detect chain
        chain = args.chain
        if chain.lower() == "auto":
            d = detect_chain(args.address)
            if not d:
                raise ProviderError("Không nhận diện được chain từ địa chỉ. Hãy chỉ định --chain.")
            chain = {"evm": "eth", "btc": "btc", "tron": "tron", "solana": "solana"}[d]
            console.print(f"[cyan]Detected chain:[/cyan] {chain}")

        _validate_addr(args.address, chain)
        prov = _pick_provider(chain, args.provider)
        rep: WalletReport = asyncio.run(prov.fetch(args.address, chain, history=args.history))

        if args.export_csv:
            _export_csv(rep, args.export_csv)
            console.print(f"[green]CSV exported to:[/green] {args.export_csv}")

        if args.count:
            console.print(str(len(rep.items)))
            return 0

        _print_report(rep, as_json=args.json, show_count=True, show_txs=bool(args.history))
        return 0
    except ProviderError as e:
        console.print(f"[red]Error:[/red] {e}")
        return 2
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]Unexpected error:[/red] {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
