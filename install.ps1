$ErrorActionPreference = "Stop"

function Write-Log {
  param([string]$Message)
  Write-Host $Message
}

function Ensure-Admin {
  $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
  if (-not $principal.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
    Write-Log "Run this script in an elevated PowerShell (Run as Administrator)."
    exit 1
  }
}

function Test-Command {
  param([string]$Name)
  return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Ensure-Chocolatey {
  if (-not (Test-Command choco)) {
    Write-Log "Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
  }
}

function Ensure-Winget {
  if (-not (Test-Command winget)) {
    Write-Log "winget not found. Install App Installer from Microsoft Store."
    exit 1
  }
}

function Ensure-Python {
  if (-not (Test-Command python)) {
    Write-Log "Installing Python 3.10 via winget..."
    winget install -e --id Python.Python.3.10 --accept-package-agreements --accept-source-agreements
  }
}

function Ensure-UV {
  if (-not (Test-Command uv)) {
    Write-Log "Installing uv..."
    Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -UseBasicParsing | Invoke-Expression
  }
}

function Ensure-Docker {
  if (-not (Test-Command docker)) {
    Write-Log "Installing Docker Desktop via winget..."
    winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
    Write-Log "Docker Desktop installed. You may need to start it once to finish setup."
  }
}

param(
  [switch]$WithTestDeps
)

Ensure-Admin
Ensure-Winget
Ensure-Python
Ensure-UV
Ensure-Docker

if ($WithTestDeps) {
  Write-Log "Headless test deps are handled in CI on Linux. No extra Windows packages required."
}

Write-Log "Install complete."
Write-Log "Next steps:"
Write-Log "- docker compose up -d"
Write-Log "- uv sync  (or: pip install -r requirements.txt)"
Write-Log "- python main.py"
