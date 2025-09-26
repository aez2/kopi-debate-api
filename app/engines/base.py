from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

class BaseArguer(ABC):
    @abstractmethod
    def pick_topic_and_stance(self) -> Tuple[str, str]:
        ...

    @abstractmethod
    def reply(self, topic: str, stance: str, history: List[Dict], user_msg: str) -> str:
        ...
