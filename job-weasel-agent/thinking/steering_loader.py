from __future__ import annotations

import glob
import os
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SteeringDoc:
    path: str
    content: str


class SteeringLoader:
    """
    Loads steering docs from repo root and produces a compact set of principles.

    Sources:
    - STEERING*.md at repo root
    """

    def __init__(self, repo_root: str | None = None):
        self.repo_root = repo_root or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    def load(self) -> list[SteeringDoc]:
        pattern = os.path.join(self.repo_root, "STEERING*.md")
        docs: list[SteeringDoc] = []
        for path in sorted(glob.glob(pattern)):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    docs.append(SteeringDoc(path=os.path.abspath(path), content=f.read()))
            except FileNotFoundError:
                continue
        return docs

    def extract_principles(self, docs: list[SteeringDoc], max_chars: int = 1500) -> str:
        """
        Heuristic extraction:
        - Keep headings and bullet points (pseudo-rules)
        - Remove code blocks to keep prompt small
        """
        chunks: list[str] = []
        for d in docs:
            text = d.content
            # Drop fenced code blocks (keep speed)
            text = re.sub(r"```[\s\S]*?```", "", text)
            lines = []
            for line in text.splitlines():
                l = line.rstrip()
                if not l:
                    continue
                if l.startswith("###") or l.startswith("##"):
                    lines.append(l)
                elif l.lstrip().startswith("- "):
                    lines.append(l.strip())
            if lines:
                chunks.append(f"[{os.path.basename(d.path)}]\n" + "\n".join(lines))

        out = "\n\n".join(chunks).strip()
        if len(out) > max_chars:
            out = out[:max_chars].rstrip() + "\n…(truncated)…"
        return out


