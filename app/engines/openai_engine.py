import os
from typing import List, Dict, Tuple
from .base import BaseArguer

try:
    from openai import OpenAI  # pip install openai
except Exception:  # pragma: no cover
    OpenAI = None

SYSTEM = (
    "You are a debate bot. Pick a topic and stance on start. Stay on-topic, \n"
    "stand your ground, persuasive not hostile, avoid unsafe or disallowed content. \n"
    "Keep responses under 180 words."
)

class OpenAIArguer(BaseArguer):
    def __init__(self):
        if OpenAI is None:
            raise RuntimeError("openai package not installed")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key)

    def pick_topic_and_stance(self) -> Tuple[str, str]:
        rsp = self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.7,
            max_tokens=120,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": "Propose a debate topic and your firm stance in one line: 'Topic — Stance'"},
            ],
            timeout=25,
        )
        line = rsp.choices[0].message.content.strip()
        if "—" in line:
            topic, stance = [p.strip() for p in line.split("—", 1)]
        else:
            topic, stance = line, "Pro"
        return topic, stance

    def reply(self, topic: str, stance: str, history: List[Dict], user_msg: str) -> str:
        msgs = [{"role": "system", "content": SYSTEM}]
        msgs.append({"role": "user", "content": f"Topic: {topic}\nYour stance: {stance}"})

        # 🔧 Map our internal roles to OpenAI roles
        for h in history[-10:]:
            role = "assistant" if h["role"] == "bot" else "user"
            msgs.append({"role": role, "content": h["message"]})

        msgs.append({"role": "user", "content": user_msg})

        rsp = self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.7,
            max_tokens=220,
            messages=msgs,
            timeout=25,
        )
        return rsp.choices[0].message.content.strip()
