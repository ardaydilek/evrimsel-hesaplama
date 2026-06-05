#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
docker build -t arena/proxy:1 proxy
for p in python cpp go rust node java; do
  docker build -t "arena/$p:1" "presets/$p"
done
echo "built: arena/proxy:1 and arena/{python,cpp,go,rust,node,java}:1"
