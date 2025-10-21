from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Dict, List

from .utils import LOGS_DIR, MEMORY_PATH, load_json, save_json


class MemoryStore:
    def __init__(self, path: Path = MEMORY_PATH):
        self.path = path
        self.state = {
            "facts": [],
            "notes": {},
            "history": [],
        }
        self._load()

    def _load(self) -> None:
        data = load_json(self.path)
        if data:
            self.state.update(data)
        else:
            save_json(self.path, self.state)

    def add_fact(self, fact: str) -> None:
        if fact and fact not in self.state["facts"]:
            self.state["facts"].append(fact)
            self._persist()

    def remember(self, key: str, value: str) -> None:
        key = key.strip()
        value = value.strip()
        if not key or not value:
            return
        self.state["notes"][key] = value
        self._persist()

    def log_interaction(self, question: str, answer: str) -> None:
        entry = {
            "timestamp": dt.datetime.utcnow().isoformat(),
            "question": question,
            "answer": answer,
        }
        self.state["history"].append(entry)
        logs_path = LOGS_DIR / "chat.log"
        logs_path.parent.mkdir(parents=True, exist_ok=True)
        with logs_path.open("a", encoding="utf-8") as f:
            f.write(f"[{entry['timestamp']}] Q: {question}\nA: {answer}\n\n")
        self._persist()

    def recall(self) -> Dict[str, str]:
        return self.state.get("notes", {})

    def recent_history(self, limit: int = 5) -> List[Dict[str, str]]:
        return self.state.get("history", [])[-limit:]

    def _persist(self) -> None:
        save_json(self.path, self.state)


__all__ = ["MemoryStore"]
