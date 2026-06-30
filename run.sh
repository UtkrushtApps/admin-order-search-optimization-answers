#!/usr/bin/env bash
set -Eeuo pipefail

cd /root/task

log() {
  printf '[run.sh] %s\n' "$1"
}

log "Starting FastAPI and PostgreSQL services"
docker compose up -d --build

log "Waiting for PostgreSQL readiness"
for attempt in $(seq 1 60); do
  if docker compose exec -T postgres pg_isready -U postgres -d orders_db >/dev/null 2>&1; then
    log "PostgreSQL is ready"
    break
  fi
  if [ "$attempt" -eq 60 ]; then
    log "PostgreSQL did not become ready in time"
    docker compose logs postgres
    exit 1
  fi
  sleep 2
done

log "Waiting for FastAPI readiness"
for attempt in $(seq 1 60); do
  if python - <<'PY' >/dev/null 2>&1
import urllib.request
with urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2) as response:
    raise SystemExit(0 if response.status == 200 else 1)
PY
  then
    log "FastAPI is ready"
    break
  fi
  if [ "$attempt" -eq 60 ]; then
    log "FastAPI did not become ready in time"
    docker compose logs api
    exit 1
  fi
  sleep 2
done

log "Running baseline smoke check for target endpoint"
python - <<'PY'
import json
import time
import urllib.parse
import urllib.request

params = urllib.parse.urlencode({"status": "paid", "from": "2026-01-01", "limit": 100, "offset": 0})
url = f"http://127.0.0.1:8000/api/orders?{params}"
started = time.perf_counter()
with urllib.request.urlopen(url, timeout=30) as response:
    body = response.read()
    elapsed_ms = (time.perf_counter() - started) * 1000
    payload = json.loads(body)
    statements = response.headers.get("X-SQL-Statements", "not-reported")
print(f"baseline_status=ok rows={len(payload)} elapsed_ms={elapsed_ms:.1f} sql_statements={statements}")
if len(payload) != 100:
    raise SystemExit("Expected smoke check to return 100 rows")
PY

log "Project is ready under /root/task"
