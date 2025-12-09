#!/bin/bash
# run_recipenow.sh - one-stop script to setup and launch RecipeNOW
# Usage:
#   chmod +x run_recipenow.sh
#   ./run_recipenow.sh           # SQLite
#   ./run_recipenow.sh mysql     # ensure Docker MySQL is running

set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -d venv ]]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "[info] Created .env. Edit it with your API keys before proceeding."
fi

python - <<'PY'
from backend.User.database import Base, engine
import backend.User.models  # ensures all models register
Base.metadata.create_all(bind=engine)
print("[info] Database tables ensured.")
PY

if [[ "${1:-}" == "mysql" ]]; then
  docker start recipenow-mysql || docker run --name recipenow-mysql \
    -e MYSQL_DATABASE=recipenow \
    -e MYSQL_USER=user \
    -e MYSQL_PASSWORD=recipenow \
    -e MYSQL_ROOT_PASSWORD=root \
    -p 3309:3306 -d mysql:8
fi

uvicorn main:app --reload &
BACKEND_PID=$!
trap 'kill $BACKEND_PID' EXIT

echo "[info] Backend running (PID $BACKEND_PID)"

echo "[info] Installing frontend dependencies"
cd frontend
npm install
if [[ ! -f .env ]]; then
  cp .env.example .env
fi
PORT=$(grep -E '^VITE_DEV_SERVER_PORT=' .env | cut -d'=' -f2)
PORT=${PORT:-3000}
echo "[info] Starting Vite on port $PORT"
npm run dev -- --port "$PORT"
