from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

from wallet_tool.models import WalletReport, TokenBalance
from wallet_tool.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def _sample_report() -> WalletReport:
    return WalletReport(
        address="0x000000000000000000000000000000000000dead",
        chain="eth",
        items=[
            TokenBalance(
                chain="eth",
                symbol="ETH",
                name="Ether",
                contract_address=None,
                decimals=18,
                amount=1.2345,
                quote_rate=2000.0,
                quote=2469.0,
            ),
            TokenBalance(
                chain="eth",
                symbol="USDC",
                name="USD Coin",
                contract_address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                decimals=6,
                amount=100.0,
                quote_rate=1.0,
                quote=100.0,
            ),
        ],
    )


@patch("wallet_tool.cli._pick_provider")
def test_cli_json(mock_pick):
    mock = AsyncMock()
    mock.fetch.return_value = _sample_report()
    mock_pick.return_value = mock

    result = runner.invoke(app, ["check", "-a", "0x000000000000000000000000000000000000dead", "-c", "eth", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["chain"] == "eth"
    assert len(data["items"]) == 2
