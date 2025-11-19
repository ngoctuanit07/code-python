#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tool tạo ví: Solana | Dogecoin | Ethereum (MetaMask) | TON (nếu được hỗ trợ)
- Vá lỗi AttributeError: Bip44Coins has no attribute 'TONCOIN'
- Cơ chế phát hiện động enum TON: 'TONCOIN' hoặc 'TON'. Nếu không có, ẩn TON.
- Tùy chọn --ask để nhập số lượng ví tại runtime.
"""

import argparse
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional

from bip_utils import (
    Bip39MnemonicGenerator, Bip39WordsNum, Bip39SeedGenerator,
    Bip44, Bip44Coins, Bip44Changes
)
import base58


# =========================
# Phát hiện hỗ trợ TON động
# =========================
_TON_ENUM_NAME = None
if hasattr(Bip44Coins, "TONCOIN"):
    _TON_ENUM_NAME = "TONCOIN"
elif hasattr(Bip44Coins, "TON"):
    _TON_ENUM_NAME = "TON"   # Một số phiên bản đặt tên ngắn 'TON'
# Nếu _TON_ENUM_NAME vẫn None -> phiên bản bip-utils không có TON


def _get_supported_coins_map() -> Dict[str, Tuple[object, str, str]]:
    """
    Trả về COIN_MAP nhưng KHÔNG tham chiếu TON khi version không hỗ trợ.
    tuple: (enum coin, mô tả, gợi ý path)
    """
    coins: Dict[str, Tuple[object, str, str]] = {
        "eth": (Bip44Coins.ETHEREUM, "Ethereum (MetaMask compatible)", "m/44'/60'/0'/0/i"),
        "doge": (Bip44Coins.DOGECOIN, "Dogecoin", "m/44'/3'/0'/0/i"),
        "sol": (Bip44Coins.SOLANA, "Solana (ed25519, SLIP-0010)", "m/44'/501'/0'/0'"),
    }
    if _TON_ENUM_NAME is not None:
        ton_enum = getattr(Bip44Coins, _TON_ENUM_NAME)
        coins["ton"] = (ton_enum, "TON (Toncoin)", "m/44'/607'/0'/0/i")
    return coins


COIN_MAP = _get_supported_coins_map()


def ensure_outdir(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)


def now_tag() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def gen_mnemonic(words: int) -> str:
    """Sinh mnemonic BIP39 với 12/24 từ."""
    words_num = Bip39WordsNum.WORDS_NUM_12 if words == 12 else Bip39WordsNum.WORDS_NUM_24
    return Bip39MnemonicGenerator().FromWordsNumber(words_num)


def derive_wallets_for_coin(
    coin_key: str,
    count: int,
    words: int,
    passphrase: str = "",
) -> List[dict]:
    """
    Tạo N ví cho 1 coin:
    - ETH/DOGE/TON: BIP44 m/44'/coin'/0'/0/i
    - SOL: m/44'/501'/0'/0' (nhiều ví chỉ dùng index=0; tăng i khi cần nhiều)
    """
    if coin_key not in COIN_MAP:
        # Trường hợp đặc biệt: TON không được hỗ trợ bởi phiên bản bip-utils hiện tại
        if coin_key == "ton":
            raise SystemExit(
                "TON hiện không được hỗ trợ bởi phiên bản 'bip-utils' bạn đang dùng.\n"
                "Cách xử lý:\n"
                " - Chạy: pip install -U bip-utils\n"
                " - Hoặc dùng thư viện TON chuyên dụng (tonsdk/pytoniq)."
            )
        raise ValueError(f"Coin không hỗ trợ: {coin_key}")

    coin_enum, _, _ = COIN_MAP[coin_key]
    results: List[dict] = []

    for i in range(count):
        mnemonic = gen_mnemonic(words)
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate(passphrase)
        bip_ctx = Bip44.FromSeed(seed_bytes, coin_enum)
        acc = bip_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)

        address = acc.PublicKey().ToAddress()
        priv_hex = acc.PrivateKey().Raw().ToHex()

        # WIF (nếu coin hỗ trợ)
        priv_wif = None
        try:
            to_wif = getattr(acc.PrivateKey(), "ToWif", None)
            if callable(to_wif):
                priv_wif = acc.PrivateKey().ToWif()
        except Exception:
            priv_wif = None

        # Solana: thêm secret base58 (32B)
        sol_secret_b58 = None
        if coin_key == "sol":
            try:
                raw_bytes = acc.PrivateKey().Raw().ToBytes()
                sol_secret_b58 = base58.b58encode(raw_bytes).decode("utf-8")
            except Exception:
                sol_secret_b58 = None

        results.append({
            "index": i,
            "mnemonic": mnemonic,
            "passphrase": passphrase,
            "derivation_path_hint": COIN_MAP[coin_key][2],
            "address": address,
            "private_key_hex": priv_hex,
            "private_key_wif": priv_wif,
            "sol_secret_base58": sol_secret_b58,
        })

    return results


def write_txt(
    out_path: str,
    coin_key: str,
    wallets: List[dict],
    append: bool = False
) -> None:
    """Ghi dữ liệu ví ra .txt."""
    mode = "a" if append else "w"
    with open(out_path, mode, encoding="utf-8") as f:
        f.write(f"# === {coin_key.upper()} WALLET EXPORT ===\n")
        f.write(f"# Generated at: {datetime.now().isoformat()}\n")
        f.write("# CẢNH BÁO: Không chia sẻ file này. Private key/mnemonic là TỐI MẬT.\n\n")
        for w in wallets:
            f.write(f"Index: {w['index']}\n")
            f.write(f"Address: {w['address']}\n")
            f.write(f"Mnemonic: {w['mnemonic']}\n")
            if w['passphrase']:
                f.write(f"Passphrase: {w['passphrase']}\n")
            f.write(f"DerivationPathHint: {w['derivation_path_hint']}\n")
            f.write(f"PrivateKeyHex: {w['private_key_hex']}\n")
            if w.get("private_key_wif"):
                f.write(f"PrivateKeyWIF: {w['private_key_wif']}\n")
            if w.get("sol_secret_base58"):
                f.write(f"SolanaSecretBase58(32B): {w['sol_secret_base58']}\n")
            f.write("-" * 60 + "\n")
        f.write("\n")


def prompt_count(default_val: int = 1) -> int:
    """Hỏi người dùng nhập số lượng ví muốn tạo."""
    while True:
        raw = input(f"Nhập số lượng ví muốn tạo cho MỖI coin (mặc định {default_val}): ").strip()
        if raw == "":
            return default_val
        try:
            val = int(raw)
            if val > 0:
                return val
            print("Vui lòng nhập số nguyên dương (>0).")
        except ValueError:
            print("Giá trị không hợp lệ. Hãy nhập số nguyên, ví dụ 3.")


def parse_args() -> argparse.Namespace:
    # Tạo chuỗi mặc định cho --coins dựa theo coin hỗ trợ
    default_coins = ",".join(COIN_MAP.keys())
    parser = argparse.ArgumentParser(
        description="Tool tạo ví SOL | DOGE | ETH(MetaMask) | TON (nếu hỗ trợ) và xuất .txt"
    )
    parser.add_argument(
        "--coins", "-c",
        help=f"Danh sách coin, cách nhau bởi dấu phẩy (mặc định: {default_coins})",
        default=default_coins
    )
    parser.add_argument(
        "--count", "-n",
        help="Số ví muốn tạo cho MỖI coin (bỏ qua nếu dùng --ask)",
        type=int, default=1
    )
    parser.add_argument(
        "--ask",
        action="store_true",
        help="Bật chế độ hỏi số lượng ví tại runtime (ghi đè --count)."
    )
    parser.add_argument(
        "--words",
        help="Số từ mnemonic: 12 hoặc 24 (mặc định: 12)",
        type=int, choices=[12, 24], default=12
    )
    parser.add_argument(
        "--passphrase",
        help="BIP39 passphrase (tùy chọn; để trống nếu không dùng)",
        default=""
    )
    parser.add_argument(
        "--out-dir",
        help="Thư mục xuất file .txt",
        default="./wallet_exports"
    )
    parser.add_argument(
        "--separate",
        action="store_true",
        help="Nếu bật, xuất mỗi coin ra 1 file riêng. Nếu tắt, gộp vào 1 file."
    )
    parser.add_argument(
        "--outfile",
        help="Tên file .txt khi gộp (mặc định: wallets-<timestamp>.txt)",
        default=""
    )
    return parser.parse_args()


def main():
    args = parse_args()
    coins = [c.strip().lower() for c in args.coins.split(",") if c.strip()]

    # Xác thực coin
    for c in coins:
        if c not in COIN_MAP:
            if c == "ton" and _TON_ENUM_NAME is None:
                raise SystemExit(
                    "Bạn đã chọn TON nhưng phiên bản 'bip-utils' hiện tại không hỗ trợ.\n"
                    "Hãy nâng cấp: pip install -U bip-utils"
                )
            raise SystemExit(f"Coin không hỗ trợ: {c}. Hỗ trợ: {', '.join(COIN_MAP.keys())}")

    count: int = prompt_count() if args.ask else max(1, int(args.count or 1))
    ensure_outdir(args.out_dir)

    combined_path = os.path.join(
        args.out_dir,
        args.outfile or f"wallets-{now_tag()}.txt"
    )

    if not args.separate:
        open(combined_path, "w", encoding="utf-8").close()

    for coin_key in coins:
        wallets = derive_wallets_for_coin(
            coin_key=coin_key,
            count=count,
            words=args.words,
            passphrase=args.passphrase
        )

        if args.separate:
            out_path = os.path.join(args.out_dir, f"{coin_key}-wallets-{now_tag()}.txt")
            write_txt(out_path, coin_key, wallets, append=False)
            print(f"[OK] Đã xuất {len(wallets)} ví {coin_key.upper()} -> {out_path}")
        else:
            write_txt(combined_path, coin_key, wallets, append=True)
            print(f"[OK] Đã ghi {len(wallets)} ví {coin_key.upper()} vào file gộp.")

    if not args.separate:
        print(f"[DONE] File gộp: {combined_path}")


if __name__ == "__main__":
    main()
