#!/usr/bin/env bash
# Spin up local Postgres and Redis (Redis Stack for RediSearch) via Docker.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required but not found on PATH." >&2
  exit 1
fi

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${ROOT_DIR}/.env"
  set +a
fi

PG_CONTAINER="${PG_CONTAINER:-novel-system-pg}"
REDIS_CONTAINER="${REDIS_CONTAINER:-novel-system-redis}"

PG_PORT="${PG_PORT:-5432}"
REDIS_PORT="${REDIS_PORT:-6379}"

POSTGRES_USER="${POSTGRES_USER:-user}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-password}"
POSTGRES_DB="${POSTGRES_DB:-novel_db}"

PG_DATA="${PG_DATA:-${ROOT_DIR}/novel_system/docker-data/postgres}"
REDIS_DATA="${REDIS_DATA:-${ROOT_DIR}/novel_system/docker-data/redis}"

REDIS_IMAGE="${REDIS_IMAGE:-redis/redis-stack-server:latest}"

mkdir -p "${PG_DATA}" "${REDIS_DATA}"

start_postgres() {
  docker rm -f "${PG_CONTAINER}" >/dev/null 2>&1 || true
  docker run -d \
    --name "${PG_CONTAINER}" \
    -e POSTGRES_USER="${POSTGRES_USER}" \
    -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
    -e POSTGRES_DB="${POSTGRES_DB}" \
    -p "${PG_PORT}:5432" \
    -v "${PG_DATA}:/var/lib/postgresql/data" \
    postgres:16-alpine
}

start_redis() {
  docker rm -f "${REDIS_CONTAINER}" >/dev/null 2>&1 || true
  docker run -d \
    --name "${REDIS_CONTAINER}" \
    -p "${REDIS_PORT}:6379" \
    -v "${REDIS_DATA}:/data" \
    "${REDIS_IMAGE}"
}

start_postgres
start_redis

echo "Postgres running: postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${PG_PORT}/${POSTGRES_DB}"
echo "Redis running: redis://localhost:${REDIS_PORT}/0"
echo "Containers: ${PG_CONTAINER}, ${REDIS_CONTAINER}"
