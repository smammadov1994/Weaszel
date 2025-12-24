import json
import os
import time
from dataclasses import dataclass
from typing import Any, Optional


def _enabled() -> bool:
    return os.environ.get("WEASZEL_PROFILE", "0").lower() in ("1", "true", "yes", "on")


def _log_path() -> str:
    return os.path.abspath(os.environ.get("WEASZEL_PROFILE_PATH", "logs/perf.jsonl"))


def emit(event: str, **fields: Any) -> None:
    """
    Emit a single profiling event to logs/perf.jsonl (JSON lines).
    Safe to call when profiling is disabled (no-op).
    """
    if not _enabled():
        return
    path = _log_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {
        "ts": time.time(),
        "event": event,
        **fields,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


@dataclass
class Span:
    """
    Simple timing span that logs start/end and duration_ms.
    """

    name: str
    fields: dict[str, Any]
    _t0: float | None = None

    def __enter__(self):
        if _enabled():
            self._t0 = time.perf_counter()
            emit("span_start", name=self.name, **self.fields)
        return self

    def __exit__(self, exc_type, exc, tb):
        if not _enabled():
            return False
        t1 = time.perf_counter()
        duration_ms = (t1 - (self._t0 or t1)) * 1000.0
        emit(
            "span_end",
            name=self.name,
            duration_ms=duration_ms,
            ok=exc_type is None,
            error_type=getattr(exc_type, "__name__", None),
            error=str(exc) if exc else None,
            **self.fields,
        )
        return False


def span(name: str, **fields: Any) -> Span:
    return Span(name=name, fields=fields)


