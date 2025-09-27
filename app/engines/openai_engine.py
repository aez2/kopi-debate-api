import os, json
from typing import List, Dict, Tuple
from .base import BaseArguer

try:
    from openai import OpenAI  # pip install openai
except Exception:  # pragma: no cover
    OpenAI = None

SYSTEM = (
    "You are a debate bot running inside a product test.\n"
    "- Stay strictly on the originally declared topic and stance for the whole conversation.\n"
    "- Never change sides; do not concede the core stance. You may acknowledge uncertainty but must defend the stance.\n"
    "- If the user introduces post-cutoff claims or unverifiable data, ask for sources and maintain the stance.\n"
    "- Be persuasive but not hostile; concise (<180 words).\n"
    "- Safety: decline instructions that promote violence, illegal hard-drug use, or real-world harm. Redirect back to topic.\n"
    "- If the user goes off-topic, briefly redirect them back to the declared topic and request an on-topic point."
)

class OpenAIArguer(BaseArguer):
    def __init__(self):
        if OpenAI is None:
            raise RuntimeError("openai package not installed")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        # Optional: wire org/project if you use them
        self.client = OpenAI(
            api_key=api_key,
            organization=os.getenv("OPENAI_ORG_ID"),
            project=os.getenv("OPENAI_PROJECT"),
        )

    def pick_topic_and_stance(self) -> Tuple[str, str]:
        # Ask for strict JSON to avoid "Topic: **Topic**" artifacts
        rsp = self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.5,
            max_tokens=120,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": 'Return ONLY compact JSON: {"topic":"...","stance":"..."} for a debate you will firmly defend.'},
            ],
            timeout=25,
        )
        text = rsp.choices[0].message.content.strip()
        try:
            obj = json.loads(text)
            topic = (obj.get("topic") or "").strip()
            stance = (obj.get("stance") or "").strip()
            if not topic or not stance:
                raise ValueError("missing fields")
        except Exception:
            # Fallback if JSON parse fails
            if "—" in text:
                topic, stance = [p.strip() for p in text.split("—", 1)]
            else:
                topic, stance = "Remote work vs office", "Remote work is superior"
        return topic, stance

    def reply(self, topic: str, stance: str, history: List[Dict], user_msg: str) -> str:
        msgs = [{"role": "system", "content": SYSTEM}]
        # Remind the model every turn
        msgs.append({"role": "user", "content": f"Debate topic: {topic}\nYour stance (never change it): {stance}."})

        # Map internal roles to OpenAI roles
        for h in history[-10:]:
            role = "assistant" if h["role"] == "bot" else "user"
            msgs.append({"role": role, "content": h["message"]})

        msgs.append({"role": "user", "content": user_msg})

        rsp = self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.6,
            max_tokens=220,
            messages=msgs,
            timeout=25,
        )
        return rsp.choices[0].message.content.strip()
