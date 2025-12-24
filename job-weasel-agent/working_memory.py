from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryItem:
    ts: float
    kind: str
    text: str
    meta: dict[str, Any] = field(default_factory=dict)


class WorkingMemory:
    """
    Lightweight working memory designed for prompt injection.
    Keeps a small sliding window to avoid prompt bloat.
    """

    def __init__(self, max_items: int = 12):
        self.max_items = max_items
        self.items: list[MemoryItem] = []

    def add(self, kind: str, text: str, **meta: Any) -> None:
        if not text:
            return
        self.items.append(MemoryItem(ts=time.time(), kind=kind, text=text.strip(), meta=meta))
        # prune
        if len(self.items) > self.max_items:
            self.items = self.items[-self.max_items :]

    def render_for_prompt(self) -> str:
        if not self.items:
            return ""
        lines = ["<working_memory>"]
        for it in self.items[-self.max_items :]:
            lines.append(f"- ({it.kind}) {it.text}")
        lines.append("</working_memory>")
        return "\n".join(lines)

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        payload = [
            {"ts": it.ts, "kind": it.kind, "text": it.text, "meta": it.meta}
            for it in self.items
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    @staticmethod
    def load(path: str, max_items: int = 12) -> "WorkingMemory":
        wm = WorkingMemory(max_items=max_items)
        if not os.path.exists(path):
            return wm
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for row in data[-max_items:]:
                wm.items.append(
                    MemoryItem(
                        ts=float(row.get("ts", time.time())),
                        kind=str(row.get("kind", "note")),
                        text=str(row.get("text", "")),
                        meta=dict(row.get("meta", {})),
                    )
                )
        except Exception:
            # If corrupted, ignore and start fresh
            return WorkingMemory(max_items=max_items)
        return wm


