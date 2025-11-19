# File: macchanger/cli.py
from __future__ import annotations

import argparse
import sys
from typing import Optional

from .platform_ops import clear_mac_windows, get_platform_setter
from .util import (
    format_mac_colon,
    normalize_mac,
    random_mac,
    require_admin,
    validate_mac,
)


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="macchanger",
        description="Change MAC address for an interface (Linux/macOS) or adapter (Windows).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_set = sub.add_parser("set", help="Set MAC address")
    p_set.add_argument("iface", help="Interface/adapter name (e.g., eth0, en0, 'Wi-Fi')")
    p_set.add_argument("mac", help="MAC address (e.g., 02:11:22:33:44:55)")
    p_set.add_argument("--dry-run", action="store_true", help="Print commands only")

    p_rand = sub.add_parser("random", help="Set random locally-administered unicast MAC")
    p_rand.add_argument("iface", help="Interface/adapter name")
    p_rand.add_argument("--dry-run", action="store_true", help="Print commands only")

    p_reset = sub.add_parser(
        "reset",
        help="Reset to driver default (Windows) or set to provided MAC (Linux/macOS).",
    )
    p_reset.add_argument("iface", help="Interface/adapter name")
    p_reset.add_argument(
        "--mac",
        help="On Linux/macOS you must provide the original hardware MAC to restore.",
    )
    p_reset.add_argument("--dry-run", action="store_true", help="Print commands only")

    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    try:
        require_admin()
    except PermissionError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if args.cmd == "set":
        try:
            validate_mac(args.mac)
            mac12 = normalize_mac(args.mac)
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
        setter = get_platform_setter()
        ok, msg = setter(args.iface, mac12, dry_run=args.dry_run)
        if ok:
            print(f"Set MAC on '{args.iface}' to {format_mac_colon(mac12)}")
            return 0
        print(f"ERROR: {msg}", file=sys.stderr)
        return 1

    if args.cmd == "random":
        mac = random_mac()
        mac12 = mac.replace(":", "")
        setter = get_platform_setter()
        ok, msg = setter(args.iface, mac12, dry_run=args.dry_run)
        if ok:
            print(f"Set MAC on '{args.iface}' to {mac} (random)")
            return 0
        print(f"ERROR: {msg}", file=sys.stderr)
        return 1

    if args.cmd == "reset":
        # Windows can clear the advanced property; Linux/macOS need a provided original MAC
        if sys.platform.startswith("win"):
            ok, msg = clear_mac_windows(args.iface, dry_run=args.dry_run)
            if ok:
                print(f"Cleared custom MAC on '{args.iface}' (Windows).")
                return 0
            print(f"ERROR: {msg}", file=sys.stderr)
            return 1
        else:
            if not args.mac:
                print(
                    "ERROR: On Linux/macOS please pass --mac <ORIGINAL_MAC> to restore.",
                    file=sys.stderr,
                )
                return 1
            try:
                validate_mac(args.mac)
                mac12 = normalize_mac(args.mac)
            except ValueError as e:
                print(f"ERROR: {e}", file=sys.stderr)
                return 1
            setter = get_platform_setter()
            ok, msg = setter(args.iface, mac12, dry_run=args.dry_run)
            if ok:
                print(f"Restored MAC on '{args.iface}' to {format_mac_colon(mac12)}")
                return 0
            print(f"ERROR: {msg}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
