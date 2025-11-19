# File: macchanger/platform_ops.py
from __future__ import annotations

import sys
from typing import Tuple

from .util import format_mac_colon, normalize_mac, run


def set_mac_linux(interface: str, mac12: str, dry_run: bool = False) -> Tuple[bool, str]:
    # ip tool is the modern way (net-tools ifconfig is deprecated)
    rc, out, err = run(["ip", "link", "set", "dev", interface, "down"], dry_run)
    if rc != 0 and not dry_run:
        return False, f"Failed to bring down {interface}: {err or out}"
    rc, out, err = run(
        ["ip", "link", "set", "dev", interface, "address", format_mac_colon(mac12)],
        dry_run,
    )
    if rc != 0 and not dry_run:
        return False, f"Failed to set MAC: {err or out}"
    rc, out, err = run(["ip", "link", "set", "dev", interface, "up"], dry_run)
    if rc != 0 and not dry_run:
        return False, f"Failed to bring up {interface}: {err or out}"
    return True, "OK"


def set_mac_macos(interface: str, mac12: str, dry_run: bool = False) -> Tuple[bool, str]:
    # macOS requires interface down/up around setting sometimes
    rc, out, err = run(["ifconfig", interface, "down"], dry_run)
    if rc != 0 and not dry_run:
        return False, f"Failed to bring down {interface}: {err or out}"
    rc, out, err = run(
        ["ifconfig", interface, "ether", format_mac_colon(mac12)], dry_run
    )
    if rc != 0 and not dry_run:
        return False, f"Failed to set MAC: {err or out}"
    rc, out, err = run(["ifconfig", interface, "up"], dry_run)
    if rc != 0 and not dry_run:
        return False, f"Failed to bring up {interface}: {err or out}"
    return True, "OK"


def set_mac_windows(adapter_name: str, mac12: str, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Windows uses the 'NetworkAddress' advanced property if supported by the driver.
    We use PowerShell cmdlets: Set-NetAdapterAdvancedProperty then bounce the adapter.
    """
    ps_cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        # Set property
        f"Set-NetAdapterAdvancedProperty -Name '{adapter_name}' "
        f"-RegistryKeyword 'NetworkAddress' -RegistryValue '{mac12}' -NoRestart -ErrorAction Stop; "
        # Bounce adapter to apply
        f"Disable-NetAdapter -Name '{adapter_name}' -Confirm:$false -PassThru | Out-Null; "
        f"Start-Sleep -Seconds 1; "
        f"Enable-NetAdapter -Name '{adapter_name}' -Confirm:$false -PassThru | Out-Null; "
        "Write-Output 'OK'"
    ]
    rc, out, err = run(ps_cmd, dry_run)
    if rc != 0 and not dry_run:
        return False, f"PowerShell error: {err or out}"
    return True, "OK"


def clear_mac_windows(adapter_name: str, dry_run: bool = False) -> Tuple[bool, str]:
    ps_cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        f"Set-NetAdapterAdvancedProperty -Name '{adapter_name}' "
        f"-RegistryKeyword 'NetworkAddress' -RegistryValue '' -NoRestart -ErrorAction SilentlyContinue; "
        f"Disable-NetAdapter -Name '{adapter_name}' -Confirm:$false -PassThru | Out-Null; "
        f"Start-Sleep -Seconds 1; "
        f"Enable-NetAdapter -Name '{adapter_name}' -Confirm:$false -PassThru | Out-Null; "
        "Write-Output 'OK'",
    ]
    rc, out, err = run(ps_cmd, dry_run)
    if rc != 0 and not dry_run:
        return False, f"PowerShell error: {err or out}"
    return True, "OK"


def get_platform_setter():
    if sys.platform.startswith("linux"):
        return set_mac_linux
    if sys.platform.startswith("darwin"):
        return set_mac_macos
    if sys.platform.startswith("win"):
        return set_mac_windows
    raise RuntimeError("Unsupported platform")

