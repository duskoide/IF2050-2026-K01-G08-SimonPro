#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '%s\n' "$*"
}

err() {
  printf '%s\n' "$*" >&2
}

have() {
  command -v "$1" >/dev/null 2>&1
}

with_test_deps=0
for arg in "$@"; do
  case "$arg" in
    --with-test-deps)
      with_test_deps=1
      ;;
    *)
      err "Unknown argument: $arg"
      exit 1
      ;;
  esac
done

sudo_cmd=""
if [ "$(id -u)" -ne 0 ]; then
  if have sudo; then
    sudo_cmd="sudo"
  else
    err "sudo is required to install packages. Run as root or install sudo."
    exit 1
  fi
fi

if [ -f /etc/os-release ]; then
  . /etc/os-release
else
  err "Cannot detect Linux distro. /etc/os-release not found."
  exit 1
fi

pkg_mgr=""
case "${ID:-}" in
  ubuntu|debian|linuxmint|pop|elementary)
    pkg_mgr="apt"
    ;;
  fedora|rhel|centos|rocky|almalinux)
    pkg_mgr="dnf"
    ;;
esac

if [ -z "$pkg_mgr" ] && [ -n "${ID_LIKE:-}" ]; then
  case "$ID_LIKE" in
    *debian*)
      pkg_mgr="apt"
      ;;
    *fedora*|*rhel*)
      pkg_mgr="dnf"
      ;;
  esac
fi

if [ -z "$pkg_mgr" ]; then
  err "Unsupported distro: ${ID:-unknown}. Supported: Debian/Ubuntu or Fedora/RHEL."
  exit 1
fi

install_base_packages() {
  if [ "$pkg_mgr" = "apt" ]; then
    $sudo_cmd apt-get update
    $sudo_cmd apt-get install -y curl ca-certificates python3 python3-venv python3-pip
  else
    $sudo_cmd dnf -y install curl ca-certificates python3 python3-pip
  fi
}

log "Installing base packages..."
install_base_packages

if ! have python3; then
  err "python3 not found after install."
  exit 1
fi

if ! python3 - <<'PY'
import sys
sys.exit(0 if sys.version_info >= (3, 10) else 1)
PY
then
  err "Python 3.10 or newer is required."
  exit 1
fi

if ! have uv; then
  log "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

if ! have uv; then
  err "uv is not in PATH. Restart your shell or add ~/.local/bin to PATH."
fi

if ! have docker; then
  log "Installing Docker Engine..."
  curl -fsSL https://get.docker.com | $sudo_cmd sh
fi

if have docker; then
  if ! docker compose version >/dev/null 2>&1; then
    log "Installing docker compose plugin..."
    if [ "$pkg_mgr" = "apt" ]; then
      $sudo_cmd apt-get install -y docker-compose-plugin
    else
      $sudo_cmd dnf -y install docker-compose-plugin
    fi
  fi
fi

if have docker && have getent; then
  if getent group docker >/dev/null 2>&1; then
    if ! groups "$USER" | grep -q "\bdocker\b"; then
      $sudo_cmd usermod -aG docker "$USER"
      log "Added $USER to the docker group. Log out and back in to use docker without sudo."
    fi
  fi
fi

if [ "$with_test_deps" -eq 1 ]; then
  log "Installing headless test dependencies..."
  if [ "$pkg_mgr" = "apt" ]; then
    $sudo_cmd apt-get install -y xvfb libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0 x11-utils libegl1 libgl1 libxcb-cursor0 postgresql-client
  else
    $sudo_cmd dnf -y install xorg-x11-server-Xvfb libX11 libxkbcommon-x11 libXcursor libXrandr libXrender libXinerama libXfixes mesa-libEGL mesa-libGL postgresql
  fi
fi

log "Install complete."
log "Next steps:"
log "- docker compose up -d"
log "- uv sync  (or: pip install -r requirements.txt)"
log "- python main.py"
