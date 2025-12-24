from __future__ import annotations

import contextvars

current_goal: contextvars.ContextVar[str | None] = contextvars.ContextVar("weaszel_goal", default=None)
current_task_type: contextvars.ContextVar[str | None] = contextvars.ContextVar("weaszel_task_type", default=None)
current_last_error: contextvars.ContextVar[str | None] = contextvars.ContextVar("weaszel_last_error", default=None)
current_failure_count: contextvars.ContextVar[int] = contextvars.ContextVar("weaszel_failure_count", default=0)
current_speed_mode: contextvars.ContextVar[str | None] = contextvars.ContextVar("weaszel_speed_mode", default=None)


