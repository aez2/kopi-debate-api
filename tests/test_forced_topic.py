import os
from fastapi.testclient import TestClient
from app.main import app

def test_forced_topic_stance_inline(monkeypatch):
    client = TestClient(app)
    body = {
        "conversation_id": None,
        "message": "topic: Tabs vs spaces\nstance: Tabs are objectively better\nhello"
    }
    r = client.post("/chat", json=body)
    assert r.status_code == 200
    data = r.json()
    text = " ".join(m["message"] for m in data["message"]).lower()
    assert "tabs" in text and "objectively better" in text
