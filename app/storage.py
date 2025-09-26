import json
import os
import time
import uuid
from typing import List, Dict

try:
    import redis  # type: ignore
except ImportError:
    redis = None

MAX_HISTORY = 100  # store more than we return so stance can be consistent

class Storage:
    def __init__(self):
        self.use_redis = False
        self.r = None
        url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        if redis is not None:
            try:
                self.r = redis.Redis.from_url(url, decode_responses=True)
                self.r.ping()
                self.use_redis = True
            except Exception:
                self.use_redis = False
        self.mem: Dict[str, Dict] = {}

    def new_conversation(self, topic: str, stance: str) -> str:
        cid = str(uuid.uuid4())
        payload = {
            "topic": topic,
            "stance": stance,
            "history": [],  # list of {role, message, ts}
            "created_at": time.time(),
        }
        self._set(cid, payload)
        return cid

    def append(self, cid: str, role: str, message: str):
        doc = self._get(cid)
        if not doc:
            raise KeyError("conversation not found")
        doc["history"].append({"role": role, "message": message, "ts": time.time()})
        # trim
        if len(doc["history"]) > MAX_HISTORY:
            doc["history"] = doc["history"][-MAX_HISTORY:]
        self._set(cid, doc)

    def get_window(self, cid: str, n: int = 5):
        doc = self._get(cid)
        if not doc:
            raise KeyError("conversation not found")
        recent = doc["history"][-(n*2):]  # roughly 5 user+bot pairs
        return doc["topic"], doc["stance"], [{"role": h["role"], "message": h["message"]} for h in recent]

    def get_meta(self, cid: str):
        doc = self._get(cid)
        if not doc:
            raise KeyError("conversation not found")
        return doc

    # internals
    def _get(self, cid: str):
        if self.use_redis:
            raw = self.r.get(f"conv:{cid}")
            return json.loads(raw) if raw else None
        return self.mem.get(cid)

    def _set(self, cid: str, payload: Dict):
        if self.use_redis:
            self.r.set(f"conv:{cid}", json.dumps(payload), ex=60*60*24*7)  # 7 days TTL
        else:
            self.mem[cid] = payload
