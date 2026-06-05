#!/usr/bin/env bash
# Provision a fresh Ubuntu/Debian host to run the TSP Solver Arena with gVisor.
# Idempotent-ish; re-running is safe. Run as a sudo-capable user from arena/deploy/.
set -euo pipefail
cd "$(dirname "$0")"

echo "==> 1/6 Docker Engine + compose plugin"
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

echo "==> 2/6 gVisor (runsc)"
if ! command -v runsc >/dev/null 2>&1; then
  (
    set -e
    ARCH="$(uname -m)"
    URL="https://storage.googleapis.com/gvisor/releases/release/latest/${ARCH}"
    wget -q "${URL}/runsc" "${URL}/runsc.sha512" \
         "${URL}/containerd-shim-runsc-v1" "${URL}/containerd-shim-runsc-v1.sha512"
    sha512sum -c runsc.sha512 -c containerd-shim-runsc-v1.sha512
    chmod a+rx runsc containerd-shim-runsc-v1
    sudo mv runsc containerd-shim-runsc-v1 /usr/local/bin/
  )
fi
# Register runsc as a Docker runtime.
sudo mkdir -p /etc/docker
if [ ! -f /etc/docker/daemon.json ]; then
  echo '{"runtimes":{"runsc":{"path":"/usr/local/bin/runsc"}}}' | sudo tee /etc/docker/daemon.json >/dev/null
fi
sudo systemctl restart docker
echo "==> verifying gVisor"
docker run --rm --runtime=runsc hello-world >/dev/null && echo "    runsc OK"

echo "==> 3/6 shared submission workdir + docker group id"
# shellcheck source=/dev/null
source ./.env
# The docker socket is group-owned by `docker` (gid varies by host); write the real
# gid into .env now that Docker is installed, so the worker's group_add grants real
# socket access (replaces whatever placeholder DOCKER_GID was in .env).
sed -i "s/^DOCKER_GID=.*/DOCKER_GID=$(getent group docker | cut -d: -f3)/" .env
sudo mkdir -p "${ARENA_WORK_DIR}"
sudo chmod 1777 "${ARENA_WORK_DIR}"

echo "==> 4/6 toolchain + proxy images (on the host daemon; submissions are siblings)"
../backend/docker/build-presets.sh

echo "==> 5/6 build app images + run migrations"
docker compose build
docker compose run --rm migrate

echo "==> 6/6 start the stack"
docker compose up -d
echo "Done. Point DNS for ${ARENA_DOMAIN} at this host; Caddy will obtain TLS certs."
