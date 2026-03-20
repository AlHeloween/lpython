param(
    [string]$TargetDir = (Join-Path $env:LOCALAPPDATA "Programs\LPython"),
    [ValidateSet("User", "Machine", "Process", "None")]
    [string]$PathScope = "User",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Get-PathEntries([string]$PathValue) {
    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return @()
    }

    return @($PathValue.Split(';') | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Add-PathEntry([string]$Scope, [string]$Entry) {
    if ($Scope -eq "None") {
        return
    }

    if ($Scope -eq "Machine" -and -not (Test-IsAdmin)) {
        throw "Machine-scope installation requires an elevated PowerShell session."
    }

    if ($Scope -eq "Process") {
        $currentEntries = Get-PathEntries $env:Path
        if ($currentEntries -notcontains $Entry) {
            $env:Path = ($currentEntries + $Entry) -join ';'
        }
        return
    }

    $currentPath = [Environment]::GetEnvironmentVariable("Path", $Scope)
    $entries = Get-PathEntries $currentPath
    if ($entries -notcontains $Entry) {
        [Environment]::SetEnvironmentVariable("Path", (($entries + $Entry) -join ';'), $Scope)
    }
}

$PackageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetDir = [System.IO.Path]::GetFullPath($TargetDir)
$BinDir = Join-Path $TargetDir "bin"
$crtDlls = @("msvcp140.dll", "vcruntime140.dll", "vcruntime140_1.dll")

if ((Test-Path $TargetDir) -and -not $Force) {
    throw "Target directory '$TargetDir' already exists. Re-run with -Force to overwrite."
}

New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

$copyItems = @(
    "bin",
    "share",
    "README.md",
    "LICENSE",
    "install-lpython.ps1",
    "uninstall-lpython.ps1"
)

foreach ($item in $copyItems) {
    $source = Join-Path $PackageRoot $item
    if (-not (Test-Path $source)) {
        continue
    }

    Copy-Item -LiteralPath $source -Destination $TargetDir -Recurse -Force
}

Add-PathEntry -Scope $PathScope -Entry $BinDir

$missingCrt = @(
    $crtDlls | Where-Object {
        -not (Test-Path (Join-Path $BinDir $_)) -and
        -not (Test-Path (Join-Path $env:WINDIR "System32\$_"))
    }
)

Write-Host "LPython 0.1-git installed to $TargetDir"
if ($PathScope -ne "None") {
    Write-Host "PATH updated for scope '$PathScope' with $BinDir"
}
if ($missingCrt.Count -gt 0) {
    Write-Warning "Missing Microsoft VC++ runtime DLLs: $($missingCrt -join ', '). Install the Microsoft Visual C++ Redistributable if lpython fails to start."
}
Write-Host "Open a new shell to pick up persisted PATH changes."
