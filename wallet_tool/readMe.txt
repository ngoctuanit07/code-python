# Tron (ví của bạn) + 10 giao dịch
python -m wallet_tool.cli -a TTMR8ejfGpcCoqZA9vaaqfWSPwdkGR1gUD -H 10

# Solana (auto detect hoặc ép chain)
python -m wallet_tool.cli -a YOUR_SOL_ADDRESS -H 5
python -m wallet_tool.cli -a YOUR_SOL_ADDRESS -c solana -H 5

# EVM qua Moralis: đếm token & export CSV
python -m wallet_tool.cli -a 0xYourEvmAddress -p moralis --count --export-csv balances.csv

# BTC + 5 giao dịch
python -m wallet_tool.cli -a bc1YourBtcAddress -c btc -H 5

# JSON output
python -m wallet_tool.cli -a YOUR_SOL_ADDRESS -H 5 --json
