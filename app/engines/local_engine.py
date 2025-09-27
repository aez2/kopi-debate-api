import random
from typing import List, Dict
from .base import BaseArguer

TOPICS = [
    ("Pineapple on pizza", "Pro"),
    ("Remote work vs office", "Remote work is superior"),
    ("Tabs vs spaces", "Tabs are objectively better"),
    ("Cats vs dogs", "Cats are superior companions"),
    ("The Earth is flat", "The Earth is flat"),
]

TACTICS = [
    "Use a concrete example",
    "Find common ground then pivot",
    "Ask a leading question",
    "Cite a (plausible) study or expert",
    "Reframe the metric of success",
    "Address counterargument succinctly",
]

OPENERS = [
    "Let’s ground this in what matters most.",
    "Let me challenge a common assumption.",
    "Here’s the simple core of it.",
    "Consider a practical test.",
]

CLOSERS = [
    "What would change your mind if not this?",
    "Notice how this holds across examples.",
    "If we care about outcomes, this follows.",
    "Happy to examine any counterexample you have.",
]

class LocalArguer(BaseArguer):
    def pick_topic_and_stance(self):
        return random.choice(TOPICS)

    def reply(self, topic: str, stance: str, history: List[Dict], user_msg: str) -> str:
        opener = random.choice(OPENERS)
        tactic = random.choice(TACTICS)
        closer = random.choice(CLOSERS)

        last_user = next((h["message"] for h in reversed(history) if h["role"] == "user"), "")
        hook = f"You mentioned: ‘{last_user[:120]}’ — let’s address that directly. " if last_user else ""

        body = (
            f"{opener} On **{topic}**, my view is **{stance}**. "
            f"{hook}{tactic}. In short: "
            f"1) define the goal clearly, 2) compare evidence on that goal, 3) prefer what consistently wins. "
            f"On that basis, **{stance}** wins. {closer}"
        )
        body += " To stay focused, let’s keep arguments tied to this topic and stance."
        return body
