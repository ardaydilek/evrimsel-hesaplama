# TSP Solver Arena — Deploy Runbook

## What this is
Docker Compose stack: caddy (auto-HTTPS) → frontend (Next.js standalone) → api (FastAPI)
→ worker (RQ; runs each submission as a gVisor-hardened, host-sibling container via the
mounted Docker socket — Docker-out-of-Docker) + redis (RQ broker) + postgres. Alembic owns
the schema: a one-shot `migrate` service runs `alembic upgrade head` and gates api/worker.

## Prerequisites
- A Linux host (Ubuntu/Debian) with a public IP and a domain you control.
- DNS A record: `ARENA_DOMAIN` → host IP (required before Caddy can issue TLS certs).

## First deploy
1. `git clone … && cd <repo>/arena/deploy`
2. `cp .env.example .env` and set real values (the `.env.example` defaults are LOCAL-dev, not prod):
   - `POSTGRES_PASSWORD` to a real secret, and the matching password in `DATABASE_URL`.
   - `ARENA_DOCKER_RUNTIME=runsc`   (gVisor hardening — the whole point of the Linux host)
   - `ARENA_WORK_DIR=/srv/arena/work`
   - `DOCKER_GID=$(getent group docker | cut -d: -f3)`
   - `API_ORIGIN=http://api:8000`
   - `ARENA_DOMAIN=arena.example.com`, `ARENA_ACME_EMAIL=you@example.com`
3. `./provision.sh` — installs Docker + gVisor, registers `runsc`, builds the 6 toolchain +
   proxy images on the host daemon, builds app images, runs migrations, starts the stack.
   It verifies gVisor with `docker run --rm --runtime=runsc hello-world`.
   - **Brownfield host:** `provision.sh` writes `/etc/docker/daemon.json` only if it does NOT
     already exist (it never clobbers an existing one). If Docker was already installed with a
     `daemon.json`, merge the runtime in by hand and restart:
     `{"runtimes":{"runsc":{"path":"/usr/local/bin/runsc"}}}` then `sudo systemctl restart docker`.
4. Browse to `https://ARENA_DOMAIN` — Caddy obtains the cert automatically (certs persist in the
   `caddy_data` volume across restarts).

## Updating
`git pull && docker compose build && docker compose run --rm migrate && docker compose up -d`

## Operations
- Logs: `docker compose logs -f api worker`
- A stuck submission is marked `failed` by the worker safety net (never stays `running`).
- Verify gVisor is active for submissions: `docker compose exec worker docker info | grep -iA3 runtimes`
  should list `runsc`; submission containers launch with `--runtime runsc`.
- The stack auto-restarts on reboot/crash (`restart: unless-stopped`); `migrate` is one-shot
  (`restart: "no"`) so its completion gate latches.

## Non-gVisor / local (macOS) validation
On a host without gVisor (or macOS dev), set `ARENA_DOCKER_RUNTIME=runc` — this runs WITHOUT the
extra kernel isolation: fine for local validation, NOT for a public host.

Run `./smoke.sh` to validate the whole submission pipeline end-to-end locally (build → migrate →
api+worker → submit → scored 699). It deliberately excludes caddy (the TLS proxy isn't part of the
pipeline) and writes its own throwaway `.env` (runc + a `/tmp`-based `ARENA_WORK_DIR`).

**macOS Docker Desktop file-sharing caveat:** the worker bind-mounts `ARENA_WORK_DIR` and then hands
sub-paths to the host daemon for the submission containers (DooD), so `ARENA_WORK_DIR` MUST be a path
Docker Desktop shares. Docker Desktop shares `/tmp` and `/private/tmp` but, on a restricted setup, NOT
`/Users/...`. Use a `/tmp`-based workdir (the smoke does), or add your path under **Settings → Resources
→ File Sharing**. That repo-path bind-mount limitation is also why the local smoke skips caddy (its
Caddyfile bind-mounts from the repo path). On the Linux host all paths bind-mount normally.

## Security model (recap)
Only submissions are untrusted; each runs `--network none`, `--read-only`, `/work:ro`, `--cap-drop ALL`,
non-root uid 65534, resource-capped, and under `runsc` (gVisor) in prod. The worker is trusted and is the
only service with the Docker socket. Postgres/Redis are NOT published to the host — only Caddy's 80/443
are public.

## Production hardening checklist
- Run `./pin-digests.sh` and pin every base image by `@sha256` in the preset + app Dockerfiles
  (includes the `docker:27-cli` ref the backend image copies the CLI from).
- Keep `postgres` pinned within major **16** — never let an "update images" step drift it to
  `postgres:17` (it would refuse to start on a PG16 data dir). Digest-pinning avoids this.
- Rotate `POSTGRES_PASSWORD`; keep `.env` off version control (it's gitignored).
- Optional: lock down Caddy's rootfs (`read_only: true` + `tmpfs: [/tmp]`) — it only writes to its
  `/data` + `/config` volumes.

## Known follow-ups (not in M6)
- No api readiness healthcheck yet, so `frontend`/`caddy` `depends_on` waits for START, not ready (Caddy
  retries upstream + the frontend fetches client-side, so this is tolerated). A trivial `/health` route +
  a compose healthcheck would enable true readiness gating.
- Carry-forward: DB backups, metrics/log shipping, registry/CI image push, BYOI mode, multi-host scaling.
