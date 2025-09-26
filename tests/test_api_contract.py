from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_start_and_reply_flow():
    r = client.post("/chat", json={"conversation_id": None, "message": "Hi"})
    assert r.status_code == 200
    data = r.json()
    assert "conversation_id" in data
    cid = data["conversation_id"]
    assert isinstance(cid, str)
    assert len(data["message"]) >= 1

    r2 = client.post("/chat", json={"conversation_id": cid, "message": "I disagree"})
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["conversation_id"] == cid
    assert len(d2["message"]) >= 2
    assert d2["message"][-1]["role"] == "bot"
