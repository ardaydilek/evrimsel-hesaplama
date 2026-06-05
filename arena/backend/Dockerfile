# syntax=docker/dockerfile:1

# --- builder: install arena_core + prod deps into a venv ---
FROM python:3.12-slim AS builder
WORKDIR /src
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY pyproject.toml ./
COPY arena_core ./arena_core
RUN pip install --no-cache-dir '.[prod]'

# --- runner: venv + alembic project files + the docker CLI client ---
FROM python:3.12-slim AS runner
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1
# Docker CLI client only (no daemon): the worker shells out to it against the
# bind-mounted host socket. api/migrate carry it unused.
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=builder /opt/venv /opt/venv
WORKDIR /app
COPY alembic.ini ./
COPY alembic ./alembic
# Non-root; the worker is granted socket access via compose `group_add`.
RUN useradd --create-home --uid 10001 arena
USER arena
# Default command is overridden per service (api / worker / migrate) in compose.
CMD ["uvicorn", "arena_core.server:build_prod_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
