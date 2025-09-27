import os
from fastapi import FastAPI
from app.models import ChatRequest, ChatResponse, Msg
from app.storage import Storage
from app.deps import get_engine
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from app.utils import is_on_topic, is_unsafe, parse_topic_stance

app = FastAPI(title="Kopi Debate API", version="1.0.0")
store = Storage()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    engine = get_engine()

    if req.conversation_id is None:
        # Try to read forced topic/stance from the first message
        forced_topic, forced_stance, remainder = parse_topic_stance(req.message)

        # Optional env overrides for global forcing
        env_topic = os.getenv("FORCE_TOPIC")
        env_stance = os.getenv("FORCE_STANCE")

        if env_topic or env_stance or forced_topic or forced_stance:
            topic = env_topic or forced_topic or "General debate"
            stance = env_stance or forced_stance or "Pro"
        else:
            topic, stance = engine.pick_topic_and_stance()

        cid = store.new_conversation(topic, stance)
        bot_intro = (
            f"Topic: **{topic}**. My stance: **{stance}**. "
            "Tell me your position — I’ll make the case and stand my ground."
        )
        store.append(cid, "bot", bot_intro)

        # Use the remainder (if any) as the actual first user message
        first_user_msg = remainder or req.message
    else:
        cid = req.conversation_id
        meta = store.get_meta(cid)
        topic, stance = meta["topic"], meta["stance"]
        first_user_msg = req.message

    # Record the user's message
    store.append(cid, "user", first_user_msg)

    # ----- Guards: safety and topic discipline -----
    topic2, stance2, hist = store.get_window(cid, 5)
    assert topic2 == topic and stance2 == stance

    # 1) Safety: decline illegal/violent instructions & redirect
    if is_unsafe(first_user_msg):
        bot_msg = (
            "I can’t help with that. Let’s keep this debate on our topic: "
            f"**{topic}**. I’m defending **{stance}**. "
            "What’s your strongest counterpoint *on this topic*?"
        )
        store.append(cid, "bot", bot_msg)
        _, _, hist = store.get_window(cid, 5)
        return ChatResponse(conversation_id=cid, message=[Msg(**h) for h in hist])

    # 2) Topic guard: gently refuse off-topic and steer back
    if not is_on_topic(first_user_msg, topic):
        bot_msg = (
            f"Quick nudge: our topic is **{topic}** and my stance is **{stance}**. "
            "Let’s stick to that so we can make progress. "
            "What’s one argument *for or against* my stance?"
        )
        store.append(cid, "bot", bot_msg)
        _, _, hist = store.get_window(cid, 5)
        return ChatResponse(conversation_id=cid, message=[Msg(**h) for h in hist])

    # ----- Normal reply path with timeout + graceful fallback -----
    timeout = int(os.getenv("RESPONSE_TIMEOUT", "25"))
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(engine.reply, topic, stance, hist, first_user_msg)
            bot_msg = fut.result(timeout=timeout)
    except FuturesTimeout:
        bot_msg = (
            "I’m considering your point, but to keep momentum: my stance remains "
            f"**{stance}** on **{topic}** — give me your best counterexample."
        )
    except Exception:
        bot_msg = (
            f"(Temporary note) External engine hit an error. Staying on-topic: my stance is "
            f"**{stance}** on **{topic}** — let’s keep going."
        )

    store.append(cid, "bot", bot_msg)
    _, _, hist = store.get_window(cid, 5)
    return ChatResponse(conversation_id=cid, message=[Msg(**h) for h in hist])
