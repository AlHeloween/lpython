param(
    [ValidateSet("User", "Machine", "Process", "None")]
    [string]$PathScope = "User"
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

function Remove-PathEntry([string]$Scope, [string]$Entry) {
    if ($Scope -eq "None") {
        return
    }

    if ($Scope -eq "Machine" -and -not (Test-IsAdmin)) {
        throw "Machine-scope uninstall requires an elevated PowerShell session."
    }

    if ($Scope -eq "Process") {
        $entries = Get-PathEntries $env:Path
        $env:Path = (($entries | Where-Object { $_ -ne $Entry }) -join ';')
        return
    }

    $currentPath = [Environment]::GetEnvironmentVariable("Path", $Scope)
    $entries = Get-PathEntries $currentPath
    [Environment]::SetEnvironmentVariable("Path", (($entries | Where-Object { $_ -ne $Entry }) -join ';'), $Scope)
}

$InstallRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BinDir = Join-Path $InstallRoot "bin"

Remove-PathEntry -Scope $PathScope -Entry $BinDir

Write-Host "Removed PATH entry for $BinDir from scope '$PathScope'."
Write-Host "Delete '$InstallRoot' manually if you want to remove the installed files."
