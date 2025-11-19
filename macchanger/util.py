# File: macchanger/util.py
from __future__ import annotations

import os
import random
import re
import shutil
import string
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Tuple


MAC_RE = re.compile(r"^[0-9A-Fa-f]{2}([:\-]?[0-9A-Fa-f]{2}){5}$")


def normalize_mac(mac: str) -> str:
    """Normalize MAC to 12 hex without separators, uppercase."""
    mac = mac.strip()
    if ":" in mac or "-" in mac:
        mac = re.sub(r"[:-]", "", mac)
    mac = mac.upper()
    if len(mac) != 12 or not all(c in string.hexdigits.upper() for c in mac):
        raise ValueError("Invalid MAC length or characters")
    return mac


def format_mac_colon(mac12: str) -> str:
    return ":".join(mac12[i : i + 2] for i in range(0, 12, 2))


def validate_mac(mac: str) -> None:
    if not MAC_RE.match(mac):
        # also try raw 12 hex
        cleaned = mac.replace(":", "").replace("-", "")
        if len(cleaned) != 12 or not all(c in string.hexdigits for c in cleaned):
            raise ValueError(f"Invalid MAC address: {mac}")


def require_admin() -> None:
    if sys.platform.startswith(("linux", "darwin")):
        if os.geteuid() != 0:
            raise PermissionError("Please run as root (sudo).")
    elif sys.platform.startswith("win"):
        # heuristic: most Windows shells need elevation; we can't test reliably here.
        pass


def run(cmd: List[str], dry_run: bool = False) -> Tuple[int, str, str]:
    if dry_run:
        return 0, "(dry-run) " + " ".join(cmd), ""
    proc = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def which(binary: str) -> str | None:
    return shutil.which(binary)


def random_mac(local_admin: bool = True, unicast: bool = True) -> str:
    """Generate a random MAC. local_admin=True sets the Locally Administered bit."""
    # Start with 6 bytes
    b = [random.randint(0, 255) for _ in range(6)]
    if unicast:
        b[0] &= 0xFE  # clear multicast bit
    else:
        b[0] |= 0x01
    if local_admin:
        b[0] |= 0x02  # set locally administered bit
    else:
        b[0] &= 0xFD
    return ":".join(f"{x:02X}" for x in b)

