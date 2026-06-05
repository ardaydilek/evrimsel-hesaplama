#!/usr/bin/env bash
# Resolve current @sha256 digests for every base image, for production pinning.
# Prints `image:tag  ->  image@sha256:...` lines; copy the digests into the
# preset/app Dockerfiles to pin them. (Tag-based builds remain the dev default.)
set -euo pipefail

IMAGES=(
  "ubuntu/squid:latest"
  "python:3.12-slim"
  "gcc:13"
  "golang:1.22"
  "rust:1.78"
  "node:20"
  "maven:3.9-eclipse-temurin-21"
  "caddy:2"
  "postgres:16"
  "redis:7"
  "node:20-alpine"
  "docker:27-cli"
)

for img in "${IMAGES[@]}"; do
  docker pull -q "$img" >/dev/null
  digest="$(docker inspect --format '{{index .RepoDigests 0}}' "$img")"
  printf '%-36s -> %s\n' "$img" "$digest"
done
