import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.models import ChatRequest, ChatResponse, Msg
from app.storage import Storage
from app.deps import get_engine
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

app = FastAPI(title="Kopi Debate API", version="1.0.0")
store = Storage()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    engine = get_engine()

    if req.conversation_id is None:
        topic, stance = engine.pick_topic_and_stance()
        cid = store.new_conversation(topic, stance)
        bot_intro = (
            f"Topic: **{topic}**. My stance: **{stance}**. "
            f"Tell me your position — I’ll make the case and stand my ground."
        )
        store.append(cid, "bot", bot_intro)
    else:
        cid = req.conversation_id
        meta = store.get_meta(cid)
        topic, stance = meta["topic"], meta["stance"]

    store.append(cid, "user", req.message)
        
    timeout = int(os.getenv("RESPONSE_TIMEOUT", "25"))
    topic2, stance2, hist = store.get_window(cid, 5)
    assert topic2 == topic and stance2 == stance
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(engine.reply, topic, stance, hist, req.message)
            bot_msg = fut.result(timeout=timeout)
    except FuturesTimeout:
        bot_msg = (
            "I’m still considering your point, but to keep things crisp: my stance remains "
            f"**{stance}** on **{topic}** — happy to continue."
        )
    except Exception:
        # e.g., OpenAI quota errors (429), network hiccups, etc.
        bot_msg = (
            f"(Temporary note) External engine hit an error. Staying on-topic: my stance is "
            f"**{stance}** on **{topic}** — let’s keep going."
        )
    store.append(cid, "bot", bot_msg)

    _, _, hist = store.get_window(cid, 5)
    return ChatResponse(conversation_id=cid, message=[Msg(**h) for h in hist])
