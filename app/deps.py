import os
from .engines.local_engine import LocalArguer
from .engines.openai_engine import OpenAIArguer

_engine = None

def get_engine():
    global _engine
    if _engine:
        return _engine
    backend = os.getenv("ENGINE_BACKEND", "local").lower()
    if backend == "openai":
        _engine = OpenAIArguer()
    else:
        _engine = LocalArguer()
    return _engine
