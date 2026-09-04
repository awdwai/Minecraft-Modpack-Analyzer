"""API smoke tests."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from fixtures.build_fixtures import build

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "modpacks"


@pytest.fixture(scope="session", autouse=True)
def _fixtures():
    build()


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_analyze_and_mods(client):
    r = client.post("/api/analyze", json={"path": str(FIXTURES / "mini_forge")})
    assert r.status_code == 200
    data = r.json()
    assert data["summary"]["jar_count"] == 2
    aid = data["analysis_id"]

    mods = client.get("/api/mods", params={"analysis_id": aid})
    assert mods.status_code == 200
    assert mods.json()["count"] >= 2

    deps = client.get("/api/dependencies", params={"analysis_id": aid})
    assert deps.status_code == 200
    assert "graph" in deps.json()


def test_analyze_rejects_relative(client):
    r = client.post("/api/analyze", json={"path": "relative/path"})
    assert r.status_code == 400


def test_stub_compare(client):
    r = client.post("/api/compare", json={"path_a": "C:/a", "path_b": "C:/b"})
    assert r.status_code == 200
    assert r.json()["implemented"] is False
