import re
from difflib import SequenceMatcher

# --- safety regex ------------------------------------------------------------
_UNSAFE = re.compile(
    r"\b("
    r"kill|murder|genocide|assassinate|exterminate|eliminate\s+50%|mass\s+harm|"
    r"bomb|build\s+a\s+bomb|explosive|weapon(?:ize|\s*build)|"
    r"cocaine|heroin|methamphetamine|make\s+drugs|deal\s+drugs"
    r")\b",
    re.IGNORECASE,
)

# --- helpers -----------------------------------------------------------------
_WORDS_RE = re.compile(r"[a-z]{3,}")
_TOPIC_RE = re.compile(r"^\s*topic\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
_STANCE_RE = re.compile(r"^\s*stance\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
_LINE_DIRECTIVE_RE = re.compile(r"^\s*(topic|stance)\s*:", re.IGNORECASE | re.MULTILINE)

def extract_keywords(text: str) -> set[str]:
    # crude but effective: 3+ letter words
    return set(_WORDS_RE.findall(text.lower()))

def is_on_topic(user_msg: str, topic: str, threshold: float = 0.32) -> bool:
    """Return True if user_msg is plausibly about topic."""
    if not topic:
        return True
    msg_kw, topic_kw = extract_keywords(user_msg), extract_keywords(topic)
    if msg_kw & topic_kw:  # any keyword overlap
        return True
    sim = SequenceMatcher(None, user_msg.lower(), topic.lower()).quick_ratio()
    return sim >= threshold

def is_unsafe(user_msg: str) -> bool:
    return bool(_UNSAFE.search(user_msg))

def parse_topic_stance(msg: str) -> tuple[str | None, str | None, str]:
    """
    Parse optional 'topic:' and 'stance:' directives from the first message.
    Returns (topic, stance, remainder_message) where topic/stance may be None.
    """
    topic = None
    stance = None

    m_topic = _TOPIC_RE.search(msg)
    if m_topic:
        topic = m_topic.group(1).strip()

    m_stance = _STANCE_RE.search(msg)
    if m_stance:
        stance = m_stance.group(1).strip()

    # Remove any directive lines from what we store as the user's message
    remainder_lines: list[str] = []
    for line in msg.splitlines():
        if _LINE_DIRECTIVE_RE.match(line):
            continue
        remainder_lines.append(line)
    remainder = "\n".join(remainder_lines).strip()

    return topic, stance, remainder
