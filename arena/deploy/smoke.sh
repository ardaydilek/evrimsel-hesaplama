#!/usr/bin/env bash
# End-to-end smoke for the SUBMISSION PIPELINE on the real stack:
#   build -> migrate (alembic) -> api + worker (+ deps) -> submit -> scored 699.
# Brings up everything EXCEPT caddy: the TLS proxy isn't part of the submission
# pipeline (it's validated separately via `caddy validate`), and skipping it avoids
# bind-mounting the repo-path Caddyfile, which Docker Desktop denies on macOS
# (it shares /tmp, not /Users). Uses runc locally (no gVisor) + a /tmp-based throwaway
# workdir for the DooD bind mounts.
set -euo pipefail
cd "$(dirname "$0")"

# A Docker-Desktop-shared, cross-platform throwaway workdir for the DooD bind mounts.
WORK="${ARENA_WORK_DIR:-/tmp/arena-work}"
mkdir -p "$WORK"

# Build a smoke .env from the template, forcing runc + the shared workdir.
cp .env.example .env
python3 - "$WORK" <<'PY'
import re, sys, pathlib
work = sys.argv[1]
p = pathlib.Path(".env"); t = p.read_text()
t = re.sub(r"^ARENA_DOCKER_RUNTIME=.*$", "ARENA_DOCKER_RUNTIME=runc", t, flags=re.M)
t = re.sub(r"^ARENA_WORK_DIR=.*$", f"ARENA_WORK_DIR={work}", t, flags=re.M)
p.write_text(t)
PY

cleanup() { docker compose down -v >/dev/null 2>&1 || true; rm -f .env; }
trap cleanup EXIT

echo "==> build app images"
docker compose build

echo "==> up api + worker + frontend (deps postgres/redis/migrate auto-start; caddy excluded)"
docker compose up -d api worker frontend

echo "==> wait for API"
for _ in $(seq 1 60); do
  if docker compose exec -T api python -c \
     "import httpx,sys; sys.exit(0 if httpx.get('http://localhost:8000/api/presets').status_code==200 else 1)" \
     >/dev/null 2>&1; then ok=1; break; fi
  sleep 2
done
[ "${ok:-}" = 1 ] || { echo "API never came up"; docker compose logs api migrate worker; exit 1; }

echo "==> submit identity-tour python solver + poll to terminal"
docker compose exec -T api python - <<'PY'
import time, httpx
B = "http://localhost:8000"
solver = "print('TOUR ' + ' '.join(str(i) for i in range(1, 43)))"
r = httpx.post(f"{B}/api/submissions",
               json={"handle": "smoke", "preset": "python", "files": {"main.py": solver}})
r.raise_for_status()
sid = r.json()["id"]
for _ in range(120):
    s = httpx.get(f"{B}/api/submissions/{sid}").json()
    if s["status"] in ("scored", "failed"):
        break
    time.sleep(2)
assert s["status"] == "scored", f"expected scored, got {s}"
assert s["length"] == 699, f"expected 699, got {s.get('length')}"
print("SMOKE OK: scored", s["length"])
PY

echo "==> leaderboard contains the entry"
docker compose exec -T api python -c \
  "import httpx; rows=httpx.get('http://localhost:8000/api/leaderboard').json(); assert any(x['handle']=='smoke' for x in rows), rows; print('leaderboard OK')"
echo "ALL SMOKE CHECKS PASSED"
