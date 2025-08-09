#!/bin/sh
echo "[entrypoint] Starting app"
# If you use Alembic in production, run migrations here (uncomment in production)
# alembic upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
