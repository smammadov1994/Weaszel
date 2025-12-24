from __future__ import annotations

import os
from typing import Any

from browser_use.llm.messages import SystemMessage

from perf_context import current_step, current_task_id
from perf_logger import emit, span
from thinking.thinking_engine import ThinkingEngine
from thinking.working_memory import WorkingMemory


class ThinkingLLM:
    """
    Injects a "thinking layer" into each LLM call without adding overhead by default.

    - Always runs quick_think() (rule-based).
    - Optionally runs deep_think() (LLM) when WEASZEL_DEEP_THINK triggers.
    - Injects steering principles + working memory + thinking output as a SystemMessage.
    """

    def __init__(self, llm: Any, engine: ThinkingEngine, memory: WorkingMemory):
        self._llm = llm
        self.engine = engine
        self.memory = memory

    def __getattr__(self, item: str) -> Any:
        return getattr(self._llm, item)

    async def ainvoke(self, messages: list[Any], *args: Any, **kwargs: Any) -> Any:
        if os.environ.get("WEASZEL_THINKING", "1").lower() in ("0", "false", "off", "no"):
            return await self._llm.ainvoke(messages, *args, **kwargs)

        # Best-effort extract a task string from the latest user message
        task = ""
        try:
            for m in reversed(messages):
                if getattr(m, "role", None) == "user":
                    task = m.content if isinstance(m.content, str) else str(m.content)
                    break
        except Exception:
            task = ""

        ctx = self.engine.build_context(task=task)
        quick = self.engine.quick_think(ctx)

        injected_parts = [
            "<weaszel_thinking>",
            f"task_id={current_task_id.get()} step={current_step.get()}",
            f"quick_think={quick}",
        ]
        if ctx.memory:
            injected_parts.append(f"<working_memory>\n{ctx.memory}\n</working_memory>")
        if ctx.steering:
            injected_parts.append(f"<steering_principles>\n{ctx.steering}\n</steering_principles>")
        injected_parts.append(
            "RULES: Think before acting. Consider at least 2 options, pick safest+fastest, avoid repeating failed actions. "
            "Batch simple actions, and add fallback strategies if blocked."
        )
        injected_parts.append("</weaszel_thinking>")

        # Optional deep-think (only on anomalies/risk)
        if self.engine.should_deep_think(task):
            with span("thinking.deep", task_id=current_task_id.get(), step=current_step.get()):
                deep = await self.engine.deep_think(ctx)
            injected_parts.append(f"<deep_think>{deep.model_dump()}</deep_think>")

        sys_msg = SystemMessage(content="\n".join(injected_parts), cache=True)

        # Place injected system message before the rest so it conditions the step
        new_messages = [sys_msg, *messages]
        emit("thinking.injected", task_id=current_task_id.get(), step=current_step.get(), deep=self.engine.should_deep_think(task))
        return await self._llm.ainvoke(new_messages, *args, **kwargs)


