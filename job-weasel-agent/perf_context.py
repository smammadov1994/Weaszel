from __future__ import annotations

import contextvars

# Attach profiling events to a current task/step without threading globals.
current_task_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("weaszel_task_id", default=None)
current_step: contextvars.ContextVar[int | None] = contextvars.ContextVar("weaszel_step", default=None)


