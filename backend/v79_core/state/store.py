from __future__ import annotations
from typing import List, Dict

class InMemoryStore:
    def __init__(self):
        self.history: List[Dict] = []

    def add(self, item: Dict) -> None:
        self.history.append(item)
        if len(self.history) > 200:
            self.history = self.history[-200:]

    def recent(self, n: int = 50) -> List[Dict]:
        return self.history[-n:]

    def clear(self) -> None:
        self.history.clear()
