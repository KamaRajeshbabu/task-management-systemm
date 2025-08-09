# tests/test_api_flow.py
import os
import pytest
from httpx import AsyncClient

# Ensure test DB and minimal env before importing app
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_task_management.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SECRET_KEY", "testing-secret-key")

from app.main import app  # import after env is set

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json().get("status") == "healthy"

@pytest.mark.asyncio
async def test_e2e_register_project_task_flow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {"email": "e2e@example.com", "password": "e2e-pass"}
        rg = await client.post("/auth/register", json=payload)
        assert rg.status_code in (200, 201)
        # now login using form fields (login endpoint expects form)
        login = await client.post("/auth/login", data=payload)
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        p = await client.post("/projects/", json={"name":"E2E Project"}, headers=headers)
        assert p.status_code == 201
        pid = p.json()["id"]

        t = await client.post("/tasks/", json={"title":"E2E Task","project_id":pid}, headers=headers)
        assert t.status_code == 201
        tid = t.json()["id"]

        upd = await client.patch(f"/tasks/{tid}", json={"status":"in_progress"}, headers=headers)
        assert upd.status_code == 200
        assert upd.json()["status"] == "in_progress"
