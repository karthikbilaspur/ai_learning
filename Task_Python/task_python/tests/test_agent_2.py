
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_list_tools_unauthorized():
    r = client.get("/api/agent/tools")
    assert r.status_code == 401

def test_tool_registry():
    from src.agent.core import TOOL_REGISTRY
    assert "reddit_analysis" in TOOL_REGISTRY
    assert "tower_defense" in TOOL_REGISTRY
    assert len(TOOL_REGISTRY) == 9
