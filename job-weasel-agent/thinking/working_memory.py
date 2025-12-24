from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class MemoryItem:
    ts: float
    kind: str  # e.g. "reflection", "pattern", "warning"
    data: dict[str, Any]


class WorkingMemory:
    """
    Small persistent memory intended for *prompt injection* (short, pruned).
    Stored as JSON for debuggability.
    """

    def __init__(self, path: str | None = None, max_items: int = 50):
        self.path = path or os.path.abspath("logs/working_memory.json")
        self.max_items = max_items
        self._items: list[MemoryItem] = []
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            items = []
            for x in raw.get("items", []):
                items.append(MemoryItem(ts=float(x["ts"]), kind=str(x["kind"]), data=dict(x["data"])))
            self._items = items[-self.max_items :]
        except FileNotFoundError:
            self._items = []
        except Exception:
            # If corrupted, start fresh; do not break the agent.
            self._items = []

    def _persist(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        data = {"items": [{"ts": i.ts, "kind": i.kind, "data": i.data} for i in self._items[-self.max_items :]]}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add(self, kind: str, **data: Any) -> None:
        self.load()
        self._items.append(MemoryItem(ts=time.time(), kind=kind, data=data))
        self._items = self._items[-self.max_items :]
        self._persist()

    def to_prompt(self, max_chars: int = 800) -> str:
        self.load()
        if not self._items:
            return ""
        # Keep only recent items, render compactly.
        lines = []
        for item in self._items[-15:]:
            t = time.strftime("%H:%M:%S", time.localtime(item.ts))
            lines.append(f"- [{t}] {item.kind}: {item.data}")
        out = "\n".join(lines)
        if len(out) > max_chars:
            out = out[-max_chars:]
        return out


