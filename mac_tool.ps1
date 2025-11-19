# mac_tool.ps1 - Simple MAC changer tool for Windows
# Run this script in PowerShell as Administrator

# ===== Check admin =====
$currUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currUser)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "Please run this script in an elevated PowerShell (Run as Administrator)."
    Read-Host "Press Enter to exit"
    exit
}

# ===== Functions =====

function Get-AdapterRegistryKey {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Guid
    )

    $classKey  = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
    $targetKey = $null

    Get-ChildItem $classKey | ForEach-Object {
        try {
            $props = Get-ItemProperty -Path $_.PsPath -ErrorAction Stop
            if ($props.NetCfgInstanceId -eq $Guid) {
                $targetKey = $_.PsPath
            }
        } catch {}
    }

    return $targetKey
}

function New-RandomMac {
    # Create 6 bytes
    $bytes = @()

    # First byte: set local bit, clear multicast bit
    $first = Get-Random -Minimum 0 -Maximum 256
    $first = ($first -bor 0x02) -band 0xFE
    $bytes += $first

    for ($i = 1; $i -lt 6; $i++) {
        $bytes += (Get-Random -Minimum 0 -Maximum 256)
    }

    $macNoSep  = ($bytes | ForEach-Object { '{0:X2}' -f $_ }) -join ''
    $macPretty = ($bytes | ForEach-Object { '{0:X2}' -f $_ }) -join '-'

    return [PSCustomObject]@{
        Raw   = $macNoSep
        Human = $macPretty
    }
}

function Apply-MacChange {
    param(
        [Parameter(Mandatory=$true)][string]$AdapterName,
        [Parameter(Mandatory=$true)][string]$NewMac  # 12 hex chars or "" for reset
    )

    Write-Host ""
    Write-Host ">>> Getting adapter info..." -ForegroundColor Cyan
    $adapter = Get-NetAdapter -Name $AdapterName -ErrorAction Stop
    $guid    = $adapter.InterfaceGuid.ToString()

    Write-Host "Adapter    : $AdapterName"
    Write-Host "Old MAC    : $($adapter.MacAddress)"

    $regKey = Get-AdapterRegistryKey -Guid $guid
    if (-not $regKey) {
        Write-Host "Cannot find registry key for adapter $AdapterName" -ForegroundColor Red
        return
    }

    if ([string]::IsNullOrWhiteSpace($NewMac)) {
        Write-Host ">>> Removing NetworkAddress (reset to default)..." -ForegroundColor Cyan
        Remove-ItemProperty -Path $regKey -Name "NetworkAddress" -ErrorAction SilentlyContinue
    }
    else {
        if ($NewMac -notmatch '^[0-9A-Fa-f]{12}$') {
            Write-Host "Invalid MAC. Need 12 hex characters (0-9, A-F), no separators." -ForegroundColor Red
            return
        }
        Write-Host ">>> Setting NetworkAddress = $NewMac" -ForegroundColor Cyan
        Set-ItemProperty -Path $regKey -Name "NetworkAddress" -Value $NewMac
    }

    Write-Host ">>> Disabling adapter $AdapterName ..." -ForegroundColor Cyan
    Disable-NetAdapter -Name $AdapterName -Confirm:$false
    Start-Sleep -Seconds 3

    Write-Host ">>> Enabling adapter $AdapterName ..." -ForegroundColor Cyan
    Enable-NetAdapter -Name $AdapterName -Confirm:$false
    Start-Sleep -Seconds 2

    Write-Host ">>> Done. Current adapter info:" -ForegroundColor Green
    Get-NetAdapter -Name $AdapterName | Format-List Name,MacAddress,Status
}

# ===== MAIN =====

Write-Host "=== MAC TOOL STARTED ===" -ForegroundColor Yellow
Write-Host ""

Write-Host "=== AVAILABLE NETWORK ADAPTERS ===" -ForegroundColor Yellow
Get-NetAdapter | Select-Object Name, Status, MacAddress | Format-Table -AutoSize
Write-Host ""

$adapterName = Read-Host "Adapter name (press Enter for 'Ethernet')"
if ([string]::IsNullOrWhiteSpace($adapterName)) {
    $adapterName = "Ethernet"
}

try {
    $null = Get-NetAdapter -Name $adapterName -ErrorAction Stop
} catch {
    Write-Host "Adapter '$adapterName' not found. Exit." -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit
}

Write-Host ""
Write-Host "=== MENU ===" -ForegroundColor Yellow
Write-Host "1) Random new MAC"
Write-Host "2) Reset MAC to default (driver)"
Write-Host ""

$choice = Read-Host "Choose 1 or 2"

switch ($choice) {
    "1" {
        $mac = New-RandomMac
        Write-Host ""
        Write-Host "Random MAC generated:" -ForegroundColor Yellow
        Write-Host "  Raw   : $($mac.Raw)"
        Write-Host "  Pretty: $($mac.Human)"
        Apply-MacChange -AdapterName $adapterName -NewMac $mac.Raw
    }
    "2" {
        Apply-MacChange -AdapterName $adapterName -NewMac ""
    }
    default {
        Write-Host "Invalid choice. Exit." -ForegroundColor Red
    }
}

Write-Host ""
Read-Host "Done. Press Enter to close"
