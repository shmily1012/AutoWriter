#!/usr/bin/env bash
# Restart backend (uvicorn) and frontend (streamlit) for the novel system.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_CMD="uvicorn novel_system.backend.main:app --host 0.0.0.0 --port 8000"
FRONTEND_CMD="streamlit run ${ROOT_DIR}/frontend/app.py --server.address 0.0.0.0 --server.port 8501"

LOG_DIR="${ROOT_DIR}/novel_system/docker-data/logs"
mkdir -p "${LOG_DIR}"

stop_app() {
  local pattern="$1"
  pkill -f "${pattern}" >/dev/null 2>&1 || true
}

start_backend() {
  echo "Starting backend..."
  nohup ${BACKEND_CMD} >"${LOG_DIR}/backend.log" 2>&1 &
}

start_frontend() {
  echo "Starting frontend..."
  nohup ${FRONTEND_CMD} >"${LOG_DIR}/frontend.log" 2>&1 &
}

echo "Stopping existing backend/frontend..."
stop_app "uvicorn novel_system.backend.main:app"
stop_app "streamlit run ${ROOT_DIR}/frontend/app.py"

start_backend
start_frontend

echo "Done. Logs: ${LOG_DIR}/backend.log , ${LOG_DIR}/frontend.log"
