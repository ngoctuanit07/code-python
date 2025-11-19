$env:MORALIS_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjhkYzYxOTY3LTI3MGUtNGI2NS1iZDk5LTBlY2E0YTE3M2FkZiIsIm9yZ0lkIjoiNDgyMTA2IiwidXNlcklkIjoiNDk1OTg3IiwidHlwZUlkIjoiMmQ5ZTM1YWUtNzYyNy00NjI5LTkwMDgtMjk3YmU4MTA0ZDBlIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NjM1NDM2OTQsImV4cCI6NDkxOTMwMzY5NH0.6ckTdRU-YJwxlovBOr50IbpE4xQub1k99eDbh8nDSuo"
$env:TRON_API_KEY = "e7753967-ee43-4d0b-a747-3b8cdc6cac98"
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

python -m wallet_tool.cli -a 0x8Cb9A43EfB5F9E43c2f9A3D5E0f44d7528612a61 -c bsc -p moralis -H 10
