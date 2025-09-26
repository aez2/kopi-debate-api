from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_history_window_limit():
    r = client.post("/chat", json={"conversation_id": None, "message": "hello"})
    cid = r.json()["conversation_id"]
    for i in range(12):
        client.post("/chat", json={"conversation_id": cid, "message": f"msg {i}"})
    r2 = client.post("/chat", json={"conversation_id": cid, "message": "final"})
    hist = r2.json()["message"]
    assert len(hist) <= 10
    assert hist[-1]["role"] == "bot"
